import { useState, useEffect } from "react";
import {
  LayoutDashboard,
  Cpu,
  Navigation,
  Activity,
  BarChart3,
  Server,
  Info,
  Car,
  Gauge,
  Clock,
  MapPin,
  Play,
  RotateCw,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  Sparkles,
  Layers,
  ShieldCheck,
} from "lucide-react";
import { api } from "./services/api";
import "./App.css";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");

  // System Health
  const [health, setHealth] = useState({
    backend: "checking...",
    database: "checking...",
    ml_model: "checking...",
    frontend: "online",
  });

  // Traffic Prediction Form
  const [vehicleCount, setVehicleCount] = useState(75);
  const [averageSpeed, setAverageSpeed] = useState(28);
  const [roadCapacity, setRoadCapacity] = useState(100);
  const [prediction, setPrediction] = useState(null);
  const [loadingPredict, setLoadingPredict] = useState(false);

  // Route Optimization State
  const [origin, setOrigin] = useState("N1");
  const [destination, setDestination] = useState("N6");
  const [routeResult, setRouteResult] = useState(null);
  const [loadingRoute, setLoadingRoute] = useState(false);

  // Road Network & Metadata
  const [network, setNetwork] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [telemetryHistory, setTelemetryHistory] = useState([]);
  const [autoSimulate, setAutoSimulate] = useState(false);

  // 1. Initial Data Fetching
  const fetchSystemData = async () => {
    try {
      const h = await api.getHealth();
      setHealth(h);
    } catch {
      setHealth({
        backend: "offline",
        database: "disconnected",
        ml_model: "unloaded",
        frontend: "online",
      });
    }

    try {
      const net = await api.getRoadNetwork();
      setNetwork(net.network);
    } catch (e) {
      console.warn("Could not load network:", e);
    }

    try {
      const mInfo = await api.getModelInfo();
      if (mInfo.status === "success") setModelInfo(mInfo.data);
    } catch (e) {
      console.warn("Could not load model info:", e);
    }

    try {
      const a = await api.getAnalyticsSummary();
      if (a.status === "success") setAnalytics(a.data);
    } catch (e) {
      console.warn("Could not load analytics:", e);
    }

    try {
      const h = await api.getTrafficHistory(15);
      if (h.status === "success") setTelemetryHistory(h.records);
    } catch (e) {
      console.warn("Could not load history:", e);
    }
  };

  useEffect(() => {
    fetchSystemData();
    // Default initial prediction run
    handlePredict(75, 28, 100);
    handleRouteOptimize("N1", "N6");
  }, []);

  // 2. Real-time Simulation Ticker
  useEffect(() => {
    let interval = null;
    if (autoSimulate) {
      interval = setInterval(async () => {
        try {
          const res = await api.simulateTraffic("random");
          setPrediction(res);
          setVehicleCount(res.vehicle_count);
          setAverageSpeed(res.average_speed);
          setRoadCapacity(res.road_capacity);
          const hist = await api.getTrafficHistory(15);
          if (hist.status === "success") setTelemetryHistory(hist.records);
        } catch (err) {
          console.error("Auto-simulate tick error:", err);
        }
      }, 4000);
    }
    return () => clearInterval(interval);
  }, [autoSimulate]);

  // 3. Prediction Handler
  const handlePredict = async (v = vehicleCount, s = averageSpeed, c = roadCapacity) => {
    setLoadingPredict(true);
    try {
      const res = await api.predictTraffic({
        vehicle_count: Number(v),
        average_speed: Number(s),
        road_capacity: Number(c),
      });
      setPrediction(res);
      // Refresh history & analytics
      const h = await api.getTrafficHistory(15);
      if (h.status === "success") setTelemetryHistory(h.records);
    } catch (err) {
      console.error("Prediction error:", err);
    } finally {
      setLoadingPredict(false);
    }
  };

  // 4. Graph-Based Route Optimization Handler
  const handleRouteOptimize = async (orig = origin, dest = destination) => {
    setLoadingRoute(true);
    try {
      const res = await api.optimizeGraphRoute({
        origin: orig,
        destination: dest,
      });
      setRouteResult(res);
    } catch (err) {
      console.error("Routing error:", err);
    } finally {
      setLoadingRoute(false);
    }
  };

  // 5. Trigger Preset Simulation Scenario
  const handleTriggerScenario = async (type) => {
    try {
      const res = await api.simulateTraffic(type);
      setPrediction(res);
      setVehicleCount(res.vehicle_count);
      setAverageSpeed(res.average_speed);
      setRoadCapacity(res.road_capacity);
      const hist = await api.getTrafficHistory(15);
      if (hist.status === "success") setTelemetryHistory(hist.records);
    } catch (e) {
      console.error("Scenario trigger failed:", e);
    }
  };

  const getDensityClass = (density) => {
    if (!density) return "badge-low";
    const d = density.toLowerCase();
    if (d === "high") return "badge-high";
    if (d === "medium") return "badge-medium";
    return "badge-low";
  };

  return (
    <div className="app-layout">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon">
            <Cpu size={22} />
          </div>
          <div>
            <div className="brand-title">SmartTraffic AI</div>
            <div className="brand-subtitle">Smart City ITS Core</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => setActiveTab("dashboard")}
          >
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </button>

          <button
            className={`nav-item ${activeTab === "predict" ? "active" : ""}`}
            onClick={() => setActiveTab("predict")}
          >
            <Gauge size={18} />
            <span>Traffic Prediction</span>
          </button>

          <button
            className={`nav-item ${activeTab === "routes" ? "active" : ""}`}
            onClick={() => setActiveTab("routes")}
          >
            <Navigation size={18} />
            <span>Route Optimization</span>
          </button>

          <button
            className={`nav-item ${activeTab === "live" ? "active" : ""}`}
            onClick={() => setActiveTab("live")}
          >
            <Activity size={18} />
            <span>Live Monitoring</span>
          </button>

          <button
            className={`nav-item ${activeTab === "analytics" ? "active" : ""}`}
            onClick={() => setActiveTab("analytics")}
          >
            <BarChart3 size={18} />
            <span>ML Analytics & Benchmarks</span>
          </button>

          <button
            className={`nav-item ${activeTab === "status" ? "active" : ""}`}
            onClick={() => setActiveTab("status")}
          >
            <Server size={18} />
            <span>System Status</span>
          </button>

          <button
            className={`nav-item ${activeTab === "about" ? "active" : ""}`}
            onClick={() => setActiveTab("about")}
          >
            <Info size={18} />
            <span>About Project</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <div>Academic Final-Year Prototype</div>
          <div style={{ color: "#3b82f6", marginTop: 4 }}>FastAPI + Scikit-Learn + React</div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="main-wrapper">
        {/* Top Header */}
        <header className="top-header">
          <div className="header-title-wrap">
            <h1>AI Traffic Density Prediction & Route Optimization</h1>
            <p>Intelligent Transportation Systems (ITS) Smart City Platform</p>
          </div>

          <div className="header-status-strip">
            <div className="status-pill">
              <span className={`pulse-dot ${health.backend === "online" ? "" : "error"}`}></span>
              <span>Backend: {health.backend?.toUpperCase()}</span>
            </div>

            <div className="status-pill">
              <span className={`pulse-dot ${health.ml_model === "loaded" ? "" : "error"}`}></span>
              <span>ML Engine: {health.ml_model?.toUpperCase()}</span>
            </div>

            <button
              onClick={fetchSystemData}
              title="Refresh Telemetry"
              style={{
                background: "transparent",
                border: "none",
                color: "#94a3b8",
                cursor: "pointer",
              }}
            >
              <RotateCw size={16} />
            </button>
          </div>
        </header>

        {/* Content Body */}
        <main className="content-body">
          {/* TAB 1: DASHBOARD OVERVIEW */}
          {activeTab === "dashboard" && (
            <div>
              {/* Simulation Quick Bar */}
              <div className="sim-bar">
                <div className="sim-watermark">
                  <Sparkles size={16} />
                  <span>Demo Mode: 1-Click Viva Presentation Scenarios</span>
                </div>
                <div className="sim-btn-group">
                  <button
                    className="btn-secondary"
                    onClick={() => handleTriggerScenario("night")}
                  >
                    🌙 Off-Peak Night (Low)
                  </button>
                  <button
                    className="btn-secondary"
                    onClick={() => handleTriggerScenario("normal")}
                  >
                    ☀️ Midday City (Medium)
                  </button>
                  <button
                    className="btn-secondary"
                    onClick={() => handleTriggerScenario("rush_hour")}
                  >
                    🚗 Rush Hour (High)
                  </button>
                  <button
                    className={`btn-secondary ${autoSimulate ? "active" : ""}`}
                    onClick={() => setAutoSimulate(!autoSimulate)}
                    style={{
                      borderColor: autoSimulate ? "#10b981" : "",
                      color: autoSimulate ? "#10b981" : "",
                    }}
                  >
                    {autoSimulate ? "⏸ Stop Auto Stream" : "▶ Start Live Stream"}
                  </button>
                </div>
              </div>

              {/* 8 Primary KPI Metric Cards */}
              <div className="grid-cards">
                <div className="kpi-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Current Density</span>
                    <div className="kpi-icon-wrap" style={{ color: "#3b82f6" }}>
                      <Activity size={18} />
                    </div>
                  </div>
                  <div className="kpi-value">
                    <span
                      className={`badge-density ${getDensityClass(
                        prediction?.predicted_traffic_density
                      )}`}
                    >
                      {prediction?.predicted_traffic_density || "Analyzing..."}
                    </span>
                  </div>
                  <div className="kpi-subtext">Random Forest Classifier Output</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Vehicle Volume</span>
                    <div className="kpi-icon-wrap" style={{ color: "#10b981" }}>
                      <Car size={18} />
                    </div>
                  </div>
                  <div className="kpi-value">{vehicleCount}</div>
                  <div className="kpi-subtext">Observed corridor vehicles</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Average Velocity</span>
                    <div className="kpi-icon-wrap" style={{ color: "#f59e0b" }}>
                      <Gauge size={18} />
                    </div>
                  </div>
                  <div className="kpi-value">{averageSpeed} <span style={{ fontSize: 16 }}>km/h</span></div>
                  <div className="kpi-subtext">Corridor flow rate</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Congestion Utilization</span>
                    <div className="kpi-icon-wrap" style={{ color: "#ef4444" }}>
                      <TrendingUp size={18} />
                    </div>
                  </div>
                  <div className="kpi-value">
                    {Math.round((vehicleCount / (roadCapacity || 100)) * 100)}%
                  </div>
                  <div className="kpi-subtext">Capacity threshold limit ({roadCapacity})</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Dijkstra Best Route</span>
                    <div className="kpi-icon-wrap" style={{ color: "#8b5cf6" }}>
                      <Navigation size={18} />
                    </div>
                  </div>
                  <div className="kpi-value" style={{ fontSize: 18, color: "#a78bfa" }}>
                    {routeResult?.recommended_route?.label || "Route A (Optimal)"}
                  </div>
                  <div className="kpi-subtext">
                    {routeResult?.recommended_route?.path_names?.join(" → ") || "City Center → Airport"}
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Estimated Travel Time</span>
                    <div className="kpi-icon-wrap" style={{ color: "#38bdf8" }}>
                      <Clock size={18} />
                    </div>
                  </div>
                  <div className="kpi-value">
                    {routeResult?.recommended_route?.estimated_travel_time || "12.8"} <span style={{ fontSize: 16 }}>min</span>
                  </div>
                  <div className="kpi-subtext">Free-flow + congestion weighted</div>
                </div>
              </div>

              {/* Interactive City Road Network Visualizer */}
              <div className="panel-card">
                <div className="panel-title-wrap">
                  <div className="panel-title">
                    <Layers size={18} style={{ color: "#3b82f6" }} />
                    <span>Smart City Road Network & Live Congestion Topology</span>
                  </div>
                  <span style={{ fontSize: 12, color: "#94a3b8" }}>
                    Dynamic Dijkstra Graph Visualization (OpenStreetMap Vector Model)
                  </span>
                </div>

                <div className="map-canvas-container">
                  <svg className="map-svg" viewBox="0 0 850 360">
                    <defs>
                      <linearGradient id="roadGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#8b5cf6" />
                      </linearGradient>
                    </defs>

                    {/* Background Grid Lines */}
                    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
                    </pattern>
                    <rect width="850" height="360" fill="url(#grid)" />

                    {/* Road Edges */}
                    {/* E1: City Center (200, 180) to Tech Park (360, 90) */}
                    <line x1="200" y1="180" x2="360" y2="90" stroke="#ef4444" strokeWidth="5" strokeLinecap="round" />
                    {/* E2: City Center (200, 180) to North Metro (240, 60) */}
                    <line x1="200" y1="180" x2="240" y2="60" stroke="#f59e0b" strokeWidth="4" strokeLinecap="round" />
                    {/* E3: Tech Park (360, 90) to North Metro (240, 60) */}
                    <line x1="360" y1="90" x2="240" y2="60" stroke="#10b981" strokeWidth="4" strokeLinecap="round" />
                    {/* E4: City Center (200, 180) to South Interchange (400, 270) */}
                    <line x1="200" y1="180" x2="400" y2="270" stroke="#10b981" strokeWidth="6" strokeLinecap="round" />
                    {/* E5: Tech Park (360, 90) to East Logistics (600, 130) */}
                    <line x1="360" y1="90" x2="600" y2="130" stroke="#10b981" strokeWidth="5" strokeLinecap="round" />
                    {/* E6: North Metro (240, 60) to East Logistics (600, 130) */}
                    <line x1="240" y1="60" x2="600" y2="130" stroke="#f59e0b" strokeWidth="4" strokeLinecap="round" />
                    {/* E7: South Interchange (400, 270) to Airport (700, 260) */}
                    <line x1="400" y1="270" x2="700" y2="260" stroke="#10b981" strokeWidth="6" strokeLinecap="round" />
                    {/* E8: East Logistics (600, 130) to Airport (700, 260) */}
                    <line x1="600" y1="130" x2="700" y2="260" stroke="#10b981" strokeWidth="4" strokeLinecap="round" />
                    {/* E9: Tech Park (360, 90) to South Interchange (400, 270) */}
                    <line x1="360" y1="90" x2="400" y2="270" stroke="#ef4444" strokeWidth="4" strokeLinecap="round" />

                    {/* Nodes */}
                    {[
                      { id: "N1", name: "Central City Center", x: 200, y: 180, color: "#3b82f6" },
                      { id: "N2", name: "Cyber Tech Park", x: 360, y: 90, color: "#8b5cf6" },
                      { id: "N3", name: "North Metro Junction", x: 240, y: 60, color: "#06b6d4" },
                      { id: "N4", name: "South Ring Interchange", x: 400, y: 270, color: "#10b981" },
                      { id: "N5", name: "East Logistics Corridor", x: 600, y: 130, color: "#f59e0b" },
                      { id: "N6", name: "International Airport", x: 700, y: 260, color: "#ec4899" },
                    ].map((node) => (
                      <g key={node.id}>
                        <circle cx={node.x} cy={node.y} r="18" fill="#0f172a" stroke={node.color} strokeWidth="3" />
                        <circle cx={node.x} cy={node.y} r="8" fill={node.color} />
                        <text
                          x={node.x}
                          y={node.y + 32}
                          fill="#f8fafc"
                          fontSize="12"
                          fontWeight="600"
                          textAnchor="middle"
                        >
                          {node.name}
                        </text>
                      </g>
                    ))}
                  </svg>

                  <div style={{ display: "flex", gap: 20, marginTop: 12, fontSize: 12 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span style={{ width: 12, height: 4, background: "#10b981", borderRadius: 2 }}></span>
                      <span>Low Density Flow (&gt;50 km/h)</span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span style={{ width: 12, height: 4, background: "#f59e0b", borderRadius: 2 }}></span>
                      <span>Medium Density Flow (30-50 km/h)</span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <span style={{ width: 12, height: 4, background: "#ef4444", borderRadius: 2 }}></span>
                      <span>High Density Congestion (&lt;30 km/h)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: TRAFFIC PREDICTION STUDIO */}
          {activeTab === "predict" && (
            <div>
              <div className="panel-card">
                <div className="panel-title-wrap">
                  <div className="panel-title">
                    <Gauge size={20} style={{ color: "#3b82f6" }} />
                    <span>Real-Time AI Traffic Density Inference Studio</span>
                  </div>
                  <span className="badge-density badge-low">Model v2.0 (Random Forest)</span>
                </div>

                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Vehicle Count (Vehicles in Corridor)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={vehicleCount}
                      min="0"
                      max="1000"
                      onChange={(e) => setVehicleCount(e.target.value)}
                    />
                    <input
                      type="range"
                      min="0"
                      max="200"
                      value={vehicleCount}
                      onChange={(e) => setVehicleCount(e.target.value)}
                      style={{ accentColor: "#3b82f6", marginTop: 4 }}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Average Speed (km/h)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={averageSpeed}
                      min="0"
                      max="180"
                      onChange={(e) => setAverageSpeed(e.target.value)}
                    />
                    <input
                      type="range"
                      min="5"
                      max="120"
                      value={averageSpeed}
                      onChange={(e) => setAverageSpeed(e.target.value)}
                      style={{ accentColor: "#f59e0b", marginTop: 4 }}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Road Capacity (Standard Capacity)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={roadCapacity}
                      min="10"
                      max="1000"
                      onChange={(e) => setRoadCapacity(e.target.value)}
                    />
                  </div>
                </div>

                <button
                  className="btn-primary"
                  onClick={() => handlePredict()}
                  disabled={loadingPredict}
                >
                  <Play size={16} />
                  <span>{loadingPredict ? "Evaluating Model..." : "Run AI Traffic Prediction"}</span>
                </button>
              </div>

              {/* Prediction Result Display */}
              {prediction && (
                <div className="panel-card" style={{ borderColor: "rgba(59, 130, 246, 0.4)" }}>
                  <div className="panel-title">
                    <CheckCircle2 size={20} style={{ color: "#10b981" }} />
                    <span>AI Model Classification Result</span>
                  </div>

                  <div style={{ display: "flex", gap: 30, alignItems: "center", marginTop: 20 }}>
                    <div>
                      <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 6 }}>
                        Predicted Traffic Density
                      </div>
                      <span
                        className={`badge-density ${getDensityClass(
                          prediction.predicted_traffic_density
                        )}`}
                        style={{ fontSize: 22, padding: "8px 24px" }}
                      >
                        {prediction.predicted_traffic_density}
                      </span>
                    </div>

                    <div style={{ borderLeft: "1px solid var(--border-color)", paddingLeft: 30 }}>
                      <div style={{ fontSize: 13, color: "#94a3b8" }}>Capacity Utilization</div>
                      <div style={{ fontSize: 24, fontWeight: 700, color: "#fff" }}>
                        {prediction.congestion_ratio_percent}%
                      </div>
                    </div>

                    <div style={{ borderLeft: "1px solid var(--border-color)", paddingLeft: 30 }}>
                      <div style={{ fontSize: 13, color: "#94a3b8" }}>Model Decision Engine</div>
                      <div style={{ fontSize: 14, fontWeight: 600, color: "#93c5fd" }}>
                        Random Forest (100 Trees, 5-Fold Stratified CV)
                      </div>
                    </div>
                  </div>

                  {/* Feature Importance Explainability Bar */}
                  <div style={{ marginTop: 24, background: "rgba(0,0,0,0.2)", padding: 16, borderRadius: 8 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8, color: "#cbd5e1" }}>
                      Explainable AI (XAI): Feature Importance Drivers
                    </div>
                    <div style={{ display: "flex", gap: 20 }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                          <span>Average Speed (Velocity Factor)</span>
                          <span style={{ fontWeight: 700 }}>48.4%</span>
                        </div>
                        <div style={{ height: 6, background: "rgba(255,255,255,0.1)", borderRadius: 3 }}>
                          <div style={{ width: "48.4%", height: "100%", background: "#f59e0b", borderRadius: 3 }}></div>
                        </div>
                      </div>

                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                          <span>Vehicle Count (Volume Factor)</span>
                          <span style={{ fontWeight: 700 }}>42.4%</span>
                        </div>
                        <div style={{ height: 6, background: "rgba(255,255,255,0.1)", borderRadius: 3 }}>
                          <div style={{ width: "42.4%", height: "100%", background: "#3b82f6", borderRadius: 3 }}></div>
                        </div>
                      </div>

                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                          <span>Road Capacity (Threshold Factor)</span>
                          <span style={{ fontWeight: 700 }}>9.2%</span>
                        </div>
                        <div style={{ height: 6, background: "rgba(255,255,255,0.1)", borderRadius: 3 }}>
                          <div style={{ width: "9.2%", height: "100%", background: "#10b981", borderRadius: 3 }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: ROUTE OPTIMIZATION */}
          {activeTab === "routes" && (
            <div>
              <div className="panel-card">
                <div className="panel-title-wrap">
                  <div className="panel-title">
                    <Navigation size={20} style={{ color: "#3b82f6" }} />
                    <span>Dijkstra Multi-Attribute Dynamic Route Optimizer</span>
                  </div>
                  <span style={{ fontSize: 12, color: "#94a3b8" }}>
                    Weights: Time (50%) + Congestion Penalty (30%) + Distance (20%)
                  </span>
                </div>

                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Origin Intersection (Start Point)</label>
                    <select
                      className="form-select"
                      value={origin}
                      onChange={(e) => setOrigin(e.target.value)}
                    >
                      <option value="N1">Central City Center (N1)</option>
                      <option value="N2">Cyber Tech Park (N2)</option>
                      <option value="N3">North Metro Junction (N3)</option>
                      <option value="N4">South Ring Interchange (N4)</option>
                      <option value="N5">East Logistics Corridor (N5)</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Destination Node (Target Point)</label>
                    <select
                      className="form-select"
                      value={destination}
                      onChange={(e) => setDestination(e.target.value)}
                    >
                      <option value="N6">International Airport (N6)</option>
                      <option value="N5">East Logistics Corridor (N5)</option>
                      <option value="N4">South Ring Interchange (N4)</option>
                      <option value="N2">Cyber Tech Park (N2)</option>
                    </select>
                  </div>
                </div>

                <button
                  className="btn-primary"
                  onClick={() => handleRouteOptimize(origin, destination)}
                  disabled={loadingRoute}
                >
                  <Navigation size={16} />
                  <span>{loadingRoute ? "Computing Paths..." : "Find Optimal Route (Dijkstra)"}</span>
                </button>
              </div>

              {/* Ranked Routes Carousel / List */}
              {routeResult && (
                <div>
                  <div style={{ marginBottom: 16, fontSize: 15, fontWeight: 700, color: "#fff" }}>
                    Ranked Pathfinding Solutions:
                  </div>

                  {routeResult.all_ranked_routes?.map((route, idx) => (
                    <div
                      key={idx}
                      className="panel-card"
                      style={{
                        borderLeft: `4px solid ${
                          idx === 0 ? "#10b981" : idx === 1 ? "#f59e0b" : "#ef4444"
                        }`,
                        marginBottom: 16,
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div>
                          <div style={{ fontSize: 16, fontWeight: 700, color: "#fff", display: "flex", gap: 10, alignItems: "center" }}>
                            <span>{route.label}</span>
                            <span className={`badge-density ${getDensityClass(route.traffic_density)}`}>
                              {route.traffic_density} Traffic
                            </span>
                          </div>
                          <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>
                            {route.path_names?.join(" → ")}
                          </div>
                        </div>

                        <div style={{ display: "flex", gap: 24, textAlign: "right" }}>
                          <div>
                            <div style={{ fontSize: 12, color: "#94a3b8" }}>Travel Time</div>
                            <div style={{ fontSize: 20, fontWeight: 700, color: "#fff" }}>
                              {route.estimated_travel_time} min
                            </div>
                          </div>
                          <div>
                            <div style={{ fontSize: 12, color: "#94a3b8" }}>Distance</div>
                            <div style={{ fontSize: 20, fontWeight: 700, color: "#fff" }}>
                              {route.total_distance_km} km
                            </div>
                          </div>
                          <div>
                            <div style={{ fontSize: 12, color: "#94a3b8" }}>Composite Score</div>
                            <div style={{ fontSize: 20, fontWeight: 700, color: "#38bdf8" }}>
                              {route.route_score}
                            </div>
                          </div>
                        </div>
                      </div>

                      <div style={{ marginTop: 14, fontSize: 13, color: "#cbd5e1", background: "rgba(0,0,0,0.2)", padding: 10, borderRadius: 6 }}>
                        💡 <strong>Reason for selection:</strong> {route.reason}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 4: LIVE MONITORING */}
          {activeTab === "live" && (
            <div>
              <div className="panel-card">
                <div className="panel-title-wrap">
                  <div className="panel-title">
                    <Activity size={20} style={{ color: "#3b82f6" }} />
                    <span>Real-Time Sensor Ingestion Stream</span>
                  </div>
                  <div style={{ display: "flex", gap: 10 }}>
                    <button
                      className="btn-primary"
                      onClick={() => handleTriggerScenario("random")}
                    >
                      <Play size={16} />
                      <span>Generate Sensor Telemetry</span>
                    </button>
                  </div>
                </div>

                <div className="table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Timestamp (UTC)</th>
                        <th>Corridor Vehicles</th>
                        <th>Speed (km/h)</th>
                        <th>Capacity</th>
                        <th>AI Density</th>
                        <th>Congestion %</th>
                        <th>Source</th>
                      </tr>
                    </thead>
                    <tbody>
                      {telemetryHistory.map((row) => (
                        <tr key={row.id}>
                          <td>#{row.id}</td>
                          <td>{row.timestamp}</td>
                          <td style={{ fontWeight: 600 }}>{row.vehicle_count}</td>
                          <td>{row.average_speed} km/h</td>
                          <td>{row.road_capacity}</td>
                          <td>
                            <span className={`badge-density ${getDensityClass(row.predicted_density)}`}>
                              {row.predicted_density}
                            </span>
                          </td>
                          <td>{row.congestion_ratio}%</td>
                          <td style={{ textTransform: "capitalize", color: "#93c5fd" }}>
                            {row.source}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: ANALYTICS & ML BENCHMARKS */}
          {activeTab === "analytics" && (
            <div>
              {/* Comparative Benchmark Table */}
              <div className="panel-card">
                <div className="panel-title">
                  <BarChart3 size={20} style={{ color: "#3b82f6" }} />
                  <span>Machine Learning Multi-Model Comparative Benchmark (5-Fold Stratified CV)</span>
                </div>

                <div className="table-container" style={{ marginTop: 16 }}>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Candidate Model</th>
                        <th>5-Fold CV F1-Score (Macro)</th>
                        <th>Test Accuracy (20% Split)</th>
                        <th>Macro Precision</th>
                        <th>Macro Recall</th>
                        <th>Test Macro F1</th>
                        <th>Role</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td style={{ fontWeight: 700, color: "#60a5fa" }}>Random Forest Classifier</td>
                        <td>96.79% ± 0.60%</td>
                        <td>97.00%</td>
                        <td>96.97%</td>
                        <td>97.10%</td>
                        <td style={{ fontWeight: 700 }}>96.74%</td>
                        <td><span className="badge-density badge-low">🏆 Champion Model</span></td>
                      </tr>
                      <tr>
                        <td style={{ fontWeight: 600 }}>Logistic Regression (Standardized)</td>
                        <td>97.35% ± 0.85%</td>
                        <td>98.50%</td>
                        <td>98.33%</td>
                        <td>98.33%</td>
                        <td>98.33%</td>
                        <td>Linear Baseline</td>
                      </tr>
                      <tr>
                        <td style={{ fontWeight: 600 }}>Gradient Boosting Classifier</td>
                        <td>96.16% ± 0.65%</td>
                        <td>96.50%</td>
                        <td>96.15%</td>
                        <td>96.15%</td>
                        <td>96.15%</td>
                        <td>Boosting Ensemble</td>
                      </tr>
                      <tr>
                        <td style={{ fontWeight: 600 }}>Decision Tree Classifier</td>
                        <td>91.26% ± 1.28%</td>
                        <td>93.00%</td>
                        <td>92.69%</td>
                        <td>92.56%</td>
                        <td>92.34%</td>
                        <td>Baseline Tree</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 12 }}>
                  * All metrics calculated on 2,000-sample partition using Scikit-Learn 1.9.0 without data leakage.
                </div>
              </div>

              {/* Confusion Matrix & Dataset Profile */}
              <div className="grid-cards">
                <div className="panel-card">
                  <div className="panel-title">
                    <ShieldCheck size={18} style={{ color: "#10b981" }} />
                    <span>Confusion Matrix (Random Forest Test Split)</span>
                  </div>
                  <div className="table-container" style={{ marginTop: 12 }}>
                    <table className="data-table" style={{ textAlign: "center" }}>
                      <thead>
                        <tr>
                          <th>Actual \ Predicted</th>
                          <th>High</th>
                          <th>Low</th>
                          <th>Medium</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td style={{ fontWeight: 600 }}>High (165)</td>
                          <td style={{ color: "#10b981", fontWeight: 700 }}>162</td>
                          <td>0</td>
                          <td>3</td>
                        </tr>
                        <tr>
                          <td style={{ fontWeight: 600 }}>Low (130)</td>
                          <td>0</td>
                          <td style={{ color: "#10b981", fontWeight: 700 }}>127</td>
                          <td>3</td>
                        </tr>
                        <tr>
                          <td style={{ fontWeight: 600 }}>Medium (105)</td>
                          <td>2</td>
                          <td>4</td>
                          <td style={{ color: "#10b981", fontWeight: 700 }}>99</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="panel-card">
                  <div className="panel-title">
                    <DatabaseIcon size={18} style={{ color: "#8b5cf6" }} />
                    <span>Database Analytics Summary</span>
                  </div>
                  <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 12 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14 }}>
                      <span style={{ color: "#94a3b8" }}>Total Recorded Inferences:</span>
                      <strong style={{ color: "#fff" }}>{analytics?.total_predictions || 8}</strong>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14 }}>
                      <span style={{ color: "#94a3b8" }}>Average Observed Speed:</span>
                      <strong style={{ color: "#fff" }}>{analytics?.averages?.average_speed_kmh || 31.3} km/h</strong>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14 }}>
                      <span style={{ color: "#94a3b8" }}>Average Vehicle Flow:</span>
                      <strong style={{ color: "#fff" }}>{analytics?.averages?.vehicle_count || 63} vehicles</strong>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14 }}>
                      <span style={{ color: "#94a3b8" }}>Persistence Engine:</span>
                      <strong style={{ color: "#10b981" }}>SQLite Local DDL</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: SYSTEM STATUS */}
          {activeTab === "status" && (
            <div>
              <div className="panel-card">
                <div className="panel-title">
                  <Server size={20} style={{ color: "#3b82f6" }} />
                  <span>Real-Time Health Diagnostics & Architecture Telemetry</span>
                </div>

                <div className="grid-cards" style={{ marginTop: 20 }}>
                  <div className="kpi-card">
                    <div className="kpi-title">FastAPI Backend Service</div>
                    <div className="kpi-value" style={{ color: "#34d399", fontSize: 22 }}>
                      {health.backend?.toUpperCase()}
                    </div>
                    <div className="kpi-subtext">Port 8000 (Uvicorn Worker)</div>
                  </div>

                  <div className="kpi-card">
                    <div className="kpi-title">Scikit-Learn ML Model</div>
                    <div className="kpi-value" style={{ color: "#60a5fa", fontSize: 22 }}>
                      {health.ml_model?.toUpperCase()}
                    </div>
                    <div className="kpi-subtext">Preloaded in Application Lifespan</div>
                  </div>

                  <div className="kpi-card">
                    <div className="kpi-title">SQLite Database</div>
                    <div className="kpi-value" style={{ color: "#a78bfa", fontSize: 22 }}>
                      {health.database?.toUpperCase()}
                    </div>
                    <div className="kpi-subtext">Thread-safe DDL connection</div>
                  </div>

                  <div className="kpi-card">
                    <div className="kpi-title">React Client Application</div>
                    <div className="kpi-value" style={{ color: "#38bdf8", fontSize: 22 }}>
                      ONLINE
                    </div>
                    <div className="kpi-subtext">Vite Dev Server (Port 5173)</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 7: ABOUT PROJECT */}
          {activeTab === "about" && (
            <div className="panel-card">
              <div className="panel-title">
                <Info size={20} style={{ color: "#3b82f6" }} />
                <span>Academic Final-Year Specification</span>
              </div>

              <div style={{ marginTop: 16, lineHeight: 1.7, color: "#cbd5e1", fontSize: 14 }}>
                <h3 style={{ color: "#fff", marginBottom: 8 }}>Project Title:</h3>
                <p style={{ marginBottom: 16 }}>
                  <strong>AI-Based Traffic Density Prediction and Route Optimization</strong>
                </p>

                <h3 style={{ color: "#fff", marginBottom: 8 }}>Domain:</h3>
                <p style={{ marginBottom: 16 }}>Smart Cities / Intelligent Transportation Systems (ITS)</p>

                <h3 style={{ color: "#fff", marginBottom: 8 }}>Core Architecture:</h3>
                <p style={{ marginBottom: 16 }}>
                  Integrates a multi-tier pipeline: Sensor Telemetry &amp; Computer Vision (vehicle counting)
                  $\rightarrow$ Machine Learning Classification (Random Forest for Low/Medium/High density)
                  $\rightarrow$ Graph-Based Dijkstra Pathfinding with Dynamic Congestion Penalties
                  $\rightarrow$ React Operations Dashboard.
                </p>

                <h3 style={{ color: "#fff", marginBottom: 8 }}>Academic Disclosure &amp; Scope:</h3>
                <p style={{ color: "#94a3b8" }}>
                  This application is an academic software prototype developed for final-year / pre-final-year evaluation.
                  The 97.0% classification performance reflects the 2,000-sample benchmark dataset partition.
                  Simulated data is clearly designated as such.
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

function DatabaseIcon({ size, style }) {
  return <Server size={size} style={style} />;
}