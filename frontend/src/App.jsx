import { useState } from "react";
import "./App.css";

function App() {
  const [vehicleCount, setVehicleCount] = useState(45);
  const [averageSpeed, setAverageSpeed] = useState(36);
  const [roadCapacity, setRoadCapacity] = useState(100);

  const [routeA, setRouteA] = useState(35);
  const [routeB, setRouteB] = useState(25);
  const [routeC, setRouteC] = useState(30);

  const [traffic, setTraffic] = useState(null);
  const [recommendedRoute, setRecommendedRoute] = useState(null);

  const predictTraffic = () => {
    let result;

    if (vehicleCount >= 70 || averageSpeed < 30) {
      result = "High";
    } else if (vehicleCount >= 40 || averageSpeed < 40) {
      result = "Medium";
    } else {
      result = "Low";
    }

    setTraffic(result);

    const routes = [
      { name: "Route A", time: Number(routeA) },
      { name: "Route B", time: Number(routeB) },
      { name: "Route C", time: Number(routeC) },
    ];

    const best = routes.reduce((a, b) =>
      a.time < b.time ? a : b
    );

    setRecommendedRoute(best);
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>🚦 AI Traffic Smart Dashboard</h1>
          <p>Traffic Density Prediction & Route Optimization</p>
        </div>

        <div className="status">
          <span className="dot"></span>
          Backend Ready
        </div>
      </header>

      <main className="container">
        <section className="hero">
          <h2>Intelligent Traffic Management System</h2>
          <p>
            Predict traffic density and find the best route using
            AI-based traffic analysis.
          </p>
        </section>

        <div className="grid">
          {/* Traffic Prediction */}
          <section className="card">
            <h2>🚗 Traffic Prediction</h2>

            <label>Vehicle Count</label>
            <input
              type="number"
              value={vehicleCount}
              onChange={(e) => setVehicleCount(e.target.value)}
            />

            <label>Average Speed (km/h)</label>
            <input
              type="number"
              value={averageSpeed}
              onChange={(e) => setAverageSpeed(e.target.value)}
            />

            <label>Road Capacity</label>
            <input
              type="number"
              value={roadCapacity}
              onChange={(e) => setRoadCapacity(e.target.value)}
            />

            <button onClick={predictTraffic}>
              Predict Traffic
            </button>
          </section>

          {/* Route Optimization */}
          <section className="card">
            <h2>🛣️ Route Optimization</h2>

            <label>Route A Time (minutes)</label>
            <input
              type="number"
              value={routeA}
              onChange={(e) => setRouteA(e.target.value)}
            />

            <label>Route B Time (minutes)</label>
            <input
              type="number"
              value={routeB}
              onChange={(e) => setRouteB(e.target.value)}
            />

            <label>Route C Time (minutes)</label>
            <input
              type="number"
              value={routeC}
              onChange={(e) => setRouteC(e.target.value)}
            />

            <button onClick={predictTraffic}>
              Optimize Route
            </button>
          </section>
        </div>

        {/* Results */}
        <section className="results">
          <div className="result-card">
            <h3>Traffic Density</h3>

            {traffic ? (
              <div className={`traffic ${traffic.toLowerCase()}`}>
                {traffic}
              </div>
            ) : (
              <div className="waiting">Waiting...</div>
            )}
          </div>

          <div className="result-card">
            <h3>Recommended Route</h3>

            {recommendedRoute ? (
              <>
                <div className="route-name">
                  {recommendedRoute.name}
                </div>
                <p>
                  Estimated Time:{" "}
                  <strong>{recommendedRoute.time} min</strong>
                </p>
              </>
            ) : (
              <div className="waiting">Waiting...</div>
            )}
          </div>
        </section>

        {/* System Information */}
        <section className="info">
          <h2>📊 System Overview</h2>

          <div className="info-grid">
            <div>
              <strong>AI Model</strong>
              <span>Random Forest</span>
            </div>

            <div>
              <strong>Backend</strong>
              <span>FastAPI</span>
            </div>

            <div>
              <strong>Frontend</strong>
              <span>React + Vite</span>
            </div>

            <div>
              <strong>Prediction</strong>
              <span>Low / Medium / High</span>
            </div>
          </div>
        </section>
      </main>

      <footer>
        AI-Based Traffic Density Prediction and Route Optimization
      </footer>
    </div>
  );
}

export default App;