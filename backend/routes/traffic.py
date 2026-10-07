from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
from pathlib import Path
import os

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

# Load on module initialization if present
try:
    get_model_and_encoder()
except Exception as e:
    print(f"Warning: Model not loaded on import: {e}")


# -----------------------------
# Pydantic Schemas with validation
# -----------------------------
class TrafficInput(BaseModel):
    vehicle_count: int = Field(..., ge=0, le=2000, description="Observed vehicle count (>= 0)")
    average_speed: float = Field(..., ge=0.0, le=250.0, description="Average speed in km/h (0 to 250)")
    road_capacity: int = Field(..., gt=0, le=5000, description="Road capacity in vehicles (> 0)")


# -----------------------------
# Traffic status
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
    metadata_path = BASE_DIR / "ai-model" / "model_metadata.json"
    if not os.path.exists(metadata_path):
        return {
            "status": "partial",
            "model_name": "Traffic Density Random Forest Classifier",
            "features": ["vehicle_count", "average_speed", "road_capacity"]
        }
    with open(metadata_path, "r", encoding="utf-8") as f:
        import json
        data = json.load(f)
    return {
        "status": "success",
        "data": data
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
        "is_simulated": True
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

    return {
        "status": "success",
        "vehicle_count": data.vehicle_count,
        "average_speed": data.average_speed,
        "road_capacity": data.road_capacity,
        "predicted_traffic_density": predicted_label,
        "congestion_ratio_percent": congestion_ratio
    }