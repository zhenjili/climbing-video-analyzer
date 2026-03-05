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
