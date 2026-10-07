import random
import datetime
import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd

from app.database import insert_traffic_record, get_traffic_history

router = APIRouter(
    prefix="/traffic",
    tags=["Traffic"]
)

# -----------------------------
# Safe Model Loading
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "ai-model" / "traffic_model.pkl"
ENCODER_PATH = BASE_DIR / "ai-model" / "label_encoder.pkl"
METADATA_PATH = BASE_DIR / "ai-model" / "model_metadata.json"

model = None
label_encoder = None

def get_model_and_encoder():
    global model, label_encoder
    if model is None or label_encoder is None:
        if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODER_PATH):
            raise RuntimeError(f"Model artifacts not found at {MODEL_PATH} or {ENCODER_PATH}")
        model = joblib.load(MODEL_PATH)
        label_encoder = joblib.load(ENCODER_PATH)
    return model, label_encoder

try:
    get_model_and_encoder()
except Exception:
    pass


# -----------------------------
# Pydantic Schemas with validation
# -----------------------------
class TrafficInput(BaseModel):
    vehicle_count: int = Field(..., ge=0, le=2000, description="Observed vehicle count (>= 0)")
    average_speed: float = Field(..., ge=0.0, le=250.0, description="Average speed in km/h (0 to 250)")
    road_capacity: int = Field(..., gt=0, le=5000, description="Road capacity in vehicles (> 0)")


class SimulationTriggerInput(BaseModel):
    scenario: str = Field(default="random", description="Scenario type: random, rush_hour, night, normal")


# -----------------------------
# Traffic status & model info
# -----------------------------
@router.get("/status")
def traffic_status():
    m, _ = get_model_and_encoder() if os.path.exists(MODEL_PATH) else (None, None)
    return {
        "status": "success",
        "message": "Traffic module is active",
        "model_loaded": m is not None
    }


@router.get("/model-info")
def get_model_info():
    if not os.path.exists(METADATA_PATH):
        return {
            "status": "partial",
            "model_name": "Traffic Density Random Forest Classifier",
            "features": ["vehicle_count", "average_speed", "road_capacity"]
        }
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        "status": "success",
        "data": data
    }


# -----------------------------
# Historical Records
# -----------------------------
@router.get("/history")
def traffic_history_endpoint(limit: int = 50):
    records = get_traffic_history(limit=limit)
    return {
        "status": "success",
        "count": len(records),
        "records": records
    }


# -----------------------------
# Traffic density (Simulated / Demo sample)
# -----------------------------
@router.get("/density")
def traffic_density():
    return {
        "status": "success",
        "location": "City Central Corridor",
        "density": "High",
        "vehicle_count": 85,
        "is_simulated": True,
        "label": "Demo / Simulated Traffic Data"
    }


# -----------------------------
# ML Traffic Prediction
# -----------------------------
@router.post("/predict")
def predict_traffic(data: TrafficInput):
    try:
        active_model, active_encoder = get_model_and_encoder()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"ML Model unavailable: {str(exc)}")

    input_data = pd.DataFrame([
        {
            "vehicle_count": data.vehicle_count,
            "average_speed": data.average_speed,
            "road_capacity": data.road_capacity
        }
    ])

    prediction = active_model.predict(input_data)
    predicted_label = active_encoder.inverse_transform(prediction)[0]
    
    # Calculate congestion utilization ratio
    congestion_ratio = round((data.vehicle_count / data.road_capacity) * 100, 2)

    # Persist in SQLite database
    try:
        insert_traffic_record(
            vehicle_count=data.vehicle_count,
            average_speed=data.average_speed,
            road_capacity=data.road_capacity,
            predicted_density=predicted_label,
            congestion_ratio=congestion_ratio,
            source="manual"
        )
    except Exception as db_err:
        print(f"Warning: Failed to log prediction to database: {db_err}")

    return {
        "status": "success",
        "vehicle_count": data.vehicle_count,
        "average_speed": data.average_speed,
        "road_capacity": data.road_capacity,
        "predicted_traffic_density": predicted_label,
        "congestion_ratio_percent": congestion_ratio
    }


# -----------------------------
# Live Simulation Generator Endpoint
# -----------------------------
@router.post("/simulate")
def simulate_traffic(trigger: SimulationTriggerInput = SimulationTriggerInput()):
    """Generates realistic synthetic sensor telemetry and runs it through the ML model."""
    active_model, active_encoder = get_model_and_encoder()

    scenario = trigger.scenario.lower()
    capacity = 100

    if scenario == "rush_hour":
        vehicles = random.randint(82, 98)
        speed = round(random.uniform(14.0, 22.0), 1)
    elif scenario == "night":
        vehicles = random.randint(12, 28)
        speed = round(random.uniform(44.0, 56.0), 1)
    else:  # normal / random
        vehicles = random.randint(35, 75)
        speed = round(random.uniform(28.0, 42.0), 1)

    input_data = pd.DataFrame([
        {
            "vehicle_count": vehicles,
            "average_speed": speed,
            "road_capacity": capacity
        }
    ])

    pred = active_model.predict(input_data)
    density = active_encoder.inverse_transform(pred)[0]
    congestion = round((vehicles / capacity) * 100, 2)

    # Log to SQLite
    try:
        record_id = insert_traffic_record(
            vehicle_count=vehicles,
            average_speed=speed,
            road_capacity=capacity,
            predicted_density=density,
            congestion_ratio=congestion,
            source="simulation"
        )
    except Exception as db_err:
        record_id = None
        print(f"Simulation DB log warning: {db_err}")

    return {
        "status": "success",
        "data_tag": "Demo / Simulated Traffic Data",
        "scenario": scenario,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "record_id": record_id,
        "vehicle_count": vehicles,
        "average_speed": speed,
        "road_capacity": capacity,
        "predicted_traffic_density": density,
        "congestion_ratio_percent": congestion
    }