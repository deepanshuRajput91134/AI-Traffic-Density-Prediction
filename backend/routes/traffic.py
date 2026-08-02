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