from app.config import settings
from app.worker.celery_app import celery_app


@celery_app.task(bind=True)
def process_video_task(self, video_path: str, file_id: str) -> dict:
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
