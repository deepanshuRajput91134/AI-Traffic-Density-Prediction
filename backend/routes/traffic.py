from fastapi import APIRouter

router = APIRouter(
    prefix="/traffic",
    tags=["Traffic"]
)


@router.get("/status")
def traffic_status():
    return {
        "status": "success",
        "message": "Traffic module is working"
    }


@router.get("/density")
def traffic_density():
    return {
        "location": "Delhi",
        "density": "High",
        "vehicle_count": 85
    }
from pydantic import BaseModel


class TrafficInput(BaseModel):
    vehicle_count: int
    average_speed: float
    road_capacity: int


@router.post("/predict")
def predict_traffic(data: TrafficInput):

    traffic_ratio = data.vehicle_count / data.road_capacity

    if traffic_ratio < 0.4:
        density = "Low"
    elif traffic_ratio < 0.7:
        density = "Medium"
    else:
        density = "High"

    return {
        "vehicle_count": data.vehicle_count,
        "average_speed": data.average_speed,
        "road_capacity": data.road_capacity,
        "traffic_density": density
    }