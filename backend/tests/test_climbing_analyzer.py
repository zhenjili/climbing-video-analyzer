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
    analyzer = ClimbingAnalyzer(api_key="test-key")
    frames = _make_pose_frames(30)
    prompt = analyzer.build_analysis_prompt(frames, fps=30.0, total_frames=30)
    assert "climbing" in prompt.lower()
    assert len(prompt) > 100


def test_analyze_climbing_returns_result():
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
