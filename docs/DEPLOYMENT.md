# ☁️ Cloud Deployment Guide

## Option 1 — Render.com (Recommended for beginners, Free Tier)

### Steps:
1. Push your code to GitHub (already done ✅)
2. Go to https://render.com → Sign up / Login
3. Click **New +** → **Web Service**
4. Connect your GitHub repository: `AI-Traffic-Density-Prediction`
5. Configure:
   - **Name:** `ai-traffic-backend`
   - **Root Directory:** *(leave empty)*
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port 10000`
6. Add Environment Variables:
   - `DB_PATH` = `/opt/render/project/src/traffic.db`
7. Click **Deploy**

Your API will be live at: `https://ai-traffic-backend.onrender.com`

---

## Option 2 — Railway.app

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Go to your project
cd /Users/deepanshu/Documents/AI-Traffic-Density-Prediction

# 4. Initialize
railway init

# 5. Deploy
railway up
```

Add a `railway.json` in root:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

---

## Option 3 — Docker on Any VPS / AWS EC2

```bash
# SSH into your server
ssh ubuntu@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu

# Clone your repo
git clone https://github.com/deepanshuRajput91134/AI-Traffic-Density-Prediction.git
cd AI-Traffic-Density-Prediction

# Start everything
docker-compose up --build -d

# Check status
docker-compose ps
docker-compose logs -f backend
```

Open ports in your security group:
- Port **8000** (Backend API)
- Port **5173** (Frontend)

---

## Option 4 — Vercel (Frontend only) + Render (Backend)

### Frontend on Vercel:
1. Go to https://vercel.com
2. Import your GitHub repo
3. Set **Root Directory** to `frontend`
4. Add env variable:
   - `VITE_API_URL` = `https://your-render-backend.onrender.com`
5. Deploy

### Update frontend API base URL:
Edit `frontend/src/services/api.js`:
```js
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

---

## 🔑 Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PATH` | `traffic.db` | SQLite database file path |
| `VITE_API_URL` | `http://localhost:8000` | Backend URL for frontend |
| `PORT` | `8000` | Server port (auto-set by cloud providers) |
