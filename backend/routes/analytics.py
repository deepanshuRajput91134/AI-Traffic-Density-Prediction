from fastapi import APIRouter
from app.database import get_analytics_summary, get_presets, get_traffic_history, get_route_history

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics & History"]
)


@router.get("/summary")
def analytics_summary():
    """Retrieve high-level system analytics for dashboard charts and KPI cards."""
    data = get_analytics_summary()
    return {
        "status": "success",
        "data": data
    }


@router.get("/presets")
def simulation_presets():
    """Retrieve pre-configured viva demonstration scenarios."""
    presets = get_presets()
    return {
        "status": "success",
        "presets": presets
    }


@router.get("/history/traffic")
def traffic_history(limit: int = 50):
    """Retrieve historical traffic records."""
    records = get_traffic_history(limit=limit)
    return {
        "status": "success",
        "count": len(records),
        "records": records
    }


@router.get("/history/routes")
def routes_history(limit: int = 20):
    """Retrieve historical route optimization records."""
    records = get_route_history(limit=limit)
    return {
        "status": "success",
        "count": len(records),
        "records": records
    }
