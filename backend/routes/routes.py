from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import pandas as pd
from pathlib import Path


router = APIRouter(
    prefix="/routes",
    tags=["Route Optimization"]
)


# =============================
# Existing Route Optimization
# =============================

class RouteInput(BaseModel):
    route_a_time: float
    route_a_density: str

    route_b_time: float
    route_b_density: str

    route_c_time: float
    route_c_density: str


# =============================
# ML Traffic Prediction Input
# =============================

class SmartRouteInput(BaseModel):
    vehicle_count: int
    average_speed: float
    road_capacity: int

    route_a_time: float
    route_b_time: float
    route_c_time: float


# =============================
# Load ML Model
# =============================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ai-model" / "traffic_model.pkl"
ENCODER_PATH = BASE_DIR / "ai-model" / "label_encoder.pkl"

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)


# =============================
# Traffic Density Score
# =============================

def density_score(density: str):

    density = density.lower()

    if density == "low":
        return 1

    if density == "medium":
        return 2

    if density == "high":
        return 3

    return 2


# =============================
# Smart Route Optimization
# =============================

@router.post("/optimize")
def optimize_route(data: RouteInput):

    routes = [
        {
            "route": "Route A",
            "travel_time": data.route_a_time,
            "traffic_density": data.route_a_density
        },
        {
            "route": "Route B",
            "travel_time": data.route_b_time,
            "traffic_density": data.route_b_density
        },
        {
            "route": "Route C",
            "travel_time": data.route_c_time,
            "traffic_density": data.route_c_density
        }
    ]

    for route in routes:

        route["density_score"] = density_score(
            route["traffic_density"]
        )

        route["route_score"] = (
            route["travel_time"]
            + (route["density_score"] * 5)
        )

    best_route = min(
        routes,
        key=lambda x: x["route_score"]
    )

    return {
        "status": "success",
        "recommended_route": best_route["route"],
        "estimated_travel_time": best_route["travel_time"],
        "traffic_density": best_route["traffic_density"],
        "route_score": best_route["route_score"],
        "all_routes": routes
    }


# =============================
# ML + Route Optimization
# =============================

@router.post("/smart-predict")
def smart_predict(data: SmartRouteInput):

    # Prepare input for ML model
    input_data = pd.DataFrame([
        {
            "vehicle_count": data.vehicle_count,
            "average_speed": data.average_speed,
            "road_capacity": data.road_capacity
        }
    ])

    # Predict traffic density
    prediction = model.predict(input_data)

    predicted_density = label_encoder.inverse_transform(
        prediction
    )[0]

    # Convert predicted traffic into score
    traffic_score = density_score(
        predicted_density
    )

    # Calculate route scores
    route_a_score = (
        data.route_a_time + traffic_score * 5
    )

    route_b_score = (
        data.route_b_time + traffic_score * 5
    )

    route_c_score = (
        data.route_c_time + traffic_score * 5
    )

    routes = {
        "Route A": route_a_score,
        "Route B": route_b_score,
        "Route C": route_c_score
    }

    # Select lowest score
    recommended_route = min(
        routes,
        key=routes.get
    )

    return {
        "status": "success",
        "predicted_traffic_density": predicted_density,
        "recommended_route": recommended_route,
        "route_scores": routes
    }