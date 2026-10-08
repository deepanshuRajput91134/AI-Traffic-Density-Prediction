"""
=============================================================================
Smart Cities AI Traffic Management System
Module: Test Runner (Zero-Dependency Python Test Execution)
=============================================================================
"""

import sys
import traceback
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# Import test functions
from tests.test_api import (
    setup_database,
    test_root_endpoint,
    test_health_check_endpoint,
    test_traffic_prediction_success,
    test_traffic_prediction_boundary_high,
    test_traffic_simulation_endpoint,
    test_graph_route_optimization,
    test_legacy_route_optimization_route_b_recommended,
    test_analytics_summary_endpoint,
    test_vision_demo_feed
)

from tests.test_ml import (
    test_artifacts_exist,
    test_metadata_content,
    test_model_inference_low_traffic,
    test_model_inference_high_traffic
)

tests = [
    ("ML: Artifacts Existence Check", test_artifacts_exist),
    ("ML: Model Metadata & Benchmark Verification", test_metadata_content),
    ("ML: Low Density Inference Validation", test_model_inference_low_traffic),
    ("ML: High Density Inference Validation", test_model_inference_high_traffic),
    ("API: Root Endpoint Probe", test_root_endpoint),
    ("API: Health Diagnostics & Observability", test_health_check_endpoint),
    ("API: Valid Traffic Density Prediction", test_traffic_prediction_success),
    ("API: Boundary Validation (High Congestion Limit)", test_traffic_prediction_boundary_high),
    ("API: Traffic Simulation Generator", test_traffic_simulation_endpoint),
    ("API: Graph Dijkstra Multi-Path Route Optimizer", test_graph_route_optimization),
    ("API: Legacy Heuristic Route B Benchmark", test_legacy_route_optimization_route_b_recommended),
    ("API: Database Analytics Aggregator", test_analytics_summary_endpoint),
    ("Vision: Frame Extraction & Camera Telemetry", test_vision_demo_feed)
]

def main():
    print("=" * 70)
    print("       SMART CITY AI TRAFFIC SYSTEM: AUTOMATED TEST SUITE")
    print("=" * 70)
    setup_database()
    
    passed = 0
    failed = 0

    for name, fn in tests:
        try:
            fn()
            print(f"  [PASS] {name:<60}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name:<60}")
            traceback.print_exc()
            failed += 1

    print("=" * 70)
    print(f"Test Summary: Total={len(tests)} | Passed={passed} | Failed={failed}")
    print("=" * 70)

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
