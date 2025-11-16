# src/api.py
"""
FastAPI wrapper for the recommend function.
Run with: uvicorn src.api:app --reload --port 8000

API Endpoints:
- POST /recommend: Get price recommendation
  Request body: {
    "date": "2024-12-31",
    "cost": 85.77,
    "comp1_price": 95.01,
    "comp2_price": 95.7,
    "comp3_price": 95.21,
    "last_price": 94.45  // optional, defaults to last historical price
  }

- GET /: API documentation
- GET /docs: Interactive API documentation (Swagger UI)
- GET /redoc: Alternative API documentation (ReDoc)
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from src.data_pipeline import read_history
from src.models import load_model
from src.optimizer import recommend_price

app = FastAPI(title="Fuel Price Optimization API")

class TodayInput(BaseModel):
    date: str
    cost: float
    comp1_price: Optional[float] = None
    comp2_price: Optional[float] = None
    comp3_price: Optional[float] = None
    last_price: Optional[float] = None

# load at startup for demo simplicity
MODEL, FEATURE_COLS = load_model()
HIST = read_history("data/oil_retail_history.csv")

@app.get("/")
def root():
    return {
        "message": "Fuel Price Optimization API",
        "endpoints": {
            "POST /recommend": "Get price recommendation",
            "GET /health": "Health check",
            "GET /docs": "Interactive API documentation"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": MODEL is not None}

@app.post("/recommend")
def recommend(payload: TodayInput):
    guardrails = {
        'max_change_pct': 0.03,
        'min_margin': 1.0,
        'min_price': 20.0,
        'max_price': 1000.0,
        'max_vs_comp_pct': 0.10
    }
    rec, _ = recommend_price(payload.dict(), HIST, model=MODEL, feature_cols=FEATURE_COLS, guardrails=guardrails)
    return rec
