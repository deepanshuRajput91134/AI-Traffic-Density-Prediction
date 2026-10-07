from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
import joblib
import pandas as pd
from pathlib import Path
import os

from app.database import insert_route_record, get_route_history
from app.services.routing_service import (
    find_k_shortest_paths,
    get_city_network_metadata,
    CITY_NODES
)

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
# Schemas
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


class GraphRouteRequest(BaseModel):
    origin: str = Field(default="N1", description="Origin Node ID (e.g., N1 for Central City Center)")
    destination: str = Field(default="N6", description="Destination Node ID (e.g., N6 for International Airport)")
    density_overrides: Optional[Dict[str, str]] = Field(default=None, description="Optional road segment density overrides")


# =============================
# Helper
# =============================
def density_score(density: str) -> int:
    clean = str(density).strip().lower()
    if clean == "low":
        return 1
    elif clean == "medium":
        return 2
    elif clean == "high":
        return 3
    return 2


# =============================
# City Road Network Endpoint
# =============================
@router.get("/network")
def city_road_network():
    """Returns city road graph nodes and segments for Leaflet map visualization."""
    return {
        "status": "success",
        "network": get_city_network_metadata()
    }


# =============================
# Graph-Based Dijkstra Optimizer (Primary New Engine)
# =============================
@router.post("/graph-optimize")
def graph_optimize_route(req: GraphRouteRequest):
    """
    Computes optimal and alternative routes across the city graph network
    using Multi-Attribute Dijkstra Pathfinding.
    """
    try:
        routes = find_k_shortest_paths(
            origin=req.origin,
            destination=req.destination,
            k=3,
            density_overrides=req.density_overrides
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    if not routes:
        raise HTTPException(status_code=404, detail="No feasible route found between selected points.")

    best_route = routes[0]
    alternatives = routes[1:] if len(routes) > 1 else []

    # Persist in SQLite
    try:
        origin_name = CITY_NODES[req.origin]["name"]
        dest_name = CITY_NODES[req.destination]["name"]
        insert_route_record(
            origin=origin_name,
            destination=dest_name,
            recommended_route=best_route["route_name"],
            travel_time=best_route["estimated_travel_time"],
            route_score=best_route["route_score"],
            traffic_density=best_route["traffic_density"],
            alternative_routes=alternatives,
            recommendation_reason=best_route["reason"]
        )
    except Exception as db_err:
        print(f"Route log warning: {db_err}")

    return {
        "status": "success",
        "algorithm": "Dijkstra Multi-Attribute Shortest Path",
        "origin": CITY_NODES[req.origin],
        "destination": CITY_NODES[req.destination],
        "recommended_route": best_route,
        "alternative_routes": alternatives,
        "all_ranked_routes": routes
    }


# =============================
# Backward Compatible: Heuristic Route Optimization
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
        route["route_score"] = round(route["travel_time"] + (route["density_score"] * 5), 2)

    sorted_routes = sorted(routes, key=lambda x: x["route_score"])
    best_route = sorted_routes[0]

    reason = (
        f"Selected {best_route['route']} ({best_route['corridor_type']}) due to optimal balance "
        f"of travel time ({best_route['travel_time']} min) and {best_route['traffic_density']} traffic density "
        f"(Composite Score: {best_route['route_score']})."
    )

    try:
        insert_route_record(
            origin="Downtown Hub",
            destination="Airport Expressway",
            recommended_route=best_route["route"],
            travel_time=best_route["travel_time"],
            route_score=best_route["route_score"],
            traffic_density=best_route["traffic_density"],
            alternative_routes=sorted_routes[1:],
            recommendation_reason=reason
        )
    except Exception as e:
        print(f"Warning: Failed to log route: {e}")

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
# Backward Compatible: ML + Route Optimization
# =============================
@router.post("/smart-predict")
def smart_predict(data: SmartRouteInput):
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
    predicted_density = active_encoder.inverse_transform(prediction)[0]
    base_traffic_score = density_score(predicted_density)

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