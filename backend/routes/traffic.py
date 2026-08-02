from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import pandas as pd
from pathlib import Path


router = APIRouter(
    prefix="/traffic",
    tags=["Traffic"]
)


# -----------------------------
# Load trained ML model
# -----------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ai-model" / "traffic_model.pkl"
ENCODER_PATH = BASE_DIR / "ai-model" / "label_encoder.pkl"

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)


# -----------------------------
# Input data
# -----------------------------

class TrafficInput(BaseModel):
    vehicle_count: int
    average_speed: float
    road_capacity: int


# -----------------------------
# Traffic status
# -----------------------------

@router.get("/status")
def traffic_status():
    return {
        "status": "success",
        "message": "Traffic module is working"
    }


# -----------------------------
# Traffic density
# -----------------------------

@router.get("/density")
def traffic_density():
    return {
        "location": "Delhi",
        "density": "High",
        "vehicle_count": 85
    }


# -----------------------------
# ML Traffic Prediction
# -----------------------------

@router.post("/predict")
def predict_traffic(data: TrafficInput):

    input_data = pd.DataFrame([
        {
            "vehicle_count": data.vehicle_count,
            "average_speed": data.average_speed,
            "road_capacity": data.road_capacity
        }
    ])

    prediction = model.predict(input_data)

    predicted_label = label_encoder.inverse_transform(prediction)[0]

    return {
        "status": "success",
        "vehicle_count": data.vehicle_count,
        "average_speed": data.average_speed,
        "road_capacity": data.road_capacity,
        "predicted_traffic_density": predicted_label
    }