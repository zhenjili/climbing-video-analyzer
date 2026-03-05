# Climbing Video Analyzer

Upload climbing videos for AI-powered pose analysis and technique feedback.

## Features

- Pose detection with skeleton overlay using MediaPipe
- AI-powered climbing difficulty assessment (V-scale)
- Skill level evaluation and scoring
- Personalized improvement suggestions via Claude API

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for Redis)
- FFmpeg

### 1. Start Redis

docker compose up -d

### 2. Backend

cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your ANTHROPIC_API_KEY

# Start API server
uvicorn app.main:app --reload --port 8000

# Start Celery worker (separate terminal)
cd backend && source .venv/bin/activate
celery -A app.worker.celery_app worker --loglevel=info

### 3. Frontend

cd frontend
npm install
npm run dev

### 4. Open http://localhost:3000

## Architecture

Browser (Next.js) <-> FastAPI Backend <-> Celery + Redis
                                       |-> MediaPipe (pose estimation)
                                       |-> OpenCV (skeleton overlay)
                                       |-> Claude API (climbing analysis)

## Running Tests

cd backend && source .venv/bin/activate && pytest -v
