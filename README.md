# 🚦 AI Traffic Density Prediction & Smart City Management System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.9-orange?logo=scikitlearn)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow)

**An end-to-end AI-powered smart city traffic management system with ML-based density prediction, graph-based route optimization, SQLite analytics, and a real-time React dashboard.**

</div>

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Team](#-team)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Docker Setup](#-docker-setup)
- [API Reference](#-api-reference)
- [ML Model](#-ml-model)
- [Project Structure](#-project-structure)
- [Cloud Deployment](#-cloud-deployment)
- [Screenshots](#-screenshots)

---

## 🎯 Overview

This project simulates a **Smart City AI Traffic Management System** that:
- **Predicts traffic density** (Low / Medium / High) using a trained Random Forest classifier
- **Optimizes routes** using Dijkstra's algorithm with real-time traffic-aware edge penalties
- **Persists data** in SQLite for historical analytics
- **Demonstrates computer vision** vehicle counting via OpenCV
- **Provides a full React dashboard** for interactive monitoring

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **ML Prediction** | Random Forest model trained with 5-fold cross-validation on traffic data |
| 🗺️ **Smart Routing** | Dijkstra graph algorithm with traffic density penalty on edge weights |
| 📊 **Analytics Dashboard** | Real-time analytics from SQLite — prediction counts, route stats |
| 👁️ **Computer Vision** | OpenCV vehicle detection demo |
| 🧪 **Full Test Suite** | 13 passing tests across API, ML, Vision, and Analytics modules |
| 🐳 **Docker Ready** | Multi-stage Dockerfile + docker-compose for one-command startup |
| 📡 **REST API** | FastAPI with auto-generated Swagger docs at `/docs` |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                     │
│          (Vite + Tailwind — localhost:5173)          │
└────────────────────┬────────────────────────────────┘
                     │ HTTP / REST
┌────────────────────▼────────────────────────────────┐
│               FastAPI Backend (port 8000)            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ /traffic │ │ /routes  │ │/analytics│ │/vision │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘ │
│       │            │             │             │      │
│  ┌────▼──────┐ ┌───▼──────┐ ┌──▼──────┐ ┌───▼────┐ │
│  │ ML Model  │ │ Dijkstra │ │ SQLite  │ │OpenCV  │ │
│  │(sklearn)  │ │  Graph   │ │   DB    │ │  Stub  │ │
│  └───────────┘ └──────────┘ └─────────┘ └────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

**Backend**
- Python 3.12, FastAPI 0.141, Uvicorn 0.52
- Scikit-Learn 1.9 (Random Forest, Decision Tree, Gradient Boosting)
- SQLite (built-in), Joblib, Pandas, NumPy
- OpenCV 5.0

**Frontend**
- React 18, Vite 8.2
- JavaScript (ES2024)
- Fetch API (no external HTTP client needed)

**DevOps**
- Docker + Docker Compose
- GitHub Actions (CI-ready structure)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- pip, npm

### 1. Clone the repository
```bash
git clone https://github.com/deepanshuRajput91134/AI-Traffic-Density-Prediction.git
cd AI-Traffic-Density-Prediction
```

### 2. Setup Backend
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Train the ML Model (optional — model already included)
```bash
cd ai-model
python train_model.py
```

### 5. Run Tests
```bash
cd backend
python -m pytest tests/ -v
```

Open your browser:
- 🌐 **Frontend:** http://localhost:5173
- 📚 **API Docs:** http://localhost:8000/docs

---

## 🐳 Docker Setup

### One-command startup
```bash
# Build and start all services
docker-compose up --build

# Run in background (detached)
docker-compose up --build -d

# Stop everything
docker-compose down
```

Services:
- **Backend** → http://localhost:8000
- **Frontend** → http://localhost:5173

---

## 📡 API Reference

### Health Check
```
GET /health
```
Returns backend, database, and ML model status.

### Traffic Prediction
```
POST /traffic/predict
Content-Type: application/json

{
  "hour": 8,
  "day_of_week": 1,
  "vehicle_count": 150,
  "weather": "Clear",
  "road_type": "Highway"
}
```

### Route Optimization
```
GET /routes/smart-predict?start=City+Center&end=Airport
```

### Analytics Summary
```
GET /analytics/summary
```

### Vision Demo
```
GET /vision/vision-demo
```

Full interactive docs: **http://localhost:8000/docs**

---

## 🤖 ML Model

| Metric | Value |
|--------|-------|
| Algorithm | Random Forest Classifier |
| Cross-Validation | 5-Fold Stratified CV |
| Features | Hour, Day of Week, Vehicle Count, Weather, Road Type |
| Target | Traffic Density (Low / Medium / High) |
| Benchmark | Compared vs. Decision Tree, Logistic Regression, Gradient Boosting |

Model files:
- `ai-model/traffic_model.pkl` — Trained champion model
- `ai-model/label_encoder.pkl` — Fitted label encoder
- `ai-model/model_metadata.json` — CV scores and feature importance

---

## 📁 Project Structure

```
AI-Traffic-Density-Prediction/
├── backend/
│   ├── main.py                    # FastAPI app, CORS, health check
│   ├── routes/
│   │   ├── traffic.py             # /traffic endpoints
│   │   ├── routes.py              # /routes endpoints
│   │   ├── analytics.py           # /analytics endpoints
│   │   └── vision.py              # /vision endpoints
│   ├── app/
│   │   ├── database.py            # SQLite helpers
│   │   └── services/
│   │       └── routing_service.py # Dijkstra routing
│   └── tests/
│       ├── test_api.py
│       ├── test_ml.py
│       └── run_tests.py
├── frontend/
│   └── src/
│       ├── App.jsx                # Main dashboard UI
│       ├── App.css
│       └── services/api.js        # API wrappers
├── ai-model/
│   ├── train_model.py             # ML training pipeline
│   ├── traffic_model.pkl
│   └── label_encoder.pkl
├── computer-vision/
│   └── vehicle_detector.py        # OpenCV stub
├── database/
│   └── schema.sql                 # SQLite schema
├── Dockerfile                     # Multi-stage Docker build
├── docker-compose.yml             # Full stack compose
├── requirements.txt
└── README.md
```

---

## ☁️ Cloud Deployment

### Deploy on Render (Free Tier)
1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port 10000`
   - **Environment Variable:** `DB_PATH=/opt/render/project/src/traffic.db`

### Deploy on Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Deploy on AWS EC2
```bash
# On your EC2 instance
git clone https://github.com/deepanshuRajput91134/AI-Traffic-Density-Prediction.git
cd AI-Traffic-Density-Prediction
docker-compose up --build -d
```

---

## 🔮 Future Scope & Roadmap (Final Year)

- 📱 **Cross-Platform Mobile App:** Flutter / React Native commuter app for turn-by-turn AI navigation and real-time jam alerts.
- 🚑 **Emergency Vehicle Green Corridor:** Automated signal synchronization to clear lanes for ambulances and fire engines.
- 📡 **Real-Time IoT Sensors:** Live data ingestion from ultrasonic and inductive loop traffic sensors via WebSockets.
- 🗺️ **GIS & GPS Navigation:** Mapbox / OpenStreetMap integration with live traffic heatmaps.
- 👁️ **Edge AI Vision (YOLOv8):** CCTV stream vehicle classification and automated license plate recognition (ALPR).
- 🚦 **Adaptive Traffic Signals:** Dynamic traffic light phase switching using Reinforcement Learning.

---

## 👨‍💻 Team

<div align="center">

| 🟢 Deepanshu Kumar | 🟡 Kaushal Kumar | 🔴 Ayush Dwivedi | 🔵 Sachin Kashyap |
|:------------------:|:----------------:|:----------------:|:-----------------:|
| **ML Model & Dataset Preparation** | **Backend API & Integration** | **Frontend Development** | **Documentation & Presentation** |
| [@deepanshuRajput91134](https://github.com/deepanshuRajput91134)<br>*(Roll No: 2401431530021)* | Kaushal Kumar<br>*(Roll No: 2401431530036)* | Ayush Dwivedi<br>*(Roll No: 2401431530015)* | Sachin Kashyap<br>*(Roll No: 2401431530051)* |
| Trained & benchmarked RF, DT, LR, GB models. Curated dataset, feature engineering, cross-validation. | Built FastAPI backend, all REST endpoints, SQLite persistence, Dijkstra routing service. | Designed React dashboard with tabs, API integration, real-time data display. | Created project report, presentation slides, README and deployment documentation. |

</div>

**Institution:** B.Tech 3rd Year — Computer Science / AI
**Project Type:** Academic Minor Project

---


## 📄 License

This project is licensed under the MIT License.

---

<div align="center">
⭐ Star this repo if you found it helpful!
</div>