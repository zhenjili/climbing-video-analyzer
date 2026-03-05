import uuid
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, UploadFile

from app.config import settings
from app.models.schemas import AnalysisResult, TaskResponse, TaskStatus
from app.worker.celery_app import celery_app
from app.worker.tasks import process_video_task

router = APIRouter()


@router.post("/upload")
async def upload_video(file: UploadFile, language: str = Form(default="zh")) -> dict:
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(400, f"Invalid file type: {ext}")

    file_id = str(uuid.uuid4())
    save_path = settings.upload_dir / f"{file_id}{ext}"

    content = await file.read()
    if len(content) > settings.max_video_size_mb * 1024 * 1024:
        raise HTTPException(400, "File too large")

    save_path.write_bytes(content)

    result = process_video_task.delay(str(save_path), file_id, language)
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
