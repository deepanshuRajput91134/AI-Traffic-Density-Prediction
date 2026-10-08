# ─────────────────────────────────────────────────────────────
#  Stage 1 – Build the React frontend
# ─────────────────────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ─────────────────────────────────────────────────────────────
#  Stage 2 – Python backend + serve static frontend
# ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

# System dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/
COPY ai-model/ ./ai-model/
COPY computer-vision/ ./computer-vision/
COPY database/ ./database/

# Copy built frontend into a static/ folder the backend can serve
COPY --from=frontend-builder /app/frontend/dist ./static/

# Environment defaults (override via docker run -e or .env)
ENV DB_PATH=/app/data/traffic.db
ENV PYTHONUNBUFFERED=1

# Persist SQLite database in a named volume
VOLUME ["/app/data"]

EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
