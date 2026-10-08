"""
=============================================================================
Smart Cities AI Traffic Management System
Module: Automated Test Suite - ML Pipeline & Feature Inferences
=============================================================================
"""

import os
import json
from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "ai-model" / "traffic_model.pkl"
ENCODER_PATH = BASE_DIR / "ai-model" / "label_encoder.pkl"
METADATA_PATH = BASE_DIR / "ai-model" / "model_metadata.json"


def test_artifacts_exist():
    assert MODEL_PATH.exists(), "traffic_model.pkl must exist"
    assert ENCODER_PATH.exists(), "label_encoder.pkl must exist"
    assert METADATA_PATH.exists(), "model_metadata.json must exist"


def test_metadata_content():
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["algorithm"] == "Random Forest"
    assert "benchmark_comparison" in meta
    assert "feature_importances" in meta
    # Ensure all 4 models were evaluated in benchmark
    candidates = meta["benchmark_comparison"]
    for expected in ["Random Forest", "Decision Tree", "Logistic Regression", "Gradient Boosting"]:
        assert expected in candidates


def test_model_inference_low_traffic():
    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)

    df_low = pd.DataFrame([{
        "vehicle_count": 15,
        "average_speed": 50.0,
        "road_capacity": 100
    }])
    pred = model.predict(df_low)
    label = encoder.inverse_transform(pred)[0]
    assert label == "Low"


def test_model_inference_high_traffic():
    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)

    df_high = pd.DataFrame([{
        "vehicle_count": 95,
        "average_speed": 15.0,
        "road_capacity": 100
    }])
    pred = model.predict(df_high)
    label = encoder.inverse_transform(pred)[0]
    assert label == "High"
