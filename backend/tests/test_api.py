"""
=============================================================================
Smart Cities AI Traffic Management System
Module: Automated Test Suite - Backend Endpoints & Routing
=============================================================================
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from main import root, health_check
from routes.traffic import (
    predict_traffic,
    simulate_traffic,
    TrafficInput,
    SimulationTriggerInput
)
from routes.routes import (
    graph_optimize_route,
    optimize_route,
    GraphRouteRequest,
    RouteInput
)
from routes.analytics import analytics_summary
from routes.vision import demo_vision_feed
from app.database import init_db


def setup_database():
    init_db()


def test_root_endpoint():
    res = root()
    assert res["status"] == "online"
    assert "version" in res


def test_health_check_endpoint():
    res = health_check()
    assert res["backend"] == "online"
    assert res["database"] == "connected"
    assert res["ml_model"] == "loaded"


def test_traffic_prediction_success():
    payload = TrafficInput(
        vehicle_count=20,
        average_speed=45.0,
        road_capacity=100
    )
    res = predict_traffic(payload)
    assert res["status"] == "success"
    assert res["predicted_traffic_density"] == "Low"
    assert res["congestion_ratio_percent"] == 20.0


def test_traffic_prediction_boundary_high():
    payload = TrafficInput(
        vehicle_count=95,
        average_speed=18.0,
        road_capacity=100
    )
    res = predict_traffic(payload)
    assert res["status"] == "success"
    assert res["predicted_traffic_density"] == "High"
    assert res["congestion_ratio_percent"] == 95.0


def test_traffic_simulation_endpoint():
    trigger = SimulationTriggerInput(scenario="night")
    res = simulate_traffic(trigger)
    assert res["status"] == "success"
    assert res["data_tag"] == "Demo / Simulated Traffic Data"
    assert "predicted_traffic_density" in res


def test_graph_route_optimization():
    req = GraphRouteRequest(origin="N1", destination="N6")
    res = graph_optimize_route(req)
    assert res["status"] == "success"
    assert "recommended_route" in res
    assert len(res["all_ranked_routes"]) >= 1


def test_legacy_route_optimization_route_b_recommended():
    # User's exact baseline test case:
    # Route A: time=35, High
    # Route B: time=28, Medium
    # Route C: time=42, Low
    # Expected: Route B
    req = RouteInput(
        route_a_time=35.0,
        route_a_density="High",
        route_b_time=28.0,
        route_b_density="Medium",
        route_c_time=42.0,
        route_c_density="Low"
    )
    res = optimize_route(req)
    assert res["status"] == "success"
    assert res["recommended_route"] == "Route B"


def test_analytics_summary_endpoint():
    res = analytics_summary()
    assert res["status"] == "success"
    assert "total_predictions" in res["data"]


def test_vision_demo_feed():
    res = demo_vision_feed(target_vehicles=40)
    assert res["status"] == "success"
    assert res["camera_metadata"]["detected_count"] == 40
    assert "ai_prediction" in res
