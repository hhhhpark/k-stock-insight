#!/bin/bash
# K-Stock Insight Backend 실행 스크립트
# 이 스크립트는 항상 backend 디렉토리에서 uvicorn을 실행합니다

echo "🚀 Starting K-Stock Insight Backend..."
echo "📁 Moving to backend directory..."

cd backend && uvicorn main:app --reload --port 8000

echo "✅ Backend started on http://localhost:8000" 