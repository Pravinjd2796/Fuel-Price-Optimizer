# Fuel Price Optimization System - Project Summary

**ML Engineer Assignment: Fuel Price Optimization**  
**Date:** November 2024  
**Status:** ✅ Complete and Production-Ready

---

## Executive Summary

This project implements a machine learning-based fuel price optimization system for a retail petrol company. The system recommends the optimal daily retail price to maximize profit while respecting business guardrails and market conditions. The solution includes data engineering pipelines, ML model training, price optimization algorithms, and a REST API for deployment.

---

## 1. Business Context & Objective

### Business Problem
A retail petrol company operates in an open market where competitors change prices daily. The company sets its retail price once per day at the start of the day. The objective is to **maximize daily profit** by choosing the optimal price.

### Solution Approach
- **Machine Learning Model**: XGBoost regression to predict demand (volume) based on price and market features
- **Optimization Strategy**: Grid search over candidate prices to maximize profit (profit = (price - cost) × predicted_volume)
- **Business Rules**: Guardrails to ensure price stability, competitiveness, and minimum margins

---

## 2. Data Overview

### Historical Data (`oil_retail_history.csv`)
- **Records**: 730 days (2023-01-01 to 2024-12-30)
- **Columns**:
  - `date`: Calendar date
  - `price`: Company's historical retail price
  - `cost`: Company's cost per liter
  - `comp1_price`, `comp2_price`, `comp3_price`: Competitor prices
  - `volume`: Liters sold (target variable)

### Daily Input (`today_example.json`)
- `date`: Today's date
- `cost`: Today's cost per liter
- `comp1_price`, `comp2_price`, `comp3_price`: Today's competitor prices
- `last_price`: Company's last observed price (optional)

---

## 3. System Architecture

### 3.1 Data Engineering Pipeline

**Module**: `src/data_pipeline.py`

**Functions**:
- `read_history()`: Loads historical CSV data
- `clean()`: Removes duplicates, handles missing values, validates data types
- `compute_base_features()`: Feature engineering including:
  - **Price features**: Price differentials, moving averages, lags
  - **Competitor features**: Mean, min, max competitor prices
  - **Volume features**: 7-day and 30-day moving averages, lags (1-day, 7-day)
  - **Temporal features**: Day of week, weekend flag, month
  - **Business features**: Margin, margin percentage

**Output**: Processed DataFrame ready for ML training

### 3.2 Machine Learning Model

**Module**: `src/models.py`

**Model Type**: XGBoost Regressor (Gradient Boosting)

**Hyperparameters**:
- `n_estimators`: 300
- `max_depth`: 6
- `learning_rate`: 0.05
- `objective`: 'reg:squarederror'

**Training Process**:
- Uses all features from feature engineering
- Target variable: `volume` (liters sold)
- Handles missing features by filling with zeros
- Ensures non-negative volume predictions

**Model Performance** (from evaluation):
- **Training Set**:
  - RMSE: 42.06 liters
  - MAE: 29.59 liters
  - R²: 0.9977
  - MAPE: 0.21%
- **Test Set**:
  - RMSE: 732.85 liters
  - MAE: 551.24 liters
  - R²: 0.3274
  - MAPE: 3.97%
  - RMSE as % of mean: 5.27%

**Cross-Validation** (Time Series Split, 5 folds):
- Average RMSE: 787.42 (±39.62) liters
- Average R²: 0.23 (±0.15)
- Average MAPE: 4.40% (±0.34%)

**Key Insights**:
- Model shows some overfitting (high train R² vs lower test R²)
- However, practical accuracy is good with ~4% MAPE on unseen data
- Most important feature: `dayofweek` (56.14% importance), indicating strong weekly seasonality

### 3.3 Price Optimization

**Module**: `src/optimizer.py`

**Algorithm**:
1. **Generate candidate prices**: Grid of 41 prices within ±3% of last price (configurable)
2. **Predict demand**: Use ML model to predict volume for each candidate price
3. **Calculate profit**: Profit = (price - cost) × predicted_volume
4. **Apply guardrails**: Filter candidates that violate business rules
5. **Select optimal**: Choose price with maximum profit among valid candidates

**Business Guardrails**:
- `max_change_pct`: Maximum allowed daily price change (default: 3%)
- `min_margin`: Minimum profit margin per liter
- `min_price`, `max_price`: Price floor and ceiling
- `max_vs_comp_pct`: Maximum price above highest competitor (competitive constraint)

### 3.4 API Service

**Module**: `src/api.py`

**Framework**: FastAPI

**Endpoints**:
- `GET /`: API information
- `GET /health`: Health check (verifies model is loaded)
- `POST /recommend`: Get price recommendation
  - **Request Body**:
    ```json
    {
      "date": "2024-12-31",
      "cost": 85.77,
      "comp1_price": 95.01,
      "comp2_price": 95.7,
      "comp3_price": 95.21,
      "last_price": 94.45
    }
    ```
  - **Response**:
    ```json
    {
      "date": "2024-12-31",
      "recommended_price": 97.14,
      "expected_volume": 14284.52,
      "expected_profit": 162441.10,
      "guardrail_applied": false,
      "violation_reason": null,
      "candidates_tried": 41
    }
    ```
- `GET /docs`: Interactive Swagger UI documentation

---

## 4. Feature Engineering Details

### Price-Based Features
- `price`: Current price
- `price_diff`: Price difference from mean competitor price
- `price_ma7`: 7-day moving average of price
- `price_lag1`: Previous day's price

### Competitor Features
- `comp_mean`: Average of competitor prices
- `comp_min`: Minimum competitor price
- `comp_max`: Maximum competitor price

### Volume-Based Features (Historical Patterns)
- `vol_ma7`: 7-day moving average of volume
- `vol_ma30`: 30-day moving average of volume
- `vol_lag1`: Previous day's volume
- `vol_lag7`: Volume from 7 days ago

### Temporal Features
- `dayofweek`: Day of week (0-6)
- `is_weekend`: Boolean flag
- `month`: Month (1-12)

### Business Features
- `margin`: Price - cost
- `margin_pct`: (Price - cost) / cost × 100

**Total Features**: 16

**Top 5 Most Important Features**:
1. `dayofweek` (56.14%)
2. `margin` (4.87%)
3. `margin_pct` (4.18%)
4. `price_diff` (3.77%)
5. `vol_lag1` (3.56%)

---

## 5. Model Training & Validation

### Training Process

**Script**: `train_and_evaluate_model.py`

**Steps**:
1. Load historical data (730 rows)
2. Clean data (remove duplicates, handle missing values)
3. Feature engineering (compute 16 features)
4. Chronological split:
   - Training: 510 rows (70%, 2023-01-02 to 2024-05-25)
   - Validation: 109 rows (15%, 2024-05-26 to 2024-09-11)
   - Test: 110 rows (15%, 2024-09-12 to 2024-12-30)
5. Train XGBoost model on training set
6. Evaluate on validation and test sets
7. Perform time series cross-validation
8. Save model to `models/demand_model.joblib`

### Validation Strategy

**Time Series Cross-Validation**: 
- Uses `TimeSeriesSplit` (5 folds) to respect temporal order
- Prevents data leakage by ensuring training data always precedes validation data

**Metrics Tracked**:
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- R² (Coefficient of Determination)
- MAPE (Mean Absolute Percentage Error)

---

## 6. Business Guardrails Implementation

### Guardrail Rules

1. **Maximum Price Change**: Limits daily price changes to prevent sudden shocks
   - Default: ±3% from last price
   - Prevents customer backlash and maintains brand trust

2. **Minimum Margin**: Ensures profitability
   - Default: 0 (can be set to minimum acceptable margin)
   - Prevents selling below cost

3. **Price Bounds**: Absolute minimum and maximum prices
   - Can be set based on market regulations or business rules

4. **Competitive Constraint**: Maintains market competitiveness
   - Maximum price vs highest competitor
   - Prevents pricing too far above market

**Implementation**: If guardrails are violated, the system:
- First tries to find best price within guardrails
- If no valid candidates exist, returns best price but flags `guardrail_applied: true`

---

## 7. Usage Examples

### 7.1 Command Line Interface

**Script**: `run_example.py`

```bash
cd "/Users/pravinjadhav/Desktop/Pravin/fuel price optimizer"
source venv/bin/activate
python run_example.py
```

**Output**:
- Saves recommendation to `outputs/recommendation_YYYY-MM-DD.json`
- Displays recommended price, expected volume, and profit

### 7.2 API Usage

**Start Server**:
```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

**Test with curl**:
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-12-31",
    "cost": 85.77,
    "comp1_price": 95.01,
    "comp2_price": 95.7,
    "comp3_price": 95.21,
    "last_price": 94.45
  }'
```

### 7.3 Testing

**Run Tests**:
```bash
python -m pytest tests/ -v
```

**Test Coverage**: End-to-end pipeline testing

---

## 8. Project Structure

```
fuel price optimizer/
├── data/
│   ├── oil_retail_history.csv    # Historical training data
│   └── today_example.json         # Example daily input
├── models/
│   └── demand_model.joblib        # Trained XGBoost model
├── outputs/
│   └── recommendation_*.json      # Generated recommendations
├── src/
│   ├── api.py                     # FastAPI REST API
│   ├── data_pipeline.py           # Data ingestion & cleaning
│   ├── features.py                # Feature engineering
│   ├── models.py                  # ML model training/prediction
│   ├── optimizer.py               # Price optimization logic
│   └── utils.py                   # Utility functions
├── tests/
│   └── test_pipeline.py           # Unit tests
├── notebook/
│   ├── 1_exploration_and_feature_engineering.ipynb
│   └── 2_modeling_and_simulation.ipynb
├── requirements.txt               # Python dependencies
├── train_and_evaluate_model.py   # Training with full validation
├── train_and_save_model.py       # Simple training script
├── run_example.py                 # CLI recommendation tool
└── STEPS_TO_RUN.md               # Setup instructions
```

---

## 9. Key Technical Decisions

### Why XGBoost?
- **Non-linear relationships**: Captures complex price-demand relationships
- **Feature importance**: Provides interpretability
- **Handles missing data**: Robust to missing features
- **Time-efficient**: Fast training and prediction

### Why Grid Search for Optimization?
- **Simplicity**: Easy to understand and debug
- **Transparent**: All candidates are evaluated and can be inspected
- **Business-friendly**: Allows guardrails to be easily applied
- **Sufficient**: 41 candidates (±3%) provides fine-grained control

### Why Time Series Split?
- **Respects temporal order**: Prevents data leakage
- **Realistic validation**: Mimics production scenario where past predicts future
- **Better evaluation**: More realistic performance estimates

---

## 10. Model Performance Analysis

### Strengths
✅ **Good practical accuracy**: ~4% MAPE on test data  
✅ **Captures seasonality**: Day of week is most important feature  
✅ **Stable predictions**: Low variance in cross-validation  
✅ **Fast inference**: Predictions in milliseconds  

### Limitations
⚠️ **Overfitting**: High training R² (0.9977) vs test R² (0.3274)  
⚠️ **Limited generalization**: Model may struggle with extreme market conditions  
⚠️ **Static guardrails**: Guardrails don't adapt to market volatility  

### Recommendations for Improvement
1. **Regularization**: Add L1/L2 regularization to reduce overfitting
2. **Ensemble methods**: Combine multiple models for robustness
3. **Dynamic guardrails**: Adjust guardrails based on market volatility
4. **Feature selection**: Focus on most important features to reduce complexity
5. **Time series models**: Consider ARIMA/LSTM for better temporal modeling
6. **Reinforcement learning**: Explore RL for adaptive pricing strategies

---

## 11. Deployment Readiness

### Production Considerations

✅ **API Service**: FastAPI server ready for deployment  
✅ **Model Persistence**: Model saved and can be versioned  
✅ **Error Handling**: Guardrails prevent invalid recommendations  
✅ **Health Checks**: API includes health monitoring endpoint  
✅ **Documentation**: Interactive API docs available  

### Recommended Next Steps

1. **Containerization**: Dockerize the application
2. **Model Versioning**: Implement MLflow or similar for model tracking
3. **Monitoring**: Add logging and monitoring for model performance
4. **A/B Testing**: Framework to test pricing strategies
5. **Retraining Pipeline**: Automated retraining on new data
6. **CI/CD**: Automated testing and deployment pipelines

---

## 12. Example Results

### Sample Recommendation

**Input**:
```json
{
  "date": "2024-12-31",
  "cost": 85.77,
  "comp1_price": 95.01,
  "comp2_price": 95.7,
  "comp3_price": 95.21,
  "last_price": 94.45
}
```

**Output**:
```json
{
  "date": "2024-12-31",
  "recommended_price": 97.14,
  "expected_volume": 14284.52,
  "expected_profit": 162441.10,
  "guardrail_applied": false,
  "violation_reason": null,
  "candidates_tried": 41
}
```

**Interpretation**:
- Recommended price: ₹97.14 per liter
- Expected sales: 14,284.52 liters
- Expected profit: ₹162,441.10
- All guardrails passed
- System evaluated 41 price candidates

---

## 13. Conclusion

This fuel price optimization system successfully demonstrates:

✅ **End-to-end ML pipeline**: From data ingestion to price recommendation  
✅ **Production-ready code**: Modular, tested, and documented  
✅ **Business alignment**: Incorporates guardrails and business rules  
✅ **Practical accuracy**: ~4% MAPE suitable for real-world deployment  
✅ **API-first design**: RESTful API enables easy integration  

The system is ready for pilot deployment with ongoing monitoring and iterative improvements based on real-world performance data.

---

## 14. Contact & Documentation

- **Project Repository**: `/Users/pravinjadhav/Desktop/Pravin/fuel price optimizer`
- **API Documentation**: `http://localhost:8000/docs` (when server is running)
- **Setup Guide**: See `STEPS_TO_RUN.md`

---

**End of Summary Document**

