"""
=============================================================================
Smart Cities AI Traffic Management System
Module: Persistence Layer - SQLite Database Manager
=============================================================================
Provides thread-safe persistence and query utilities for traffic telemetry,
historical predictions, and route optimization audits.
"""

import sqlite3
import json
import datetime
from pathlib import Path
from contextlib import contextmanager

BASE_DIR = Path(__file__).resolve().parents[2]
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "traffic_system.db"
SCHEMA_PATH = DB_DIR / "schema.sql"


def get_db_path() -> Path:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return DB_PATH


@contextmanager
def get_db_connection():
    """Context manager for SQLite connections with row dict factory."""
    conn = sqlite3.connect(get_db_path(), timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database tables using schema.sql and seed sample history if empty."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        if SCHEMA_PATH.exists():
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
        else:
            # Fallback inline schema creation
            conn.execute("""
                CREATE TABLE IF NOT EXISTS traffic_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    vehicle_count INTEGER NOT NULL,
                    average_speed REAL NOT NULL,
                    road_capacity INTEGER NOT NULL,
                    predicted_density TEXT NOT NULL,
                    congestion_ratio REAL NOT NULL,
                    source TEXT DEFAULT 'manual'
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS route_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    origin TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    recommended_route TEXT NOT NULL,
                    travel_time REAL NOT NULL,
                    route_score REAL NOT NULL,
                    traffic_density TEXT NOT NULL,
                    alternative_routes TEXT,
                    recommendation_reason TEXT
                );
            """)

        # Check if traffic_records has data, seed baseline demo history if empty
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM traffic_records")
        count = cursor.fetchone()["cnt"]

        if count == 0:
            sample_records = [
                (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5), 24, 45.0, 100, "Low", 24.0, "simulation"),
                (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=4), 38, 42.0, 100, "Low", 38.0, "simulation"),
                (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3), 62, 33.5, 100, "Medium", 62.0, "simulation"),
                (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2), 78, 27.0, 100, "Medium", 78.0, "simulation"),
                (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1), 95, 18.2, 100, "High", 95.0, "simulation"),
                (datetime.datetime.now(datetime.timezone.utc), 82, 22.4, 100, "High", 82.0, "simulation"),
            ]
            cursor.executemany("""
                INSERT INTO traffic_records (timestamp, vehicle_count, average_speed, road_capacity, predicted_density, congestion_ratio, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [(r[0].strftime("%Y-%m-%d %H:%M:%S"), r[1], r[2], r[3], r[4], r[5], r[6]) for r in sample_records])


def insert_traffic_record(vehicle_count: int, average_speed: float, road_capacity: int, predicted_density: str, congestion_ratio: float, source: str = "manual") -> int:
    """Insert a new traffic prediction record into the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO traffic_records (vehicle_count, average_speed, road_capacity, predicted_density, congestion_ratio, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (vehicle_count, average_speed, road_capacity, predicted_density, congestion_ratio, source))
        return cursor.lastrowid


def get_traffic_history(limit: int = 50):
    """Retrieve recent traffic telemetry and predictions."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, vehicle_count, average_speed, road_capacity, predicted_density, congestion_ratio, source
            FROM traffic_records
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = [dict(row) for row in cursor.fetchall()]
        return rows


def insert_route_record(origin: str, destination: str, recommended_route: str, travel_time: float, route_score: float, traffic_density: str, alternative_routes: list = None, recommendation_reason: str = "") -> int:
    """Insert a route optimization query record."""
    alt_json = json.dumps(alternative_routes) if alternative_routes else "[]"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO route_records (origin, destination, recommended_route, travel_time, route_score, traffic_density, alternative_routes, recommendation_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (origin, destination, recommended_route, travel_time, route_score, traffic_density, alt_json, recommendation_reason))
        return cursor.lastrowid


def get_route_history(limit: int = 20):
    """Retrieve recent route optimization recommendations."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, origin, destination, recommended_route, travel_time, route_score, traffic_density, alternative_routes, recommendation_reason
            FROM route_records
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        results = []
        for row in cursor.fetchall():
            item = dict(row)
            try:
                item["alternative_routes"] = json.loads(item["alternative_routes"])
            except Exception:
                item["alternative_routes"] = []
            results.append(item)
        return results


def get_presets():
    """Retrieve preset scenarios for demo / viva presentation."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, vehicle_count, average_speed, road_capacity, expected_density FROM simulation_presets ORDER BY id ASC")
        return [dict(row) for row in cursor.fetchall()]


def get_analytics_summary():
    """Aggregate high-level system analytics for dashboard charts."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Total predictions
        cursor.execute("SELECT COUNT(*) AS total FROM traffic_records")
        total = cursor.fetchone()["total"]

        # Density distribution
        cursor.execute("""
            SELECT predicted_density, COUNT(*) AS count
            FROM traffic_records
            GROUP BY predicted_density
        """)
        distribution = {row["predicted_density"]: row["count"] for row in cursor.fetchall()}
        for k in ["Low", "Medium", "High"]:
            distribution.setdefault(k, 0)

        # Averages
        cursor.execute("""
            SELECT AVG(vehicle_count) AS avg_vehicles, AVG(average_speed) AS avg_speed, AVG(congestion_ratio) AS avg_congestion
            FROM traffic_records
        """)
        avg_row = cursor.fetchone()
        avg_vehicles = round(avg_row["avg_vehicles"] or 0, 1)
        avg_speed = round(avg_row["avg_speed"] or 0, 1)
        avg_congestion = round(avg_row["avg_congestion"] or 0, 1)

        # Route stats
        cursor.execute("SELECT COUNT(*) AS total_routes FROM route_records")
        total_routes = cursor.fetchone()["total_routes"]

        return {
            "total_predictions": total,
            "density_distribution": distribution,
            "averages": {
                "vehicle_count": avg_vehicles,
                "average_speed_kmh": avg_speed,
                "congestion_ratio_percent": avg_congestion
            },
            "total_route_queries": total_routes
        }
