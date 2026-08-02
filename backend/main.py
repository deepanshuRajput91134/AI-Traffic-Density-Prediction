from fastapi import FastAPI
from routes.traffic import router as traffic_router

app = FastAPI(
    title="AI Traffic Density Prediction API",
    description="Backend API for AI-Based Traffic Density Prediction and Route Optimization",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "AI Traffic Density Prediction API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


app.include_router(traffic_router)