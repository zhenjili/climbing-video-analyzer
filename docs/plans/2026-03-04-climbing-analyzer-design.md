# Climbing Video Analyzer - Design Document

## Overview

A web app where users upload climbing videos. The system performs pose estimation (skeleton detection), overlays skeletons on the original video, and provides:
1. Climbing route difficulty assessment
2. User climbing skill level evaluation
3. Improvement suggestions

## Architecture

```
Browser (Next.js + React)
    ↕ HTTP / Polling
Next.js API Routes (BFF)
    ↕ HTTP
Python FastAPI Service
    ├── MediaPipe Pose Estimation
    ├── OpenCV Video Processing (skeleton overlay)
    └── Claude API (climbing analysis)
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 14, React, Tailwind CSS |
| Backend | Python FastAPI, Celery |
| Pose Estimation | MediaPipe Pose |
| Video Processing | OpenCV, FFmpeg |
| AI Analysis | Claude API (claude-sonnet-4-20250514) |
| Task Queue | Redis + Celery |
| File Storage | Local filesystem (MVP) |

## Core Flow

1. **Upload**: User uploads video → Next.js forwards to FastAPI → stored locally
2. **Process** (async via Celery):
   - MediaPipe Pose detects 33 body keypoints per frame
   - OpenCV draws skeleton overlay on original video
   - Extract key data: joint angles, center of gravity trajectory, movement sequence
3. **Analyze**: Send skeleton data + key frame screenshots to Claude API → get difficulty, skill level, suggestions
4. **Return**: Frontend polls task status → displays processed video + analysis report

## Frontend Pages

- **Home**: Upload area (drag & drop) + instructions
- **Processing**: Progress bar + status (uploading → analyzing → complete)
- **Results**: Video player (skeleton overlay) + analysis report cards

## Key Decisions

- **No user auth** for MVP — track tasks via session/token
- **Async processing** — return task ID, frontend polls for progress
- **Server-side pose estimation** — more stable, supports longer videos
- **LLM-based analysis** — fast to develop, good quality results
