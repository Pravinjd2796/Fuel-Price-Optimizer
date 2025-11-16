# train_and_evaluate_model.py
"""
Train and evaluate the demand model with comprehensive validation metrics.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from src.data_pipeline import read_history, clean, compute_base_features
from src.models import train_demand_model, evaluate_model, predict_volume
from src.utils import ensure_dirs

def calculate_mape(y_true, y_pred):
    """Calculate Mean Absolute Percentage Error."""
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def detailed_evaluation(model, feature_cols, df: pd.DataFrame, target: str = 'volume', split_name: str = ""):
    """Compute comprehensive evaluation metrics."""
    y_true = df[target].astype(float).values
    y_pred = predict_volume(model, feature_cols, df)
    
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mape = calculate_mape(y_true, y_pred)
    
    # Volume statistics
    mean_volume = np.mean(y_true)
    std_volume = np.std(y_true)
    
    metrics = {
        'RMSE': float(rmse),
        'MAE': float(mae),
        'R²': float(r2),
        'MAPE (%)': float(mape),
        'Mean Volume': float(mean_volume),
        'Std Volume': float(std_volume),
        'RMSE/Mean (%)': float((rmse / mean_volume) * 100) if mean_volume > 0 else 0
    }
    
    if split_name:
        print(f"\n{'='*60}")
        print(f"{split_name} Set Performance:")
        print(f"{'='*60}")
    
    for key, value in metrics.items():
        if 'R²' in key:
            print(f"{key:20s}: {value:8.4f}")
        elif '%' in key:
            print(f"{key:20s}: {value:8.2f}")
        else:
            print(f"{key:20s}: {value:8.2f}")
    
    return metrics

def time_series_cross_validation(model_func, df: pd.DataFrame, feature_cols: list, 
                                  n_splits: int = 5, target: str = 'volume'):
    """Perform time series cross-validation."""
    print(f"\n{'='*60}")
    print(f"Time Series Cross-Validation (n_splits={n_splits})")
    print(f"{'='*60}")
    
    tscv = TimeSeriesSplit(n_splits=n_splits)
    X = df[feature_cols].astype(float).values
    y = df[target].astype(float).values
    dates = pd.to_datetime(df['date'])
    
    cv_metrics = {'RMSE': [], 'MAE': [], 'R²': [], 'MAPE (%)': []}
    
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
        train_dates = dates.iloc[train_idx]
        val_dates = dates.iloc[val_idx]
        
        train_df = df.iloc[train_idx].copy()
        val_df = df.iloc[val_idx].copy()
        
        # Train model on this fold
        model, _ = model_func(train_df, feature_cols=feature_cols)
        
        # Evaluate on validation set
        val_metrics = detailed_evaluation(model, feature_cols, val_df, target, 
                                         f"Fold {fold} (Val: {val_dates.min().date()} to {val_dates.max().date()})")
        
        for key in cv_metrics.keys():
            if key in val_metrics:
                cv_metrics[key].append(val_metrics[key])
    
    # Print CV summary
    print(f"\n{'='*60}")
    print("Cross-Validation Summary:")
    print(f"{'='*60}")
    for metric_name, values in cv_metrics.items():
        mean_val = np.mean(values)
        std_val = np.std(values)
        print(f"{metric_name:20s}: {mean_val:8.2f} (+/- {std_val:8.2f})")
    
    return cv_metrics

def show_feature_importance(model, feature_cols):
    """Display feature importance from the trained model."""
    print(f"\n{'='*60}")
    print("Feature Importance (Top 15):")
    print(f"{'='*60}")
    
    importances = model.feature_importances_
    feature_importance = pd.DataFrame({
        'Feature': feature_cols,
        'Importance': importances
    }).sort_values('Importance', ascending=False)
    
    for idx, row in feature_importance.head(15).iterrows():
        print(f"{row['Feature']:25s}: {row['Importance']:8.4f}")

def split_train_val_test(df: pd.DataFrame, train_ratio: float = 0.7, val_ratio: float = 0.15):
    """Split data into train, validation, and test sets chronologically."""
    df_sorted = df.sort_values('date').reset_index(drop=True)
    n = len(df_sorted)
    
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    train_df = df_sorted.iloc[:train_end].copy()
    val_df = df_sorted.iloc[train_end:val_end].copy()
    test_df = df_sorted.iloc[val_end:].copy()
    
    return train_df, val_df, test_df

def main():
    ensure_dirs()
    
    print("="*60)
    print("FUEL PRICE OPTIMIZATION - MODEL TRAINING & EVALUATION")
    print("="*60)
    
    # Load and prepare data
    history_path = "data/oil_retail_history.csv"
    print(f"\n1. Loading data from {history_path}...")
    df = read_history(history_path)
    print(f"   Loaded {len(df)} rows")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Clean data
    print(f"\n2. Cleaning data...")
    df = clean(df)
    print(f"   After cleaning: {len(df)} rows")
    
    # Compute features
    print(f"\n3. Computing features...")
    df = compute_base_features(df)
    print(f"   After feature engineering: {len(df)} rows")
    
    # Get feature columns
    from src.models import default_feature_columns
    feature_cols = default_feature_columns(df)
    print(f"   Features: {len(feature_cols)}")
    print(f"   Feature list: {', '.join(feature_cols[:5])}... (+{len(feature_cols)-5} more)")
    
    # Split data chronologically
    print(f"\n4. Splitting data chronologically...")
    train_df, val_df, test_df = split_train_val_test(df, train_ratio=0.7, val_ratio=0.15)
    print(f"   Train set: {len(train_df)} rows ({train_df['date'].min()} to {train_df['date'].max()})")
    print(f"   Validation set: {len(val_df)} rows ({val_df['date'].min()} to {val_df['date'].max()})")
    print(f"   Test set: {len(test_df)} rows ({test_df['date'].min()} to {test_df['date'].max()})")
    
    # Train model on training set
    print(f"\n5. Training model on training set...")
    model, _ = train_demand_model(train_df, feature_cols=feature_cols)
    print(f"   Model trained successfully!")
    print(f"   Model type: {type(model).__name__}")
    print(f"   Parameters: n_estimators={model.n_estimators}, max_depth={model.max_depth}, learning_rate={model.learning_rate}")
    
    # Evaluate on train, validation, and test sets
    print(f"\n6. Evaluating model performance...")
    train_metrics = detailed_evaluation(model, feature_cols, train_df, split_name="Training")
    val_metrics = detailed_evaluation(model, feature_cols, val_df, split_name="Validation")
    test_metrics = detailed_evaluation(model, feature_cols, test_df, split_name="Test")
    
    # Show feature importance
    show_feature_importance(model, feature_cols)
    
    # Time series cross-validation
    print(f"\n7. Performing time series cross-validation...")
    def train_wrapper(df, feature_cols):
        return train_demand_model(df, feature_cols=feature_cols)
    
    cv_metrics = time_series_cross_validation(train_wrapper, df, feature_cols, n_splits=5)
    
    # Summary
    print(f"\n{'='*60}")
    print("MODEL TRAINING COMPLETE")
    print(f"{'='*60}")
    print(f"\nModel saved to: models/demand_model.joblib")
    print(f"\nKey Findings:")
    print(f"  - Test RMSE: {test_metrics['RMSE']:.2f} liters")
    print(f"  - Test R²: {test_metrics['R²']:.4f}")
    print(f"  - Test MAPE: {test_metrics['MAPE (%)']:.2f}%")
    print(f"  - RMSE as % of mean volume: {test_metrics['RMSE/Mean (%)']:.2f}%")

if __name__ == "__main__":
    main()

