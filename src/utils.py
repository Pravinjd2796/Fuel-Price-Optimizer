# src/utils.py
"""
Small helper utilities used across the project.
"""
import json
from pathlib import Path
import pandas as pd

def load_json(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)

def save_json(obj: dict, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)

def ensure_dirs():
    for p in ['models', 'outputs']:
        Path(p).mkdir(parents=True, exist_ok=True)
