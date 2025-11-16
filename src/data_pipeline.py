# src/data_pipeline.py
"""
Ingestion, validation, cleaning, and feature computation functions.
Assumes CSV has columns: date, price, cost, volume, comp1, comp2, comp3
Adapt as needed for different column names.
"""
import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Dict

def read_history(path: str) -> pd.DataFrame:
    """Read CSV and parse dates. Return sorted DataFrame."""
    df = pd.read_csv(path, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)
    return df

def validate(df: pd.DataFrame) -> Dict:
    """Return diagnostics dict about missing values and ranges."""
    diag = {}
    diag['n_rows'] = len(df)
    diag['missing'] = df.isnull().sum().to_dict()
    if 'price' in df.columns:
        diag['price_min'] = float(df['price'].min())
        diag['price_max'] = float(df['price'].max())
    if 'volume' in df.columns:
        diag['volume_min'] = float(df['volume'].min())
        diag['volume_max'] = float(df['volume'].max())
    return diag

def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning: drop duplicates, fill small gaps, ensure date dtype."""
    df = df.copy()
    df = df.drop_duplicates()
    df['date'] = pd.to_datetime(df['date'])
    # Forward-fill numeric gaps then backfill
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols:
        df[num_cols] = df[num_cols].ffill().bfill()
    return df.sort_values('date').reset_index(drop=True)

def compute_base_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute rolling and lag features. Returns DataFrame ready for modeling.
    Uses shifting so no lookahead.
    """
    df = df.copy().sort_values('date').reset_index(drop=True)

    # competitor summary
    comp_cols = [c for c in df.columns if c.lower().startswith('comp')]
    if comp_cols:
        df['comp_mean'] = df[comp_cols].mean(axis=1)
        df['comp_min'] = df[comp_cols].min(axis=1)
        df['comp_max'] = df[comp_cols].max(axis=1)
    else:
        df['comp_mean'] = np.nan
        df['comp_min'] = np.nan
        df['comp_max'] = np.nan

    # price gap features
    df['price_diff'] = df['price'] - df['comp_mean']
    df['price_gap_pct'] = (df['price'] - df['comp_mean']) / df['comp_mean'].replace(0, np.nan)

    # rolling stats for volume and price (shifted to avoid lookahead)
    df['vol_ma7'] = df['volume'].rolling(7, min_periods=1).mean().shift(1)
    df['vol_ma30'] = df['volume'].rolling(30, min_periods=1).mean().shift(1)
    df['price_ma7'] = df['price'].rolling(7, min_periods=1).mean().shift(1)

    # lags
    df['vol_lag1'] = df['volume'].shift(1)
    df['vol_lag7'] = df['volume'].shift(7)
    df['price_lag1'] = df['price'].shift(1)

    # margin
    if 'cost' in df.columns:
        df['margin'] = df['price'] - df['cost']
        df['margin_pct'] = df['margin'] / df['price'].replace(0, np.nan)
    else:
        df['margin'] = np.nan
        df['margin_pct'] = np.nan

    # calendar
    df['dayofweek'] = df['date'].dt.dayofweek
    df['is_weekend'] = df['dayofweek'].isin([5,6]).astype(int)
    df['month'] = df['date'].dt.month

    # drop early rows where lag features are NaN (you can relax as needed)
    df = df.dropna(subset=['vol_lag1', 'vol_ma7']).reset_index(drop=True)
    return df

def prepare_day_input(today_json: dict, historical_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a single-row DataFrame for today's baseline features using historical data only.

    today_json: dict with possible keys:
      - date (YYYY-MM-DD), cost, comp1, comp2, comp3, last_price (optional)
    historical_df: processed historical dataframe (original or computed features OK)
    """
    hist = historical_df.copy().sort_values('date').reset_index(drop=True)
    if hist.empty:
        raise ValueError("historical_df is empty. Provide prior history.")
    last_row = hist.iloc[-1]

    d = {}
    # date
    d['date'] = pd.to_datetime(today_json.get('date', pd.Timestamp.today()))
    # cost
    d['cost'] = today_json.get('cost', last_row.get('cost', np.nan))
    # competitor raw values (if present in today_json)
    comp_keys = [k for k in today_json.keys() if k.lower().startswith('comp')]
    comp_vals = []
    for k in comp_keys:
        comp_vals.append(float(today_json[k]))
        d[k] = float(today_json[k])
    # fallback from history
    if not comp_vals:
        # use last known competitor summary if available
        if 'comp_mean' in last_row:
            d['comp_mean'] = last_row['comp_mean']
            d['comp_min'] = last_row['comp_min']
            d['comp_max'] = last_row['comp_max']
        else:
            d['comp_mean'] = np.nan
            d['comp_min'] = np.nan
            d['comp_max'] = np.nan
    else:
        d['comp_mean'] = float(np.mean(comp_vals))
        d['comp_min'] = float(np.min(comp_vals))
        d['comp_max'] = float(np.max(comp_vals))

    # last price
    d['last_price'] = float(today_json.get('last_price', last_row.get('price')))

    # rolling and lag features computed from historical_df
    d['vol_ma7'] = float(hist['volume'].rolling(7, min_periods=1).mean().iloc[-1])
    d['vol_ma30'] = float(hist['volume'].rolling(30, min_periods=1).mean().iloc[-1])
    d['price_ma7'] = float(hist['price'].rolling(7, min_periods=1).mean().iloc[-1])
    d['vol_lag1'] = float(hist['volume'].iloc[-1])
    d['vol_lag7'] = float(hist['volume'].iloc[-7]) if len(hist) >= 7 else float(hist['volume'].iloc[-1])
    d['price_lag1'] = float(hist['price'].iloc[-1])

    d['dayofweek'] = int(d['date'].dayofweek)
    d['is_weekend'] = int(d['dayofweek'] in [5,6])
    d['month'] = int(d['date'].month)

    # price-dependent fields (price, margin) will be generated per candidate price by features.py
    return pd.DataFrame([d])

def save_processed(df: pd.DataFrame, path: str):
    """Save processed DataFrame (parquet)."""
    df.to_parquet(path, index=False)
