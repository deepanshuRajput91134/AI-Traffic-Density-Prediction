import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
import cv2
import numpy as np

# Add project root to sys.path to access computer-vision module
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR / "computer-vision") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "computer-vision"))

from vehicle_detector import VehicleDetector
from routes.traffic import get_model_and_encoder
from app.database import insert_traffic_record
import pandas as pd

router = APIRouter(
    prefix="/vision",
    tags=["Computer Vision Telemetry"]
)

detector = VehicleDetector()


@router.get("/status")
def vision_status():
    return {
        "status": "active",
        "engine": "OpenCV CPU Vehicle Telemetry Detector",
        "supported_classes": ["car", "bus", "truck", "motorcycle"]
    }


@router.post("/demo-feed")
def demo_vision_feed(target_vehicles: int = 54):
    """
    Simulates a live traffic camera feed, detects vehicles,
    and pipes the count directly into the ML Traffic Model.
    """
    canvas, meta = detector.generate_demo_frame(vehicle_target_count=target_vehicles)
    
    # Run through ML model
    active_model, active_encoder = get_model_and_encoder()
    input_df = pd.DataFrame([{
        "vehicle_count": meta["detected_count"],
        "average_speed": meta["average_speed_kmh"],
        "road_capacity": meta["road_capacity"]
    }])

    pred = active_model.predict(input_df)
    predicted_density = active_encoder.inverse_transform(pred)[0]
    congestion = round((meta["detected_count"] / meta["road_capacity"]) * 100, 2)

    # Persist in SQLite
    try:
        insert_traffic_record(
            vehicle_count=meta["detected_count"],
            average_speed=meta["average_speed_kmh"],
            road_capacity=meta["road_capacity"],
            predicted_density=predicted_density,
            congestion_ratio=congestion,
            source="vision"
        )
    except Exception as e:
        print(f"Vision DB log error: {e}")

    return {
        "status": "success",
        "source": "cctv_camera_feed",
        "camera_metadata": meta,
        "ai_prediction": {
            "predicted_traffic_density": predicted_density,
            "congestion_ratio_percent": congestion
        }
    }
