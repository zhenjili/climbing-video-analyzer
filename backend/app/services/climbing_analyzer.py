import json
import math

import anthropic
import numpy as np

from app.models.schemas import AnalysisResult
from app.services.pose_estimator import PoseFrame

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
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1].rsplit("```", 1)[0]

        data = json.loads(response_text)
        return AnalysisResult(**data)
