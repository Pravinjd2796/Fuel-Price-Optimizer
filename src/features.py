# src/features.py
"""
Functions to convert a baseline (today) row and candidate price to a feature vector
expected by the demand model.
"""
import pandas as pd
import numpy as np

def compute_features_for_candidate(base_row: pd.Series, candidate_price: float) -> pd.Series:
    """
    Given the base features (one-row Series) and a candidate_price, return a Series
    containing model features for that candidate.
    """
    r = base_row.copy()
    # ensure float types
    r['price'] = float(candidate_price)
    # competitor aggregates might be present
    comp_mean = r.get('comp_mean', np.nan)
    r['price_diff'] = r['price'] - (comp_mean if not pd.isna(comp_mean) else 0.0)
    r['price_gap_pct'] = (r['price'] - (comp_mean if not pd.isna(comp_mean) else 0.0)) / ((comp_mean if not pd.isna(comp_mean) else 1.0))
    if 'cost' in r and not pd.isna(r['cost']):
        r['margin'] = r['price'] - r['cost']
        r['margin_pct'] = r['margin'] / r['price'] if r['price'] != 0 else 0.0
    else:
        r['margin'] = np.nan
        r['margin_pct'] = np.nan
    # keep only numeric/predictable columns; the model script will select feature_cols
    return r

def features_dataframe_from_candidate(base_df: pd.DataFrame, candidate_prices: list) -> pd.DataFrame:
    """
    Produce a DataFrame where each row corresponds to a candidate price features.
    base_df is expected to be a one-row DataFrame returned from prepare_day_input.
    """
    rows = []
    base = base_df.iloc[0]
    for p in candidate_prices:
        rows.append(compute_features_for_candidate(base, p))
    feat_df = pd.DataFrame(rows).reset_index(drop=True)
    return feat_df
