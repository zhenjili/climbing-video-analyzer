from app.worker.celery_app import celery_app


@celery_app.task(bind=True)
def process_video_task(self, video_path: str, file_id: str) -> dict:
    """Placeholder - implemented later."""
    raise NotImplementedError
