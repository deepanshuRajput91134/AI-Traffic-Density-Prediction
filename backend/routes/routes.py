from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
from pathlib import Path
import os

router = APIRouter(
    prefix="/routes",
    tags=["Route Optimization"]
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

try:
    get_model_and_encoder()
except Exception:
    pass


# =============================
# Route Optimization Schemas
# =============================
class RouteInput(BaseModel):
    route_a_time: float = Field(..., gt=0, description="Estimated time for Route A (minutes)")
    route_a_density: str = Field(..., description="Observed traffic density for Route A (Low/Medium/High)")

    route_b_time: float = Field(..., gt=0, description="Estimated time for Route B (minutes)")
    route_b_density: str = Field(..., description="Observed traffic density for Route B (Low/Medium/High)")

    route_c_time: float = Field(..., gt=0, description="Estimated time for Route C (minutes)")
    route_c_density: str = Field(..., description="Observed traffic density for Route C (Low/Medium/High)")


class SmartRouteInput(BaseModel):
    vehicle_count: int = Field(..., ge=0, description="Observed vehicle count")
    average_speed: float = Field(..., ge=0.0, description="Average speed in km/h")
    road_capacity: int = Field(..., gt=0, description="Road capacity")

    route_a_time: float = Field(..., gt=0, description="Base travel time for Route A (minutes)")
    route_b_time: float = Field(..., gt=0, description="Base travel time for Route B (minutes)")
    route_c_time: float = Field(..., gt=0, description="Base travel time for Route C (minutes)")


# =============================
# Traffic Density Scoring Helper
# =============================
def density_score(density: str) -> int:
    clean_density = str(density).strip().lower()
    if clean_density == "low":
        return 1
    elif clean_density == "medium":
        return 2
    elif clean_density == "high":
        return 3
    return 2


# =============================
# Endpoint: Heuristic Route Optimization
# =============================
@router.post("/optimize")
def optimize_route(data: RouteInput):
    routes = [
        {
            "route": "Route A",
            "travel_time": data.route_a_time,
            "traffic_density": data.route_a_density,
            "corridor_type": "Main Arterial Avenue"
        },
        {
            "route": "Route B",
            "travel_time": data.route_b_time,
            "traffic_density": data.route_b_density,
            "corridor_type": "Express Bypass Expressway"
        },
        {
            "route": "Route C",
            "travel_time": data.route_c_time,
            "traffic_density": data.route_c_density,
            "corridor_type": "Outer Ring Road"
        }
    ]

    for route in routes:
        route["density_score"] = density_score(route["traffic_density"])
        # Score = Travel Time + (Density Penalty Factor * 5)
        route["route_score"] = round(route["travel_time"] + (route["density_score"] * 5), 2)

    # Sort routes by score ascending (lowest score is best)
    sorted_routes = sorted(routes, key=lambda x: x["route_score"])
    best_route = sorted_routes[0]

    # Generate explanatory justification
    reason = (
        f"Selected {best_route['route']} ({best_route['corridor_type']}) due to optimal balance "
        f"of travel time ({best_route['travel_time']} min) and {best_route['traffic_density']} traffic density "
        f"(Composite Score: {best_route['route_score']})."
    )

    return {
        "status": "success",
        "recommended_route": best_route["route"],
        "estimated_travel_time": best_route["travel_time"],
        "traffic_density": best_route["traffic_density"],
        "route_score": best_route["route_score"],
        "recommendation_reason": reason,
        "all_routes": sorted_routes
    }


# =============================
# Endpoint: ML-Driven Smart Route Optimization
# =============================
@router.post("/smart-predict")
def smart_predict(data: SmartRouteInput):
    try:
        active_model, active_encoder = get_model_and_encoder()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"ML Model unavailable: {str(exc)}")

    # Prepare input for ML model
    input_data = pd.DataFrame([
        {
            "vehicle_count": data.vehicle_count,
            "average_speed": data.average_speed,
            "road_capacity": data.road_capacity
        }
    ])

    prediction = active_model.predict(input_data)
    predicted_density = active_encoder.inverse_transform(prediction)[0]
    base_traffic_score = density_score(predicted_density)

    # Real-world corridor sensitivity factors:
    # Route A (Main Arterial): High sensitivity to sector congestion (multiplier 1.4)
    # Route B (Expressway Bypass): Medium sensitivity (multiplier 1.0)
    # Route C (Outer Ring Road): Low sensitivity (multiplier 0.7)
    corridors = {
        "Route A": {
            "name": "Main Arterial Avenue",
            "base_time": data.route_a_time,
            "congestion_sensitivity": 1.4,
        },
        "Route B": {
            "name": "Express Bypass Expressway",
            "base_time": data.route_b_time,
            "congestion_sensitivity": 1.0,
        },
        "Route C": {
            "name": "Outer Ring Road",
            "base_time": data.route_c_time,
            "congestion_sensitivity": 0.7,
        }
    }

    route_scores = {}
    detailed_routes = []

    for route_id, info in corridors.items():
        # Congestion penalty scales dynamically with both predicted density and corridor sensitivity
        congestion_penalty = round(base_traffic_score * 5.0 * info["congestion_sensitivity"], 2)
        total_score = round(info["base_time"] + congestion_penalty, 2)
        route_scores[route_id] = total_score
        detailed_routes.append({
            "route": route_id,
            "name": info["name"],
            "base_travel_time": info["base_time"],
            "congestion_penalty": congestion_penalty,
            "total_route_score": total_score
        })

    # Recommended route has the lowest composite score
    detailed_routes.sort(key=lambda x: x["total_route_score"])
    recommended_route = detailed_routes[0]["route"]

    reason = (
        f"Recommended {recommended_route} ({detailed_routes[0]['name']}) with lowest composite score "
        f"({detailed_routes[0]['total_route_score']}) under predicted '{predicted_density}' traffic conditions."
    )

    return {
        "status": "success",
        "predicted_traffic_density": predicted_density,
        "recommended_route": recommended_route,
        "route_scores": route_scores,
        "recommendation_reason": reason,
        "detailed_routes": detailed_routes
    }