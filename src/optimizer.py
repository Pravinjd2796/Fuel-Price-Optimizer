# src/optimizer.py
"""
Price candidate generation, guardrails and recommendation logic.
"""
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any
from src.features import features_dataframe_from_candidate
from src.models import load_model, predict_volume

def candidate_prices(last_price: float,
                     max_change_pct: float = 0.03,
                     min_price: float = None,
                     max_price: float = None,
                     n: int = 41) -> np.ndarray:
    """Return a grid of candidate prices around last_price within max_change_pct and bounds."""
    lower = last_price * (1 - max_change_pct)
    upper = last_price * (1 + max_change_pct)
    if min_price is not None:
        lower = max(lower, min_price)
    if max_price is not None:
        upper = min(upper, max_price)
    return np.linspace(lower, upper, n)

def violates_guardrails(price: float, cost: float, last_price: float, guardrails: dict) -> Tuple[bool, str]:
    """
    Check simple numeric guardrails and return (violated, reason)
    """
    if guardrails is None:
        return False, None
    max_change_pct = guardrails.get('max_change_pct', 0.1)
    min_margin = guardrails.get('min_margin', 0.0)
    min_price = guardrails.get('min_price', -np.inf)
    max_price = guardrails.get('max_price', np.inf)
    if last_price > 0 and abs(price - last_price) / last_price > max_change_pct:
        return True, 'max_change_pct'
    if price - cost < min_margin:
        return True, 'min_margin'
    if price < min_price or price > max_price:
        return True, 'price_floor_or_ceiling'
    return False, None

def recommend_price(today_json: dict,
                    historical_df: pd.DataFrame,
                    model=None,
                    feature_cols=None,
                    guardrails: dict = None,
                    candidate_count: int = 41) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """
    Main function to recommend price. Returns (recommendation_dict, candidates_dataframe).
    """
    # lazy-load model
    if model is None or feature_cols is None:
        model, feature_cols = load_model()

    from src.data_pipeline import prepare_day_input
    base_df = prepare_day_input(today_json, historical_df)
    base_row = base_df.iloc[[0]]  # one-row DataFrame
    last_price = float(base_row['last_price'].iloc[0])
    cost = float(base_row['cost'].iloc[0]) if 'cost' in base_row.columns else 0.0
    comp_max = float(base_row.get('comp_max').iloc[0]) if 'comp_max' in base_row.columns else None

    # generate candidates
    candidates = candidate_prices(last_price,
                                  max_change_pct=guardrails.get('max_change_pct', 0.03) if guardrails else 0.03,
                                  min_price=guardrails.get('min_price') if guardrails else None,
                                  max_price=guardrails.get('max_price') if guardrails else None,
                                  n=candidate_count)
    feats = features_dataframe_from_candidate(base_row, candidates)
    # ensure model feature columns are present
    for c in feature_cols:
        if c not in feats.columns:
            feats[c] = 0.0

    preds = predict_volume(model, feature_cols, feats)
    records = []
    for i, p in enumerate(candidates):
        pred_vol = float(preds[i])
        pred_profit = float((p - cost) * pred_vol)
        violated, reason = violates_guardrails(float(p), cost, last_price, guardrails or {})
        # competitor guardrail
        comp_violation = False
        comp_reason = None
        if guardrails and guardrails.get('max_vs_comp_pct') is not None and comp_max is not None:
            if p > comp_max * (1 + guardrails['max_vs_comp_pct']):
                comp_violation = True
                comp_reason = 'comp_too_high'
        records.append({
            'price': float(p),
            'pred_volume': pred_vol,
            'pred_profit': pred_profit,
            'violated': bool(violated or comp_violation),
            'violation_reason': comp_reason or reason
        })
    cand_df = pd.DataFrame(records)

    allowed = cand_df[~cand_df['violated']]
    if not allowed.empty:
        best = allowed.loc[allowed['pred_profit'].idxmax()].to_dict()
        best['guardrail_applied'] = False
    else:
        # fallback: pick global best but note guardrail
        best = cand_df.loc[cand_df['pred_profit'].idxmax()].to_dict()
        best['guardrail_applied'] = True
    recommendation = {
        'date': str(base_row['date'].iloc[0].date()),
        'recommended_price': float(best['price']),
        'expected_volume': float(best['pred_volume']),
        'expected_profit': float(best['pred_profit']),
        'guardrail_applied': bool(best.get('guardrail_applied', False)),
        'violation_reason': best.get('violation_reason', None),
        'candidates_tried': int(len(candidates))
    }
    return recommendation, cand_df
