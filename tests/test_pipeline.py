# tests/test_pipeline.py
import pandas as pd
from src.data_pipeline import read_history, clean, compute_base_features, prepare_day_input

def test_end_to_end(tmp_path):
    # create a minimal CSV
    p = tmp_path / "history.csv"
    df = pd.DataFrame({
        'date': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05', '2025-01-06', '2025-01-07', '2025-01-08'],
        'price': [100, 101, 99, 100, 102, 101, 103, 104],
        'cost': [90, 90, 90, 90, 90, 90, 90, 90],
        'comp1': [98, 100, 101, 99, 100, 102, 101, 100],
        'comp2': [99, 100, 100, 99, 101, 101, 100, 99],
        'comp3': [97, 99, 100, 98, 100, 100, 102, 101],
        'volume': [1000, 1100, 1050, 1030, 1200, 1150, 1250, 1300]
    })
    df.to_csv(p, index=False)
    hist = read_history(str(p))
    assert len(hist) == 8
    cleaned = clean(hist)
    feats = compute_base_features(cleaned)
    assert 'vol_ma7' in feats.columns
    # prepare day input (today JSON)
    today = {
        'date': '2025-01-09',
        'cost': 90,
        'comp1': 100,
        'comp2': 99,
        'comp3': 101,
        'last_price': 104
    }
    base = prepare_day_input(today, feats)
    assert base.shape[0] == 1
    assert 'vol_ma7' in base.columns
