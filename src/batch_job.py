# src/batch_job.py
"""
Batch job script for daily price recommendations.
Can be run by cron, Airflow, Prefect, or any scheduler.
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_pipeline import read_history
from src.models import load_model
from src.optimizer import recommend_price
from src.utils import ensure_dirs

# Configuration
DEFAULT_GUARDRAILS = {
    'max_change_pct': 0.03,
    'min_margin': 1.0,
    'min_price': 20.0,
    'max_price': 1000.0,
    'max_vs_comp_pct': 0.10
}

def fetch_today_data(date: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch today's input data.
    In production, this would fetch from a database, API, or data warehouse.
    For now, reads from today_example.json or uses defaults.
    
    Args:
        date: Date string (YYYY-MM-DD). If None, uses today.
    
    Returns:
        Dictionary with today's input data
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Try to read from today_example.json
    today_file = Path("data/today_example.json")
    if today_file.exists():
        with open(today_file, 'r') as f:
            data = json.load(f)
            data['date'] = date  # Override with provided date
            return data
    
    # Default fallback - in production, fetch from real source
    print(f"Warning: today_example.json not found, using defaults")
    history_df = read_history("data/oil_retail_history.csv")
    last_row = history_df.iloc[-1]
    
    return {
        'date': date,
        'cost': float(last_row.get('cost', 85.77)),
        'comp1_price': float(last_row.get('comp1_price', 95.01)) if 'comp1_price' in last_row else 95.01,
        'comp2_price': float(last_row.get('comp2_price', 95.7)) if 'comp2_price' in last_row else 95.7,
        'comp3_price': float(last_row.get('comp3_price', 95.21)) if 'comp3_price' in last_row else 95.21,
        'last_price': float(last_row.get('price', 94.45)) if 'price' in last_row else 94.45
    }

def run_daily_recommendation(
    date: Optional[str] = None,
    guardrails: Optional[Dict[str, Any]] = None,
    output_dir: str = "outputs"
) -> Dict[str, Any]:
    """
    Run daily price recommendation batch job.
    
    Args:
        date: Date string (YYYY-MM-DD). If None, uses today.
        guardrails: Guardrails configuration. If None, uses defaults.
        output_dir: Output directory for saving recommendations.
    
    Returns:
        Recommendation dictionary
    """
    ensure_dirs()
    
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    if guardrails is None:
        guardrails = DEFAULT_GUARDRAILS
    
    print(f"Running daily recommendation for {date}...")
    
    # Load model and history
    try:
        model, feature_cols = load_model()
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        raise
    
    try:
        history_df = read_history("data/oil_retail_history.csv")
        print("✓ Historical data loaded successfully")
    except Exception as e:
        print(f"✗ Error loading historical data: {e}")
        raise
    
    # Fetch today's data
    try:
        today_data = fetch_today_data(date)
        print(f"✓ Today's data fetched: {today_data}")
    except Exception as e:
        print(f"✗ Error fetching today's data: {e}")
        raise
    
    # Generate recommendation
    try:
        recommendation, candidates_df = recommend_price(
            today_data,
            history_df,
            model=model,
            feature_cols=feature_cols,
            guardrails=guardrails
        )
        print(f"✓ Recommendation generated: {recommendation['recommended_price']}")
    except Exception as e:
        print(f"✗ Error generating recommendation: {e}")
        raise
    
    # Save recommendation
    try:
        output_path = Path(output_dir) / f"recommendation_{date}.json"
        with open(output_path, 'w') as f:
            json.dump(recommendation, f, indent=2)
        print(f"✓ Recommendation saved to: {output_path}")
    except Exception as e:
        print(f"✗ Error saving recommendation: {e}")
        raise
    
    return recommendation

def main():
    """Main entry point for batch job."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run daily price recommendation batch job')
    parser.add_argument('--date', type=str, help='Date (YYYY-MM-DD). Default: today')
    parser.add_argument('--output-dir', type=str, default='outputs', help='Output directory')
    parser.add_argument('--guardrails-json', type=str, help='Path to guardrails JSON file')
    
    args = parser.parse_args()
    
    # Load custom guardrails if provided
    guardrails = None
    if args.guardrails_json:
        with open(args.guardrails_json, 'r') as f:
            guardrails = json.load(f)
    
    try:
        recommendation = run_daily_recommendation(
            date=args.date,
            guardrails=guardrails,
            output_dir=args.output_dir
        )
        
        print("\n" + "="*50)
        print("BATCH JOB COMPLETED SUCCESSFULLY")
        print("="*50)
        print(f"Date: {recommendation['date']}")
        print(f"Recommended Price: ₹{recommendation['recommended_price']:.2f}")
        print(f"Expected Volume: {recommendation['expected_volume']:.2f} liters")
        print(f"Expected Profit: ₹{recommendation['expected_profit']:.2f}")
        print(f"Guardrail Applied: {recommendation.get('guardrail_applied', False)}")
        print("="*50)
        
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ BATCH JOB FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

