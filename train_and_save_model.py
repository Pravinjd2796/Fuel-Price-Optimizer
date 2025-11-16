# train_and_save_model.py
"""
Train and save the demand model using historical data.
"""
from src.data_pipeline import read_history, clean, compute_base_features
from src.models import train_demand_model, evaluate_model
from src.utils import ensure_dirs

def main():
    ensure_dirs()
    
    # Load and prepare data
    history_path = "data/oil_retail_history.csv"
    print(f"Loading data from {history_path}...")
    df = read_history(history_path)
    print(f"Loaded {len(df)} rows")
    
    # Clean data
    print("Cleaning data...")
    df = clean(df)
    
    # Compute features
    print("Computing features...")
    df = compute_base_features(df)
    print(f"After feature engineering: {len(df)} rows")
    
    # Train model
    print("Training model...")
    model, feature_cols = train_demand_model(df)
    print(f"Model trained with {len(feature_cols)} features: {feature_cols}")
    
    # Evaluate model
    print("Evaluating model...")
    metrics = evaluate_model(model, feature_cols, df)
    print(f"Metrics: RMSE={metrics['rmse']:.2f}, MAE={metrics['mae']:.2f}")
    
    print("Model saved successfully!")

if __name__ == "__main__":
    main()

