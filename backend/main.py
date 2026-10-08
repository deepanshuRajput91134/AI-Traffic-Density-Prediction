import datetime
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, get_db_connection
from routes.traffic import router as traffic_router, get_model_and_encoder
from routes.routes import router as routes_router
from routes.analytics import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables and pre-load ML model
    print("[STARTUP] Initializing SQLite database...")
    init_db()
    print("[STARTUP] Pre-loading ML model into memory...")
    try:
        get_model_and_encoder()
        print("[STARTUP] ML Model loaded successfully!")
    except Exception as e:
        print(f"[STARTUP WARNING] Model not loaded: {e}")
    yield
    # Shutdown
    print("[SHUTDOWN] Traffic API service stopped.")


app = FastAPI(
    title="Smart City AI Traffic Management API",
    description="Backend API for AI-Based Traffic Density Prediction and Route Optimization",
    version="2.0.0",
    lifespan=lifespan
)

# -------------------------------------------------------------
# CORS Middleware
# -------------------------------------------------------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits localhost dev servers reliably
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Smart City AI Traffic Management System API is active",
        "status": "online",
        "version": "2.0.0",
        "documentation": "/docs"
    }


@app.get("/health")
def health_check():
    """Real health check verifying backend, database, and ML model status."""
    # Check DB
    db_status = "connected"
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1").fetchone()
    except Exception:
        db_status = "error"

    # Check ML Model
    ml_status = "loaded"
    try:
        m, _ = get_model_and_encoder()
        if m is None:
            ml_status = "unloaded"
    except Exception:
        ml_status = "error"

    return {
        "status": "healthy" if (db_status == "connected" and ml_status == "loaded") else "degraded",
        "backend": "online",
        "database": db_status,
        "ml_model": ml_status,
        "frontend": "online",
        "version": "2.0.0",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }


# Mount modular routers
from routes.vision import router as vision_router

app.include_router(traffic_router)
app.include_router(routes_router)
app.include_router(analytics_router)
app.include_router(vision_router)