-- ============================================================================
-- Smart Cities AI Traffic Management System
-- Database Schema: SQLite DDL
-- ============================================================================

-- Table 1: Historical Traffic Predictions and Sensor Telemetry
CREATE TABLE IF NOT EXISTS traffic_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    vehicle_count INTEGER NOT NULL,
    average_speed REAL NOT NULL,
    road_capacity INTEGER NOT NULL,
    predicted_density TEXT NOT NULL,
    congestion_ratio REAL NOT NULL,
    source TEXT DEFAULT 'manual' -- 'manual', 'simulation', 'vision'
);

-- Index for efficient time-series and density queries
CREATE INDEX IF NOT EXISTS idx_traffic_timestamp ON traffic_records(timestamp);
CREATE INDEX IF NOT EXISTS idx_traffic_density ON traffic_records(predicted_density);

-- Table 2: Route Optimization Inquiries and Recommendation Logs
CREATE TABLE IF NOT EXISTS route_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    recommended_route TEXT NOT NULL,
    travel_time REAL NOT NULL,
    route_score REAL NOT NULL,
    traffic_density TEXT NOT NULL,
    alternative_routes TEXT, -- JSON string storing 2nd & 3rd alternatives
    recommendation_reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_route_timestamp ON route_records(timestamp);

-- Table 3: Preset Demonstration Scenarios for Viva & Evaluation
CREATE TABLE IF NOT EXISTS simulation_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    vehicle_count INTEGER NOT NULL,
    average_speed REAL NOT NULL,
    road_capacity INTEGER NOT NULL,
    expected_density TEXT NOT NULL
);

-- Seed initial preset scenarios if not already present
INSERT OR IGNORE INTO simulation_presets (id, name, description, vehicle_count, average_speed, road_capacity, expected_density)
VALUES 
    (1, 'Off-Peak Midnight Flow', 'Low density night traffic with free-flow speed on all arterials', 18, 48.0, 100, 'Low'),
    (2, 'Midday Regular City Flow', 'Moderate traffic volume around business districts with standard urban speeds', 52, 34.0, 100, 'Medium'),
    (3, 'Morning Peak Rush Hour', 'Severe congestion bottleneck on main arterial highway with low crawling speeds', 94, 16.5, 100, 'High'),
    (4, 'Rain / Incident Bottleneck', 'Reduced capacity due to rain with heavy queuing and traffic diversion required', 88, 19.0, 120, 'High');
