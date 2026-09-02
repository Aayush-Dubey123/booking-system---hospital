# 🚀 Deployment Guide: Render (Backend) & Vercel (Frontend)

This guide walks you through deploying **CityCare Clinic** with zero hassle.

---

## 1. Backend Deployment (Render)

### Option A: Using Render Blueprint (`render.yaml`) — Recommended
1. Push your repository to GitHub / GitLab.
2. In [Render Dashboard](https://dashboard.render.com/), click **New +** ➡️ **Blueprint**.
3. Select your repository. Render will automatically detect `render.yaml`.
4. Fill in the required environment variables (secret keys, MongoDB Atlas URL, etc.) when prompted.
5. Click **Apply**. Render will build and deploy your FastAPI backend.

---

### Option B: Manual Web Service Setup on Render
1. In [Render Dashboard](https://dashboard.render.com/), click **New +** ➡️ **Web Service**.
2. Connect your GitHub repository.
3. Configure the following fields:
   - **Name**: `citycare-backend`
   - **Language / Runtime**: `Python`
   - **Region**: Select closest to your users (e.g. Frankfurt, Oregon, Singapore)
   - **Branch**: `main` (or your active branch)
   - **Root Directory**: `citycare-backend` *(or leave blank if using `--app-dir`)*
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn core.apis.api:app --host 0.0.0.0 --port $PORT
     ```
     *(Note: If Root Directory is left at repo root, use: `uvicorn core.apis.api:app --host 0.0.0.0 --port $PORT --app-dir citycare-backend`)*
   - **Health Check Path**: `/health`

4. **Add Environment Variables** under the **Environment** tab:
   | Variable Key | Value / Description |
   |---|---|
   | `MONGODB_URL` | Your MongoDB Atlas connection string (e.g., `mongodb+srv://<user>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority`) |
   | `DATABASE_NAME` | `citycare` |
   | `secret` | A secure random string for JWT authentication |
   | `algorithm` | `HS256` |
   | `api_key` | Google Gemini API key (for Chatbot) |
   | `API_KEY` | Google Gemini API key (same as above) |
   | `CLOUDINARY_CLOUD_NAME` | Your Cloudinary Cloud Name |
   | `CLOUDINARY_API_KEY` | Your Cloudinary API Key |
   | `CLOUDINARY_API_SECRET` | Your Cloudinary API Secret |
   | `TELEGRAM_BOT_TOKEN` | Your Telegram Bot Token (optional) |
   | `FRONTEND_URL` | Your Vercel frontend URL (e.g. `https://your-frontend.vercel.app`) |

5. Click **Deploy Web Service**.
6. Once deployed, copy your backend URL (e.g., `https://citycare-backend.onrender.com`).

---

## 2. Frontend Deployment (Vercel)

1. Go to [Vercel Dashboard](https://vercel.com/) and click **Add New...** ➡️ **Project**.
2. Import your GitHub repository.
3. Configure Project Settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click **Edit** and choose `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `dist` (default)
4. Under **Environment Variables**, add:
   | Variable Key | Value |
   |---|---|
   | `VITE_API_URL` | Your Render backend URL (e.g. `https://citycare-backend.onrender.com` — **no trailing slash**) |
5. Click **Deploy**.

> **Note on Client Routing**: `frontend/vercel.json` is already configured with rewrite rules so refreshing sub-routes (like `/login`, `/dashboard`, `/book`) will not return 404 errors.

---

## 3. Post-Deployment Verification

1. Open your Vercel URL (e.g. `https://your-app.vercel.app`).
2. Test patient registration or login.
3. Verify that requests hit your Render backend without CORS errors (CORS is configured to accept all `*.vercel.app` domains automatically, plus any domain specified in `FRONTEND_URL`).

---

## 4. Local Development

To run both backend and frontend locally in the future:
```bash
python dev.py
```
- Backend runs at: [http://127.0.0.1:8000](http://127.0.0.1:8000) (Interactive Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs))
- Frontend runs at: [http://localhost:5173](http://localhost:5173)
