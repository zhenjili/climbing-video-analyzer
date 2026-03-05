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
                    on_progress(int(frame_idx / total_frames * 50))

                frame_idx += 1

        cap.release()
        return pose_frames, fps, total_frames
