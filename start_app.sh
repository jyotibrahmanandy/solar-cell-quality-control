#!/bin/bash
# ==========================================================
# HelioScan AI — Solar Cell Quality Control Startup Script
# Starts FastAPI Backend (Port 8000) & React Vite Dev Server (Port 5173)
# ==========================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "☀️ Starting HelioScan AI Platform..."

# 1. Start FastAPI Backend
echo "⚡ Starting FastAPI Backend on http://127.0.0.1:8000..."
./.venv/bin/python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# 2. Wait for backend to warm up
sleep 2

# 3. Start React Vite Frontend
echo "🚀 Starting React Frontend on http://localhost:5173..."
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo "=========================================================="
echo "✅ HelioScan AI is now online!"
echo "   - Web App UI:       http://localhost:5173"
echo "   - Backend API Docs: http://127.0.0.1:8000/docs"
echo "=========================================================="

trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" SIGINT SIGTERM
wait
