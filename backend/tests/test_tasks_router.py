import io
from unittest.mock import patch

from app.models.schemas import TaskStatus


def test_upload_video_success(client, tmp_path):
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
    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", io.BytesIO(b"not a video"), "text/plain")},
    )
    assert response.status_code == 400


def test_get_task_status_pending(client):
    with patch("app.routers.tasks.celery_app") as mock_celery:
        mock_result = mock_celery.AsyncResult.return_value
        mock_result.state = "PENDING"
        mock_result.info = None

        response = client.get("/api/tasks/nonexistent-id")

    assert response.status_code == 200
    assert response.json()["status"] == TaskStatus.PENDING
