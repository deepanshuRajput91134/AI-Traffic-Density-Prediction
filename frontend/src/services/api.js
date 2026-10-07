/**
 * Smart Cities AI Traffic Management System
 * Frontend API Client Service
 */

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

export const api = {
  // System & Health
  getHealth: () => request("/health"),
  
  // Traffic Inference
  predictTraffic: (data) =>
    request("/traffic/predict", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Simulation
  simulateTraffic: (scenario = "random") =>
    request("/traffic/simulate", {
      method: "POST",
      body: JSON.stringify({ scenario }),
    }),

  // Model Info & Benchmarks
  getModelInfo: () => request("/traffic/model-info"),

  // Routes & Network
  getRoadNetwork: () => request("/routes/network"),
  
  optimizeGraphRoute: (data) =>
    request("/routes/graph-optimize", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  optimizeLegacyRoute: (data) =>
    request("/routes/optimize", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Analytics & History
  getAnalyticsSummary: () => request("/analytics/summary"),
  getPresets: () => request("/analytics/presets"),
  getTrafficHistory: (limit = 20) => request(`/analytics/history/traffic?limit=${limit}`),
  getRouteHistory: (limit = 10) => request(`/analytics/history/routes?limit=${limit}`),
};
