from enum import Enum
from pydantic import BaseModel


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    FAILED = "failed"


class ImprovementFrame(BaseModel):
    time_sec: float
    image_url: str | None = None
    issue: str
    suggestion: str


class AnalysisResult(BaseModel):
    difficulty: str
    difficulty_explanation: str
    skill_level: str
    skill_score: int
    suggestions: list[str]
    improvement_frames: list[ImprovementFrame] = []


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    progress: int = 0
    video_url: str | None = None
    analysis: AnalysisResult | None = None
    error: str | None = None
