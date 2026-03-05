from unittest.mock import MagicMock, patch

from app.models.schemas import AnalysisResult


def test_process_video_pipeline():
    fake_analysis = AnalysisResult(
        difficulty="V3",
        difficulty_explanation="Moderate route",
        skill_level="Intermediate",
        skill_score=65,
        suggestions=["Improve footwork"],
    )

    with (
        patch(
            "app.services.pose_estimator.PoseEstimator"
        ) as mock_estimator_cls,
        patch(
            "app.services.video_processor.VideoProcessor"
        ) as mock_processor_cls,
        patch(
            "app.services.climbing_analyzer.ClimbingAnalyzer"
        ) as mock_analyzer_cls,
        patch("app.worker.tasks.settings") as mock_settings,
    ):
        mock_settings.output_dir.__truediv__ = lambda self, x: f"/tmp/{x}"
        mock_settings.anthropic_api_key = "test-key"

        mock_estimator = mock_estimator_cls.return_value
        mock_estimator.estimate_video.return_value = ([], 30.0, 100)

        mock_processor = mock_processor_cls.return_value
        mock_processor.extract_keyframes.return_value = []

        mock_analyzer = mock_analyzer_cls.return_value
        mock_analyzer.analyze.return_value = fake_analysis

        from app.worker.tasks import process_video_task

        # Mock update_state on the task object itself (bind=True means
        # Celery passes the task instance as self)
        process_video_task.update_state = MagicMock()

        # .run() calls the underlying function with the task as self
        result = process_video_task.run("/tmp/test.mp4", "test-id")

    assert result["analysis"]["difficulty"] == "V3"
    assert result["video_url"] == "/outputs/test-id_skeleton.mp4"
    mock_estimator.estimate_video.assert_called_once()
    mock_processor.process_video.assert_called_once()
    mock_analyzer.analyze.assert_called_once()

    # Verify progress updates were called
    process_video_task.update_state.assert_any_call(
        state="PROCESSING", meta={"progress": 0}
    )
    process_video_task.update_state.assert_any_call(
        state="ANALYZING", meta={"progress": 80}
    )
    process_video_task.update_state.assert_any_call(
        state="PROCESSING", meta={"progress": 100}
    )
