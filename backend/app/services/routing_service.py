"""
=============================================================================
Smart Cities AI Traffic Management System
Module: Routing Service - Graph-Based Dijkstra Optimizer
=============================================================================
Provides graph topology modeling, dynamic congestion weighting, and
multi-path Dijkstra pathfinding for urban road networks.
"""

import heapq
from typing import Dict, List, Tuple, Any

# ---------------------------------------------------------------------------
# City Road Network Definition
# ---------------------------------------------------------------------------
CITY_NODES = {
    "N1": {"id": "N1", "name": "Central City Center", "lat": 28.6139, "lng": 77.2090, "type": "Hub"},
    "N2": {"id": "N2", "name": "Cyber Tech Park", "lat": 28.6304, "lng": 77.2177, "type": "Commercial"},
    "N3": {"id": "N3", "name": "North Metro Junction", "lat": 28.6500, "lng": 77.2200, "type": "Transit"},
    "N4": {"id": "N4", "name": "South Ring Interchange", "lat": 28.5800, "lng": 77.2100, "type": "Interchange"},
    "N5": {"id": "N5", "name": "East Logistics Corridor", "lat": 28.6250, "lng": 77.2500, "type": "Industrial"},
    "N6": {"id": "N6", "name": "International Airport", "lat": 28.5562, "lng": 77.1000, "type": "Airport"},
}

ROAD_SEGMENTS = [
    {
        "id": "E1",
        "name": "Main Arterial Avenue",
        "u": "N1", "v": "N2",
        "distance_km": 4.5,
        "free_flow_speed_kmh": 50,
        "road_type": "Arterial",
        "default_density": "High",
        "color": "#ef4444"
    },
    {
        "id": "E2",
        "name": "Central Boulevard",
        "u": "N1", "v": "N3",
        "distance_km": 5.2,
        "free_flow_speed_kmh": 45,
        "road_type": "Boulevard",
        "default_density": "Medium",
        "color": "#f59e0b"
    },
    {
        "id": "E3",
        "name": "Tech Metro Connector",
        "u": "N2", "v": "N3",
        "distance_km": 3.8,
        "free_flow_speed_kmh": 60,
        "road_type": "Avenue",
        "default_density": "Low",
        "color": "#10b981"
    },
    {
        "id": "E4",
        "name": "South Expressway Link",
        "u": "N1", "v": "N4",
        "distance_km": 6.0,
        "free_flow_speed_kmh": 70,
        "road_type": "Expressway",
        "default_density": "Medium",
        "color": "#f59e0b"
    },
    {
        "id": "E5",
        "name": "Cyber East Bypass",
        "u": "N2", "v": "N5",
        "distance_km": 7.5,
        "free_flow_speed_kmh": 80,
        "road_type": "Bypass Expressway",
        "default_density": "Low",
        "color": "#10b981"
    },
    {
        "id": "E6",
        "name": "Outer North Ring",
        "u": "N3", "v": "N5",
        "distance_km": 6.8,
        "free_flow_speed_kmh": 65,
        "road_type": "Ring Road",
        "default_density": "Medium",
        "color": "#f59e0b"
    },
    {
        "id": "E7",
        "name": "Airport Direct Highway",
        "u": "N4", "v": "N6",
        "distance_km": 8.2,
        "free_flow_speed_kmh": 90,
        "road_type": "Highway",
        "default_density": "Low",
        "color": "#10b981"
    },
    {
        "id": "E8",
        "name": "East Airport Parkway",
        "u": "N5", "v": "N6",
        "distance_km": 11.0,
        "free_flow_speed_kmh": 75,
        "road_type": "Parkway",
        "default_density": "Low",
        "color": "#10b981"
    },
    {
        "id": "E9",
        "name": "Cross-City Tunnel",
        "u": "N2", "v": "N4",
        "distance_km": 5.5,
        "free_flow_speed_kmh": 55,
        "road_type": "Tunnel",
        "default_density": "High",
        "color": "#ef4444"
    },
]


def calculate_edge_cost(edge: dict, density_override: str = None) -> Tuple[float, float, float]:
    """
    Calculate dynamic travel time and composite cost for a road segment.
    Returns: (travel_time_min, congestion_penalty, composite_cost)
    """
    density = (density_override or edge.get("current_density") or edge["default_density"]).capitalize()
    
    # Speed degradation under congestion
    speed_factor = 1.0
    congestion_penalty = 1.0

    if density == "Medium":
        speed_factor = 0.70
        congestion_penalty = 6.0
    elif density == "High":
        speed_factor = 0.40
        congestion_penalty = 15.0

    effective_speed = max(10.0, edge["free_flow_speed_kmh"] * speed_factor)
    travel_time_min = round((edge["distance_km"] / effective_speed) * 60, 2)

    # Multi-attribute cost: Travel Time (50%) + Distance (20%) + Congestion Penalty (30%)
    composite_cost = round(travel_time_min + (edge["distance_km"] * 0.3) + congestion_penalty, 2)
    return travel_time_min, congestion_penalty, composite_cost


def build_adjacency_graph(density_overrides: Dict[str, str] = None) -> Dict[str, List[dict]]:
    """Build bidirectional adjacency list representing the city road network."""
    overrides = density_overrides or {}
    graph = {node_id: [] for node_id in CITY_NODES}

    for edge in ROAD_SEGMENTS:
        density = overrides.get(edge["id"], edge["default_density"])
        t_time, penalty, cost = calculate_edge_cost(edge, density)
        
        edge_data_fwd = {
            "edge_id": edge["id"],
            "name": edge["name"],
            "to": edge["v"],
            "distance_km": edge["distance_km"],
            "road_type": edge["road_type"],
            "density": density,
            "travel_time_min": t_time,
            "cost": cost
        }
        graph[edge["u"]].append(edge_data_fwd)

        edge_data_rev = {
            "edge_id": edge["id"],
            "name": edge["name"],
            "to": edge["u"],
            "distance_km": edge["distance_km"],
            "road_type": edge["road_type"],
            "density": density,
            "travel_time_min": t_time,
            "cost": cost
        }
        graph[edge["v"]].append(edge_data_rev)

    return graph


def find_k_shortest_paths(origin: str, destination: str, k: int = 3, density_overrides: Dict[str, str] = None) -> List[dict]:
    """
    Compute up to k alternative paths using Yen's style penalty-based Dijkstra.
    Returns: List of formatted route candidate objects.
    """
    if origin not in CITY_NODES or destination not in CITY_NODES:
        raise ValueError(f"Invalid origin '{origin}' or destination '{destination}'")

    if origin == destination:
        return [{
            "rank": 1,
            "label": "Direct Location",
            "path_nodes": [origin],
            "total_distance_km": 0.0,
            "total_time_min": 0.0,
            "route_score": 0.0,
            "dominant_density": "Low",
            "segments": []
        }]

    graph = build_adjacency_graph(density_overrides)
    routes_found = []

    # Priority queue for Dijkstra: (cost, current_node, path_nodes, path_edges)
    pq = [(0.0, origin, [origin], [])]
    seen_paths = set()

    while pq and len(routes_found) < k:
        curr_cost, curr_node, path_nodes, path_edges = heapq.heappop(pq)

        if curr_node == destination:
            path_tuple = tuple(path_nodes)
            if path_tuple not in seen_paths:
                seen_paths.add(path_tuple)
                
                # Calculate metrics for the complete path
                total_dist = sum(e["distance_km"] for e in path_edges)
                total_time = sum(e["travel_time_min"] for e in path_edges)
                densities = [e["density"] for e in path_edges]
                dominant_density = max(set(densities), key=densities.count)

                routes_found.append({
                    "path_nodes": path_nodes,
                    "path_names": [CITY_NODES[n]["name"] for n in path_nodes],
                    "total_distance_km": round(total_dist, 2),
                    "total_time_min": round(total_time, 2),
                    "route_score": round(curr_cost, 2),
                    "dominant_density": dominant_density,
                    "segments": path_edges
                })
            continue

        for edge in graph[curr_node]:
            neighbor = edge["to"]
            if neighbor not in path_nodes:  # Avoid cycle in path
                heapq.heappush(pq, (
                    curr_cost + edge["cost"],
                    neighbor,
                    path_nodes + [neighbor],
                    path_edges + [edge]
                ))

    # Format into ranked primary + alternatives
    ranked_output = []
    labels = ["Best Recommended Route", "Alternative Route 1", "Alternative Route 2"]

    for i, r in enumerate(routes_found):
        label = labels[i] if i < len(labels) else f"Alternative Route {i}"
        
        # Explainable reasoning
        if i == 0:
            reason = (
                f"Selected as optimal path via {r['path_names'][1] if len(r['path_names']) > 2 else 'direct link'} "
                f"offering lowest overall travel time ({r['total_time_min']} min) and minimal congestion delay."
            )
        else:
            reason = (
                f"Alternative option traversing {r['path_names'][1] if len(r['path_names']) > 2 else 'corridor'} "
                f"with {r['dominant_density'].lower()} traffic ({r['total_time_min']} min, {r['total_distance_km']} km)."
            )

        ranked_output.append({
            "rank": i + 1,
            "label": label,
            "route_name": f"Route {'ABC'[i] if i < 3 else str(i+1)}: {' → '.join(r['path_names'])}",
            "path_nodes": r["path_nodes"],
            "path_names": r["path_names"],
            "total_distance_km": r["total_distance_km"],
            "estimated_travel_time": r["total_time_min"],
            "route_score": r["route_score"],
            "traffic_density": r["dominant_density"],
            "reason": reason,
            "segments": r["segments"]
        })

    return ranked_output


def get_city_network_metadata():
    """Return the entire road graph topology for frontend Leaflet map rendering."""
    return {
        "nodes": list(CITY_NODES.values()),
        "edges": ROAD_SEGMENTS
    }
