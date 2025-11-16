# run_example.py
"""
Simple CLI to run recommendation using data/today_example.json and data/oil_retail_history.csv
"""
import json
from src.data_pipeline import read_history
from src.models import load_model
from src.optimizer import recommend_price
from src.utils import ensure_dirs, save_json

def main():
    ensure_dirs()
    history_path = "data/oil_retail_history.csv"
    today_path = "data/today_example.json"

    hist = read_history(history_path)
    with open(today_path, 'r') as f:
        today = json.load(f)

    model, feature_cols = load_model()
    guardrails = {
        'max_change_pct': 0.03,
        'min_margin': 1.0,
        'min_price': 20.0,
        'max_price': 1000.0,
        'max_vs_comp_pct': 0.10
    }

    rec, candidates_df = recommend_price(today, hist, model=model, feature_cols=feature_cols, guardrails=guardrails, candidate_count=41)

    out_path = f"outputs/recommendation_{rec['date']}.json"
    save_json(rec, out_path)
    print("Recommendation saved to:", out_path)
    print(json.dumps(rec, indent=2))

if __name__ == "__main__":
    main()
