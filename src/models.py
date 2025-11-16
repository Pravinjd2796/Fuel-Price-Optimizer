# src/models.py
"""
Train/save/load demand model and helpers.
Model saved as models/demand_model.joblib with structure {'model': model, 'feature_cols': feature_cols}
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from typing import Tuple, List

# Use absolute path based on project root
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = str(PROJECT_ROOT / "models" / "demand_model.joblib")

def default_feature_columns(df: pd.DataFrame) -> List[str]:
    """
    Suggest default feature columns from the df. Modify if necessary.
    """
    candidate_cols = [
        'price', 'price_diff', 'comp_mean', 'comp_max', 'comp_min',
        'vol_ma7', 'vol_ma30', 'vol_lag1', 'vol_lag7',
        'price_ma7', 'price_lag1', 'dayofweek', 'is_weekend', 'month',
        'margin', 'margin_pct'
    ]
    # keep only those present in df
    return [c for c in candidate_cols if c in df.columns]

def train_demand_model(train_df: pd.DataFrame,
                       feature_cols: list = None,
                       target_col: str = 'volume',
                       save_path: str = MODEL_PATH,
                       params: dict = None) -> Tuple[XGBRegressor, List[str]]:
    """
    Train an XGBoost regressor on train_df and save model + feature_cols metadata.
    Returns (model, feature_cols).
    """
    df = train_df.copy()
    if feature_cols is None:
        feature_cols = default_feature_columns(df)
    X = df[feature_cols].astype(float).values
    y = df[target_col].astype(float).values

    params = params or {'n_estimators': 300, 'max_depth': 6, 'learning_rate': 0.05, 'verbosity': 0}
    model = XGBRegressor(objective='reg:squarederror', **params)
    model.fit(X, y)
    # save
    joblib.dump({'model': model, 'feature_cols': feature_cols}, save_path)
    return model, feature_cols

def load_model(path: str = MODEL_PATH):
    """Load model and feature columns; raises if not found."""
    d = joblib.load(path)
    return d['model'], d['feature_cols']

def predict_volume(model, feature_cols, df: pd.DataFrame) -> np.ndarray:
    """Predict volumes for df using model and feature_cols."""
    # Make sure df has feature_cols; fill missing with zeros
    Xdf = df.copy()
    for c in feature_cols:
        if c not in Xdf.columns:
            Xdf[c] = 0.0
    X = Xdf[feature_cols].astype(float).values
    preds = model.predict(X)
    # ensure non-negative
    preds = np.maximum(preds, 0.0)
    return preds

def evaluate_model(model, feature_cols, df: pd.DataFrame, target: str = 'volume') -> dict:
    """Compute RMSE and MAE on df."""
    y_true = df[target].astype(float).values
    y_pred = predict_volume(model, feature_cols, df)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    return {'rmse': float(rmse), 'mae': float(mae)}
