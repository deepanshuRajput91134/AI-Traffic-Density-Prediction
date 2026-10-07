import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.traffic import router as traffic_router
from routes.routes import router as routes_router

app = FastAPI(
    title="AI Traffic Density Prediction API",
    description="Backend API for AI-Based Traffic Density Prediction and Route Optimization - Smart Cities",
    version="1.0.0"
)

# -------------------------------------------------------------
# CORS Middleware: Enable frontend communication safely
# -------------------------------------------------------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "AI Traffic Density Prediction API is running",
        "status": "success",
        "docs_url": "/docs"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "backend": "online",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }


# Mount application routers
app.include_router(traffic_router)
app.include_router(routes_router)