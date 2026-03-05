# Climbing Video Analyzer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a web app that accepts climbing videos, performs pose estimation with skeleton overlay, and returns AI-powered climbing analysis.

**Architecture:** Next.js frontend communicates with a Python FastAPI backend. FastAPI uses Celery+Redis for async video processing. MediaPipe extracts pose data, OpenCV overlays skeletons, and Claude API generates climbing analysis.

**Tech Stack:** Next.js 14, React, Tailwind CSS, Python 3.11+, FastAPI, Celery, Redis, MediaPipe, OpenCV, FFmpeg, Anthropic SDK

---

## Project Structure

```
climbing/
├── frontend/                 # Next.js app
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # Home/upload page
│   │   │   ├── layout.tsx
│   │   │   ├── processing/[taskId]/page.tsx
│   │   │   └── results/[taskId]/page.tsx
│   │   ├── components/
│   │   │   ├── VideoUploader.tsx
│   │   │   ├── ProcessingStatus.tsx
│   │   │   ├── VideoPlayer.tsx
│   │   │   └── AnalysisReport.tsx
│   │   └── lib/
│   │       └── api.ts                # API client
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app
│   │   ├── config.py                 # Settings
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── tasks.py              # Upload & status endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── pose_estimator.py     # MediaPipe wrapper
│   │   │   ├── video_processor.py    # OpenCV skeleton overlay
│   │   │   └── climbing_analyzer.py  # Claude API analysis
│   │   ├── worker/
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py         # Celery config
│   │   │   └── tasks.py              # Celery tasks
│   │   └── models/
│   │       ├── __init__.py
│   │       └── schemas.py            # Pydantic models
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_pose_estimator.py
│   │   ├── test_video_processor.py
│   │   ├── test_climbing_analyzer.py
│   │   ├── test_tasks_router.py
│   │   └── test_celery_tasks.py
│   ├── requirements.txt
│   └── pyproject.toml
├── uploads/                          # Uploaded videos (gitignored)
├── outputs/                          # Processed videos (gitignored)
└── docs/plans/
```

---

### Task 1: Backend Project Scaffolding

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `.gitignore`

**Step 1: Create requirements.txt**

```txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
python-multipart==0.0.20
celery[redis]==5.4.0
redis==5.2.1
mediapipe==0.10.21
opencv-python-headless==4.11.0.86
numpy==2.2.2
anthropic==0.43.0
pydantic==2.10.4
pydantic-settings==2.7.1
python-dotenv==1.0.1
```

**Step 2: Create pyproject.toml**

```toml
[project]
name = "climbing-analyzer-backend"
version = "0.1.0"
requires-python = ">=3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

**Step 3: Create .gitignore**

```
# Python
__pycache__/
*.pyc
.venv/
venv/
*.egg-info/

# Node
node_modules/
.next/

# App data
uploads/
outputs/

# Env
.env
.env.local

# IDE
.vscode/
.idea/
```

**Step 4: Create config.py**

```python
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    upload_dir: Path = Path("uploads")
    output_dir: Path = Path("outputs")
    redis_url: str = "redis://localhost:6379/0"
    anthropic_api_key: str = ""
    max_video_size_mb: int = 100
    allowed_extensions: set[str] = {".mp4", ".mov", ".avi", ".mkv"}

    model_config = {"env_file": ".env"}


settings = Settings()
```

**Step 5: Create main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import tasks

settings.upload_dir.mkdir(exist_ok=True)
settings.output_dir.mkdir(exist_ok=True)

app = FastAPI(title="Climbing Video Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=str(settings.output_dir)), name="outputs")

app.include_router(tasks.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

**Step 6: Create empty __init__.py files and conftest.py**

```python
# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)
```

**Step 7: Create routers/__init__.py and stub tasks router**

```python
# backend/app/routers/__init__.py
```

```python
# backend/app/routers/tasks.py
from fastapi import APIRouter

router = APIRouter()
```

**Step 8: Create services/__init__.py, models/__init__.py, worker/__init__.py**

Empty `__init__.py` files for each package.

**Step 9: Install dependencies and verify**

Run: `cd /Users/jiexu/code/climbing/backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

**Step 10: Run health check test**

Write and run:
```python
# backend/tests/test_health.py
def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

Run: `cd /Users/jiexu/code/climbing/backend && source .venv/bin/activate && pytest tests/test_health.py -v`
Expected: PASS

**Step 11: Commit**

```bash
git init
git add -A
git commit -m "feat: backend project scaffolding with FastAPI"
```

---

### Task 2: Pydantic Schemas

**Files:**
- Create: `backend/app/models/schemas.py`

**Step 1: Write the failing test**

```python
# backend/tests/test_schemas.py
from app.models.schemas import TaskStatus, TaskResponse, AnalysisResult


def test_task_response_creation():
    task = TaskResponse(
        task_id="abc-123",
        status=TaskStatus.PENDING,
        progress=0,
    )
    assert task.task_id == "abc-123"
    assert task.status == TaskStatus.PENDING
    assert task.progress == 0
    assert task.video_url is None
    assert task.analysis is None


def test_analysis_result():
    analysis = AnalysisResult(
        difficulty="V4",
        difficulty_explanation="Overhanging route with small crimps",
        skill_level="Intermediate",
        skill_score=65,
        suggestions=["Improve footwork on overhangs", "Work on hip positioning"],
    )
    assert analysis.skill_score == 65
    assert len(analysis.suggestions) == 2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_schemas.py -v`
Expected: FAIL (ImportError)

**Step 3: Write implementation**

```python
# backend/app/models/schemas.py
from enum import Enum

from pydantic import BaseModel


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"


class AnalysisResult(BaseModel):
    difficulty: str
    difficulty_explanation: str
    skill_level: str
    skill_score: int
    suggestions: list[str]


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    progress: int = 0
    video_url: str | None = None
    analysis: AnalysisResult | None = None
    error: str | None = None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_schemas.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/models/schemas.py backend/tests/test_schemas.py
git commit -m "feat: add Pydantic schemas for task and analysis models"
```

---

### Task 3: Upload & Task Status Endpoints

**Files:**
- Modify: `backend/app/routers/tasks.py`
- Create: `backend/tests/test_tasks_router.py`

**Step 1: Write the failing tests**

```python
# backend/tests/test_tasks_router.py
import io
from unittest.mock import patch

from app.models.schemas import TaskStatus


def test_upload_video_success(client, tmp_path):
    """Upload a valid video file and get a task ID back."""
    with patch("app.routers.tasks.settings") as mock_settings:
        mock_settings.upload_dir = tmp_path
        mock_settings.output_dir = tmp_path
        mock_settings.max_video_size_mb = 100
        mock_settings.allowed_extensions = {".mp4", ".mov"}

        with patch("app.routers.tasks.process_video_task") as mock_task:
            mock_task.delay.return_value.id = "test-task-id"

            video_content = b"fake video content"
            response = client.post(
                "/api/upload",
                files={"file": ("test.mp4", io.BytesIO(video_content), "video/mp4")},
            )

    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["task_id"] == "test-task-id"


def test_upload_invalid_extension(client):
    """Reject files with invalid extensions."""
    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", io.BytesIO(b"not a video"), "text/plain")},
    )
    assert response.status_code == 400


def test_get_task_status_not_found(client):
    """Return 404 for unknown task IDs."""
    with patch("app.routers.tasks.celery_app") as mock_celery:
        mock_result = mock_celery.AsyncResult.return_value
        mock_result.state = "PENDING"
        mock_result.info = None

        response = client.get("/api/tasks/nonexistent-id")

    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.PENDING
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_tasks_router.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# backend/app/routers/tasks.py
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.config import settings
from app.models.schemas import AnalysisResult, TaskResponse, TaskStatus
from app.worker.celery_app import celery_app
from app.worker.tasks import process_video_task

router = APIRouter()


@router.post("/upload")
async def upload_video(file: UploadFile) -> dict:
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(400, f"Invalid file type: {ext}")

    file_id = str(uuid.uuid4())
    save_path = settings.upload_dir / f"{file_id}{ext}"

    content = await file.read()
    if len(content) > settings.max_video_size_mb * 1024 * 1024:
        raise HTTPException(400, "File too large")

    save_path.write_bytes(content)

    result = process_video_task.delay(str(save_path), file_id)
    return {"task_id": result.id}


@router.get("/tasks/{task_id}")
def get_task_status(task_id: str) -> TaskResponse:
    result = celery_app.AsyncResult(task_id)

    if result.state == "PENDING":
        return TaskResponse(task_id=task_id, status=TaskStatus.PENDING, progress=0)
    elif result.state == "FAILURE":
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.FAILED,
            error=str(result.info),
        )
    elif result.state == "SUCCESS":
        data = result.result
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.COMPLETE,
            progress=100,
            video_url=data.get("video_url"),
            analysis=AnalysisResult(**data["analysis"]) if data.get("analysis") else None,
        )
    else:
        # Custom states: PROCESSING, ANALYZING
        info = result.info or {}
        status_map = {
            "PROCESSING": TaskStatus.PROCESSING,
            "ANALYZING": TaskStatus.ANALYZING,
        }
        return TaskResponse(
            task_id=task_id,
            status=status_map.get(result.state, TaskStatus.PROCESSING),
            progress=info.get("progress", 0),
        )
```

**Step 4: Create stub worker files so imports don't fail**

```python
# backend/app/worker/celery_app.py
from celery import Celery
from app.config import settings

celery_app = Celery(
    "climbing_analyzer",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
)
```

```python
# backend/app/worker/tasks.py
from app.worker.celery_app import celery_app


@celery_app.task(bind=True)
def process_video_task(self, video_path: str, file_id: str) -> dict:
    """Placeholder — implemented in Task 6."""
    raise NotImplementedError
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_tasks_router.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add backend/app/routers/tasks.py backend/app/worker/ backend/tests/test_tasks_router.py
git commit -m "feat: add upload and task status API endpoints"
```

---

### Task 4: Pose Estimator Service (MediaPipe)

**Files:**
- Create: `backend/app/services/pose_estimator.py`
- Create: `backend/tests/test_pose_estimator.py`

**Step 1: Write the failing test**

```python
# backend/tests/test_pose_estimator.py
import numpy as np
import pytest

from app.services.pose_estimator import PoseEstimator, PoseFrame


def test_pose_frame_has_landmarks():
    """PoseFrame should hold 33 landmarks with x,y,z,visibility."""
    landmarks = np.random.rand(33, 4)
    frame = PoseFrame(frame_index=0, landmarks=landmarks)
    assert frame.landmarks.shape == (33, 4)
    assert frame.frame_index == 0


def test_estimate_single_frame():
    """PoseEstimator should detect landmarks from a BGR image."""
    estimator = PoseEstimator()
    # Create a dummy 480x640 BGR image (black)
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    result = estimator.estimate_frame(image, frame_index=0)
    # May or may not detect a pose in a black image — just check it returns PoseFrame or None
    assert result is None or isinstance(result, PoseFrame)


def test_estimate_video_returns_list(tmp_path):
    """estimate_video should return a list of PoseFrame for a valid video."""
    import cv2

    # Create a minimal test video (10 frames of black)
    video_path = tmp_path / "test.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))
    for _ in range(10):
        writer.write(np.zeros((480, 640, 3), dtype=np.uint8))
    writer.release()

    estimator = PoseEstimator()
    frames, fps, total_frames = estimator.estimate_video(str(video_path))
    assert isinstance(frames, list)
    assert fps == 30.0
    assert total_frames == 10
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_pose_estimator.py -v`
Expected: FAIL (ImportError)

**Step 3: Write implementation**

```python
# backend/app/services/pose_estimator.py
from dataclasses import dataclass

import cv2
import mediapipe as mp
import numpy as np


@dataclass
class PoseFrame:
    frame_index: int
    landmarks: np.ndarray  # shape (33, 4): x, y, z, visibility


class PoseEstimator:
    def __init__(self, model_complexity: int = 1, min_detection_confidence: float = 0.5):
        self.mp_pose = mp.solutions.pose
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence

    def estimate_frame(self, bgr_image: np.ndarray, frame_index: int) -> PoseFrame | None:
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        with self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=self.model_complexity,
            min_detection_confidence=self.min_detection_confidence,
        ) as pose:
            results = pose.process(rgb_image)
            if not results.pose_landmarks:
                return None
            landmarks = np.array(
                [[lm.x, lm.y, lm.z, lm.visibility] for lm in results.pose_landmarks.landmark]
            )
            return PoseFrame(frame_index=frame_index, landmarks=landmarks)

    def estimate_video(
        self, video_path: str, on_progress: callable = None
    ) -> tuple[list[PoseFrame], float, int]:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        pose_frames: list[PoseFrame] = []

        with self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=self.model_complexity,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=0.5,
        ) as pose:
            frame_idx = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb)

                if results.pose_landmarks:
                    landmarks = np.array(
                        [[lm.x, lm.y, lm.z, lm.visibility] for lm in results.pose_landmarks.landmark]
                    )
                    pose_frames.append(PoseFrame(frame_index=frame_idx, landmarks=landmarks))

                if on_progress and total_frames > 0:
                    on_progress(int(frame_idx / total_frames * 50))  # 0-50% for pose estimation

                frame_idx += 1

        cap.release()
        return pose_frames, fps, total_frames
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_pose_estimator.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/services/pose_estimator.py backend/tests/test_pose_estimator.py
git commit -m "feat: add MediaPipe pose estimator service"
```

---

### Task 5: Video Processor Service (Skeleton Overlay)

**Files:**
- Create: `backend/app/services/video_processor.py`
- Create: `backend/tests/test_video_processor.py`

**Step 1: Write the failing test**

```python
# backend/tests/test_video_processor.py
import cv2
import numpy as np
import pytest

from app.services.pose_estimator import PoseFrame
from app.services.video_processor import VideoProcessor


def test_draw_skeleton_on_frame():
    """draw_skeleton should return a frame with skeleton drawn."""
    processor = VideoProcessor()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Create a fake pose with landmarks roughly in the center
    landmarks = np.full((33, 4), 0.5)  # all at center, fully visible
    landmarks[:, 3] = 1.0  # visibility
    pose = PoseFrame(frame_index=0, landmarks=landmarks)

    result = processor.draw_skeleton(frame, pose)
    assert result.shape == frame.shape
    # The result should not be all black (skeleton was drawn)
    assert np.any(result != 0)


def test_process_video_creates_output(tmp_path):
    """process_video should create an output video file."""
    # Create a test video
    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "output.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(input_path), fourcc, 30.0, (640, 480))
    for _ in range(10):
        writer.write(np.zeros((480, 640, 3), dtype=np.uint8))
    writer.release()

    processor = VideoProcessor()
    # Empty pose frames list — just pass through
    processor.process_video(str(input_path), str(output_path), [])
    assert output_path.exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_video_processor.py -v`
Expected: FAIL (ImportError)

**Step 3: Write implementation**

```python
# backend/app/services/video_processor.py
import cv2
import mediapipe as mp
import numpy as np

from app.services.pose_estimator import PoseFrame

# MediaPipe pose connections for drawing skeleton lines
POSE_CONNECTIONS = mp.solutions.pose.POSE_CONNECTIONS


class VideoProcessor:
    def __init__(
        self,
        line_color: tuple[int, int, int] = (0, 255, 0),
        point_color: tuple[int, int, int] = (0, 0, 255),
        line_thickness: int = 2,
        point_radius: int = 4,
    ):
        self.line_color = line_color
        self.point_color = point_color
        self.line_thickness = line_thickness
        self.point_radius = point_radius

    def draw_skeleton(self, frame: np.ndarray, pose: PoseFrame) -> np.ndarray:
        h, w = frame.shape[:2]
        result = frame.copy()
        landmarks = pose.landmarks  # (33, 4)

        # Draw connections
        for start_idx, end_idx in POSE_CONNECTIONS:
            if landmarks[start_idx, 3] < 0.5 or landmarks[end_idx, 3] < 0.5:
                continue
            start = (int(landmarks[start_idx, 0] * w), int(landmarks[start_idx, 1] * h))
            end = (int(landmarks[end_idx, 0] * w), int(landmarks[end_idx, 1] * h))
            cv2.line(result, start, end, self.line_color, self.line_thickness)

        # Draw keypoints
        for i in range(33):
            if landmarks[i, 3] < 0.5:
                continue
            point = (int(landmarks[i, 0] * w), int(landmarks[i, 1] * h))
            cv2.circle(result, point, self.point_radius, self.point_color, -1)

        return result

    def process_video(
        self,
        input_path: str,
        output_path: str,
        pose_frames: list[PoseFrame],
        on_progress: callable = None,
    ) -> None:
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Build frame_index -> PoseFrame lookup
        pose_map = {pf.frame_index: pf for pf in pose_frames}

        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx in pose_map:
                frame = self.draw_skeleton(frame, pose_map[frame_idx])

            writer.write(frame)

            if on_progress and total > 0:
                on_progress(50 + int(frame_idx / total * 30))  # 50-80% for video processing

            frame_idx += 1

        cap.release()
        writer.release()

    def extract_keyframes(
        self, video_path: str, pose_frames: list[PoseFrame], count: int = 5
    ) -> list[np.ndarray]:
        """Extract evenly-spaced keyframe images for AI analysis."""
        if not pose_frames:
            return []

        cap = cv2.VideoCapture(video_path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, total // count)
        target_indices = set(range(0, total, step))

        keyframes = []
        frame_idx = 0
        while cap.isOpened() and len(keyframes) < count:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx in target_indices:
                # Draw skeleton if available
                pose_map = {pf.frame_index: pf for pf in pose_frames}
                if frame_idx in pose_map:
                    frame = self.draw_skeleton(frame, pose_map[frame_idx])
                keyframes.append(frame)
            frame_idx += 1

        cap.release()
        return keyframes
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_video_processor.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/services/video_processor.py backend/tests/test_video_processor.py
git commit -m "feat: add video processor with skeleton overlay"
```

---

### Task 6: Climbing Analyzer Service (Claude API)

**Files:**
- Create: `backend/app/services/climbing_analyzer.py`
- Create: `backend/tests/test_climbing_analyzer.py`

**Step 1: Write the failing test**

```python
# backend/tests/test_climbing_analyzer.py
import json
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.services.climbing_analyzer import ClimbingAnalyzer
from app.services.pose_estimator import PoseFrame


def _make_pose_frames(count: int = 30) -> list[PoseFrame]:
    frames = []
    for i in range(count):
        landmarks = np.random.rand(33, 4)
        landmarks[:, 3] = 1.0
        frames.append(PoseFrame(frame_index=i, landmarks=landmarks))
    return frames


def test_build_analysis_prompt():
    """Should produce a structured prompt from pose data."""
    analyzer = ClimbingAnalyzer(api_key="test-key")
    frames = _make_pose_frames(30)
    prompt = analyzer.build_analysis_prompt(frames, fps=30.0, total_frames=30)
    assert "joint angles" in prompt.lower() or "climbing" in prompt.lower()
    assert len(prompt) > 100


def test_analyze_climbing_returns_result():
    """Should call Claude API and parse the response into AnalysisResult."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = json.dumps({
        "difficulty": "V3",
        "difficulty_explanation": "Moderate overhang with good holds",
        "skill_level": "Intermediate",
        "skill_score": 60,
        "suggestions": [
            "Keep hips closer to the wall",
            "Use more leg drive on overhangs",
        ],
    })

    with patch("app.services.climbing_analyzer.anthropic.Anthropic") as mock_anthropic:
        mock_client = mock_anthropic.return_value
        mock_client.messages.create.return_value = mock_response

        analyzer = ClimbingAnalyzer(api_key="test-key")
        frames = _make_pose_frames(30)
        result = analyzer.analyze(frames, fps=30.0, total_frames=30)

    assert result.difficulty == "V3"
    assert result.skill_score == 60
    assert len(result.suggestions) == 2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_climbing_analyzer.py -v`
Expected: FAIL (ImportError)

**Step 3: Write implementation**

```python
# backend/app/services/climbing_analyzer.py
import json
import math

import anthropic
import numpy as np

from app.models.schemas import AnalysisResult
from app.services.pose_estimator import PoseFrame

# MediaPipe landmark indices
LANDMARK_NAMES = {
    0: "nose", 11: "left_shoulder", 12: "right_shoulder",
    13: "left_elbow", 14: "right_elbow", 15: "left_wrist", 16: "right_wrist",
    23: "left_hip", 24: "right_hip", 25: "left_knee", 26: "right_knee",
    27: "left_ankle", 28: "right_ankle",
}


def _angle_between(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    ba = a - b
    bc = c - b
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    return math.degrees(math.acos(np.clip(cos_angle, -1, 1)))


class ClimbingAnalyzer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def _compute_joint_angles(self, landmarks: np.ndarray) -> dict:
        """Compute key joint angles from landmarks (x, y, z)."""
        pts = landmarks[:, :3]
        return {
            "left_elbow": _angle_between(pts[11], pts[13], pts[15]),
            "right_elbow": _angle_between(pts[12], pts[14], pts[16]),
            "left_knee": _angle_between(pts[23], pts[25], pts[27]),
            "right_knee": _angle_between(pts[24], pts[26], pts[28]),
            "left_shoulder": _angle_between(pts[13], pts[11], pts[23]),
            "right_shoulder": _angle_between(pts[14], pts[12], pts[24]),
            "left_hip": _angle_between(pts[11], pts[23], pts[25]),
            "right_hip": _angle_between(pts[12], pts[24], pts[26]),
        }

    def _compute_center_of_gravity(self, landmarks: np.ndarray) -> tuple[float, float]:
        """Approximate center of gravity from hip midpoint."""
        left_hip = landmarks[23, :2]
        right_hip = landmarks[24, :2]
        return tuple((left_hip + right_hip) / 2)

    def build_analysis_prompt(
        self, pose_frames: list[PoseFrame], fps: float, total_frames: int
    ) -> str:
        duration = total_frames / fps if fps > 0 else 0
        sample_count = min(len(pose_frames), 10)
        step = max(1, len(pose_frames) // sample_count)
        sampled = pose_frames[::step][:sample_count]

        frame_data = []
        for pf in sampled:
            angles = self._compute_joint_angles(pf.landmarks)
            cog = self._compute_center_of_gravity(pf.landmarks)
            frame_data.append({
                "time_sec": round(pf.frame_index / fps, 2) if fps > 0 else 0,
                "joint_angles": {k: round(v, 1) for k, v in angles.items()},
                "center_of_gravity": {"x": round(cog[0], 3), "y": round(cog[1], 3)},
            })

        # Compute movement stats
        if len(pose_frames) >= 2:
            cogs = [self._compute_center_of_gravity(pf.landmarks) for pf in pose_frames]
            vertical_range = max(c[1] for c in cogs) - min(c[1] for c in cogs)
            horizontal_range = max(c[0] for c in cogs) - min(c[0] for c in cogs)
        else:
            vertical_range = horizontal_range = 0

        return f"""Analyze this rock climbing video based on the body pose data below.

## Video Info
- Duration: {duration:.1f} seconds
- FPS: {fps}
- Total frames with detected pose: {len(pose_frames)} / {total_frames}

## Movement Summary
- Vertical movement range: {vertical_range:.3f} (normalized 0-1)
- Horizontal movement range: {horizontal_range:.3f} (normalized 0-1)

## Sampled Frame Data (joint angles in degrees, center of gravity in normalized coords)
{json.dumps(frame_data, indent=2)}

## Instructions
Based on the pose data above, provide a JSON response with:
1. "difficulty": The estimated climbing grade (V-scale, e.g. "V0"-"V10")
2. "difficulty_explanation": Brief explanation of why this difficulty (1-2 sentences)
3. "skill_level": One of "Beginner", "Intermediate", "Advanced", "Expert"
4. "skill_score": Integer 0-100 representing overall climbing technique quality
5. "suggestions": Array of 3-5 specific, actionable improvement tips

Consider these factors:
- Joint angles indicate body positioning efficiency
- Center of gravity movement indicates balance and control
- Arm bend angles indicate whether the climber is over-gripping or using straight arms
- Hip position relative to the wall
- Knee angles indicate foot placement quality

Respond ONLY with valid JSON, no markdown or explanation outside the JSON."""

    def analyze(
        self,
        pose_frames: list[PoseFrame],
        fps: float,
        total_frames: int,
        keyframe_images: list[np.ndarray] | None = None,
    ) -> AnalysisResult:
        prompt = self.build_analysis_prompt(pose_frames, fps, total_frames)

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text
        # Strip markdown code fences if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1].rsplit("```", 1)[0]

        data = json.loads(response_text)
        return AnalysisResult(**data)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_climbing_analyzer.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/services/climbing_analyzer.py backend/tests/test_climbing_analyzer.py
git commit -m "feat: add Claude API climbing analyzer service"
```

---

### Task 7: Celery Worker Task (Full Pipeline)

**Files:**
- Modify: `backend/app/worker/tasks.py`
- Create: `backend/tests/test_celery_tasks.py`

**Step 1: Write the failing test**

```python
# backend/tests/test_celery_tasks.py
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.models.schemas import AnalysisResult


def test_process_video_pipeline():
    """The full pipeline should call estimator, processor, and analyzer."""
    mock_self = MagicMock()

    fake_analysis = AnalysisResult(
        difficulty="V3",
        difficulty_explanation="Moderate route",
        skill_level="Intermediate",
        skill_score=65,
        suggestions=["Improve footwork"],
    )

    with (
        patch("app.worker.tasks.PoseEstimator") as mock_estimator_cls,
        patch("app.worker.tasks.VideoProcessor") as mock_processor_cls,
        patch("app.worker.tasks.ClimbingAnalyzer") as mock_analyzer_cls,
        patch("app.worker.tasks.settings") as mock_settings,
    ):
        mock_settings.output_dir.return_value = "/tmp"
        mock_settings.output_dir.__truediv__ = lambda self, x: f"/tmp/{x}"
        mock_settings.anthropic_api_key = "test-key"

        mock_estimator = mock_estimator_cls.return_value
        mock_estimator.estimate_video.return_value = ([], 30.0, 100)

        mock_processor = mock_processor_cls.return_value
        mock_processor.extract_keyframes.return_value = []

        mock_analyzer = mock_analyzer_cls.return_value
        mock_analyzer.analyze.return_value = fake_analysis

        from app.worker.tasks import process_video_task

        result = process_video_task(mock_self, "/tmp/test.mp4", "test-id")

    assert result["analysis"]["difficulty"] == "V3"
    assert "video_url" in result
    mock_estimator.estimate_video.assert_called_once()
    mock_processor.process_video.assert_called_once()
    mock_analyzer.analyze.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_celery_tasks.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# backend/app/worker/tasks.py
from app.config import settings
from app.worker.celery_app import celery_app


@celery_app.task(bind=True)
def process_video_task(self, video_path: str, file_id: str) -> dict:
    # Import here to avoid circular imports and allow mocking
    from app.services.climbing_analyzer import ClimbingAnalyzer
    from app.services.pose_estimator import PoseEstimator
    from app.services.video_processor import VideoProcessor

    def update_progress(progress: int):
        self.update_state(state="PROCESSING", meta={"progress": progress})

    # Step 1: Pose estimation (0-50%)
    self.update_state(state="PROCESSING", meta={"progress": 0})
    estimator = PoseEstimator()
    pose_frames, fps, total_frames = estimator.estimate_video(
        video_path, on_progress=update_progress
    )

    # Step 2: Video processing with skeleton overlay (50-80%)
    output_filename = f"{file_id}_skeleton.mp4"
    output_path = str(settings.output_dir / output_filename)
    processor = VideoProcessor()
    processor.process_video(
        video_path, output_path, pose_frames, on_progress=update_progress
    )

    # Step 3: AI analysis (80-100%)
    self.update_state(state="ANALYZING", meta={"progress": 80})
    keyframes = processor.extract_keyframes(video_path, pose_frames, count=5)
    analyzer = ClimbingAnalyzer(api_key=settings.anthropic_api_key)
    analysis = analyzer.analyze(pose_frames, fps, total_frames, keyframes)

    self.update_state(state="PROCESSING", meta={"progress": 100})

    return {
        "video_url": f"/outputs/{output_filename}",
        "analysis": analysis.model_dump(),
    }
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_celery_tasks.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/worker/tasks.py backend/tests/test_celery_tasks.py
git commit -m "feat: implement full video processing pipeline in Celery task"
```

---

### Task 8: Frontend Project Scaffolding

**Files:**
- Create: `frontend/` (via create-next-app)
- Modify: `frontend/src/app/layout.tsx`
- Create: `frontend/src/lib/api.ts`

**Step 1: Create Next.js project**

Run: `cd /Users/jiexu/code/climbing && npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --no-turbopack`

**Step 2: Create API client**

```typescript
// frontend/src/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface AnalysisResult {
  difficulty: string;
  difficulty_explanation: string;
  skill_level: string;
  skill_score: number;
  suggestions: string[];
}

export interface TaskResponse {
  task_id: string;
  status: "pending" | "processing" | "analyzing" | "complete" | "failed";
  progress: number;
  video_url: string | null;
  analysis: AnalysisResult | null;
  error: string | null;
}

export async function uploadVideo(file: File): Promise<{ task_id: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Upload failed");
  }

  return res.json();
}

export async function getTaskStatus(taskId: string): Promise<TaskResponse> {
  const res = await fetch(`${API_BASE}/tasks/${taskId}`);
  if (!res.ok) throw new Error("Failed to fetch task status");
  return res.json();
}

export function getVideoUrl(path: string): string {
  const base = process.env.NEXT_PUBLIC_API_URL?.replace("/api", "") || "http://localhost:8000";
  return `${base}${path}`;
}
```

**Step 3: Update layout.tsx with app title**

```tsx
// frontend/src/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Climbing Video Analyzer",
  description: "Upload climbing videos for AI-powered pose analysis and feedback",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

**Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold Next.js frontend with API client"
```

---

### Task 9: Frontend - Upload Page

**Files:**
- Create: `frontend/src/components/VideoUploader.tsx`
- Modify: `frontend/src/app/page.tsx`

**Step 1: Create VideoUploader component**

```tsx
// frontend/src/components/VideoUploader.tsx
"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { uploadVideo } from "@/lib/api";

export default function VideoUploader() {
  const router = useRouter();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(
    async (file: File) => {
      const validTypes = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska"];
      if (!validTypes.includes(file.type) && !file.name.match(/\.(mp4|mov|avi|mkv)$/i)) {
        setError("Please upload a video file (MP4, MOV, AVI, or MKV)");
        return;
      }

      setError(null);
      setIsUploading(true);

      try {
        const { task_id } = await uploadVideo(file);
        router.push(`/processing/${task_id}`);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
        setIsUploading(false);
      }
    },
    [router]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-2xl p-12 text-center transition-colors cursor-pointer ${
        isDragging
          ? "border-blue-500 bg-blue-50"
          : "border-gray-300 hover:border-gray-400"
      }`}
    >
      {isUploading ? (
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full" />
          <p className="text-gray-600">Uploading video...</p>
        </div>
      ) : (
        <label className="cursor-pointer flex flex-col items-center gap-4">
          <svg className="w-12 h-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 16l4-4m0 0l4 4m-4-4v12M21 12V4a2 2 0 00-2-2h-6l-2 2H5a2 2 0 00-2 2v4" />
          </svg>
          <div>
            <p className="text-lg font-medium text-gray-700">
              Drop your climbing video here
            </p>
            <p className="text-sm text-gray-500 mt-1">
              or click to browse (MP4, MOV, AVI, MKV up to 100MB)
            </p>
          </div>
          <input
            type="file"
            accept="video/*"
            onChange={handleChange}
            className="hidden"
          />
        </label>
      )}
      {error && <p className="mt-4 text-red-500 text-sm">{error}</p>}
    </div>
  );
}
```

**Step 2: Create home page**

```tsx
// frontend/src/app/page.tsx
import VideoUploader from "@/components/VideoUploader";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-3xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Climbing Video Analyzer
          </h1>
          <p className="text-lg text-gray-600">
            Upload your climbing video and get AI-powered analysis of your technique,
            difficulty assessment, and personalized improvement tips.
          </p>
        </div>

        <VideoUploader />

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="text-3xl mb-3">🦴</div>
            <h3 className="font-semibold text-gray-800 mb-2">Pose Detection</h3>
            <p className="text-sm text-gray-600">
              AI tracks your body movements frame by frame with skeleton overlay
            </p>
          </div>
          <div className="text-center">
            <div className="text-3xl mb-3">📊</div>
            <h3 className="font-semibold text-gray-800 mb-2">Difficulty Rating</h3>
            <p className="text-sm text-gray-600">
              Get an estimated V-scale difficulty for the route you climbed
            </p>
          </div>
          <div className="text-center">
            <div className="text-3xl mb-3">💡</div>
            <h3 className="font-semibold text-gray-800 mb-2">Smart Tips</h3>
            <p className="text-sm text-gray-600">
              Receive personalized suggestions to improve your climbing technique
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
```

**Step 3: Commit**

```bash
git add frontend/src/
git commit -m "feat: add upload page with drag-and-drop video uploader"
```

---

### Task 10: Frontend - Processing Status Page

**Files:**
- Create: `frontend/src/components/ProcessingStatus.tsx`
- Create: `frontend/src/app/processing/[taskId]/page.tsx`

**Step 1: Create ProcessingStatus component**

```tsx
// frontend/src/components/ProcessingStatus.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getTaskStatus, TaskResponse } from "@/lib/api";

const STATUS_LABELS: Record<string, string> = {
  pending: "Waiting in queue...",
  processing: "Analyzing pose & generating skeleton overlay...",
  analyzing: "AI is evaluating your climbing technique...",
  complete: "Analysis complete!",
  failed: "Processing failed",
};

export default function ProcessingStatus({ taskId }: { taskId: string }) {
  const router = useRouter();
  const [task, setTask] = useState<TaskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const poll = async () => {
      try {
        const data = await getTaskStatus(taskId);
        if (cancelled) return;
        setTask(data);

        if (data.status === "complete") {
          router.push(`/results/${taskId}`);
          return;
        }

        if (data.status === "failed") {
          setError(data.error || "An unknown error occurred");
          return;
        }

        setTimeout(poll, 2000);
      } catch {
        if (!cancelled) setError("Lost connection to server");
      }
    };

    poll();
    return () => { cancelled = true; };
  }, [taskId, router]);

  return (
    <div className="max-w-lg mx-auto text-center">
      <div className="mb-8">
        <div className="animate-pulse text-6xl mb-6">🧗</div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Processing Your Video
        </h2>
        <p className="text-gray-600">
          {task ? STATUS_LABELS[task.status] || task.status : "Connecting..."}
        </p>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
        <div
          className="bg-blue-500 h-3 rounded-full transition-all duration-500"
          style={{ width: `${task?.progress ?? 0}%` }}
        />
      </div>
      <p className="text-sm text-gray-500">{task?.progress ?? 0}%</p>

      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error}</p>
          <button
            onClick={() => router.push("/")}
            className="mt-3 text-sm text-blue-600 hover:underline"
          >
            ← Try another video
          </button>
        </div>
      )}
    </div>
  );
}
```

**Step 2: Create processing page**

```tsx
// frontend/src/app/processing/[taskId]/page.tsx
import ProcessingStatus from "@/components/ProcessingStatus";

export default async function ProcessingPage({
  params,
}: {
  params: Promise<{ taskId: string }>;
}) {
  const { taskId } = await params;
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white flex items-center justify-center px-4">
      <ProcessingStatus taskId={taskId} />
    </main>
  );
}
```

**Step 3: Commit**

```bash
git add frontend/src/
git commit -m "feat: add processing status page with progress polling"
```

---

### Task 11: Frontend - Results Page

**Files:**
- Create: `frontend/src/components/VideoPlayer.tsx`
- Create: `frontend/src/components/AnalysisReport.tsx`
- Create: `frontend/src/app/results/[taskId]/page.tsx`

**Step 1: Create VideoPlayer component**

```tsx
// frontend/src/components/VideoPlayer.tsx
"use client";

import { getVideoUrl } from "@/lib/api";

export default function VideoPlayer({ videoPath }: { videoPath: string }) {
  return (
    <div className="rounded-xl overflow-hidden bg-black">
      <video
        controls
        className="w-full"
        src={getVideoUrl(videoPath)}
      >
        Your browser does not support video playback.
      </video>
    </div>
  );
}
```

**Step 2: Create AnalysisReport component**

```tsx
// frontend/src/components/AnalysisReport.tsx
import { AnalysisResult } from "@/lib/api";

function SkillBar({ score }: { score: number }) {
  const color =
    score >= 80 ? "bg-green-500" : score >= 50 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="w-full bg-gray-200 rounded-full h-4">
      <div
        className={`${color} h-4 rounded-full transition-all duration-1000`}
        style={{ width: `${score}%` }}
      />
    </div>
  );
}

export default function AnalysisReport({ analysis }: { analysis: AnalysisResult }) {
  return (
    <div className="space-y-6">
      {/* Difficulty Card */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
          Route Difficulty
        </h3>
        <div className="flex items-baseline gap-3">
          <span className="text-4xl font-bold text-gray-900">
            {analysis.difficulty}
          </span>
        </div>
        <p className="mt-2 text-gray-600">{analysis.difficulty_explanation}</p>
      </div>

      {/* Skill Level Card */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">
          Your Skill Level
        </h3>
        <div className="flex items-baseline gap-3 mb-3">
          <span className="text-2xl font-bold text-gray-900">
            {analysis.skill_level}
          </span>
          <span className="text-lg text-gray-500">{analysis.skill_score}/100</span>
        </div>
        <SkillBar score={analysis.skill_score} />
      </div>

      {/* Suggestions Card */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">
          Improvement Tips
        </h3>
        <ul className="space-y-3">
          {analysis.suggestions.map((tip, i) => (
            <li key={i} className="flex gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-medium">
                {i + 1}
              </span>
              <span className="text-gray-700">{tip}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

**Step 3: Create results page**

```tsx
// frontend/src/app/results/[taskId]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getTaskStatus, TaskResponse } from "@/lib/api";
import VideoPlayer from "@/components/VideoPlayer";
import AnalysisReport from "@/components/AnalysisReport";

export default function ResultsPage({
  params,
}: {
  params: Promise<{ taskId: string }>;
}) {
  const router = useRouter();
  const [task, setTask] = useState<TaskResponse | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);

  useEffect(() => {
    params.then((p) => setTaskId(p.taskId));
  }, [params]);

  useEffect(() => {
    if (!taskId) return;
    getTaskStatus(taskId).then(setTask).catch(() => router.push("/"));
  }, [taskId, router]);

  if (!task || task.status !== "complete") {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full" />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
          <button
            onClick={() => router.push("/")}
            className="text-blue-600 hover:underline text-sm"
          >
            ← Analyze another video
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              Skeleton Overlay
            </h2>
            {task.video_url && <VideoPlayer videoPath={task.video_url} />}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-4">
              AI Analysis
            </h2>
            {task.analysis && <AnalysisReport analysis={task.analysis} />}
          </div>
        </div>
      </div>
    </main>
  );
}
```

**Step 4: Commit**

```bash
git add frontend/src/
git commit -m "feat: add results page with video player and analysis report"
```

---

### Task 12: Integration & Run Scripts

**Files:**
- Create: `backend/.env.example`
- Create: `README.md`
- Create: `docker-compose.yml` (Redis only)

**Step 1: Create .env.example**

```
ANTHROPIC_API_KEY=your-api-key-here
REDIS_URL=redis://localhost:6379/0
```

**Step 2: Create docker-compose.yml for Redis**

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

**Step 3: Create README.md**

```markdown
# Climbing Video Analyzer

Upload climbing videos for AI-powered pose analysis and technique feedback.

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
celery -A app.worker.celery_app worker --loglevel=info

### 3. Frontend
cd frontend
npm install
npm run dev

### 4. Open http://localhost:3000
```

**Step 4: Commit**

```bash
git add docker-compose.yml backend/.env.example README.md
git commit -m "feat: add dev setup with Docker Compose, env config, and README"
```

---

### Task 13: End-to-End Smoke Test

**Step 1: Start all services**

Terminal 1: `docker compose up -d`
Terminal 2: `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
Terminal 3: `cd backend && source .venv/bin/activate && celery -A app.worker.celery_app worker --loglevel=info`
Terminal 4: `cd frontend && npm run dev`

**Step 2: Test health endpoint**

Run: `curl http://localhost:8000/api/health`
Expected: `{"status":"ok"}`

**Step 3: Test upload via curl**

Run: `curl -X POST http://localhost:8000/api/upload -F "file=@test_video.mp4"`
Expected: `{"task_id":"<uuid>"}`

**Step 4: Test frontend**

Open http://localhost:3000, upload a climbing video, verify the full flow works.

**Step 5: Run all backend tests**

Run: `cd backend && pytest -v`
Expected: All tests PASS

**Step 6: Final commit**

```bash
git add -A
git commit -m "feat: complete MVP of climbing video analyzer"
```
