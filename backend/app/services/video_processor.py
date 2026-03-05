import os
import subprocess

import cv2
import mediapipe as mp
import numpy as np

from app.services.pose_estimator import PoseFrame

POSE_CONNECTIONS = mp.solutions.pose.POSE_CONNECTIONS


class VideoProcessor:
    def __init__(
        self,
        line_color: tuple[int, int, int] = (0, 255, 0),
        point_color: tuple[int, int, int] = (0, 0, 255),
        line_thickness: int = 2,
        point_radius: int = 4,
    ):
        self.line_color = line_color
        self.point_color = point_color
        self.line_thickness = line_thickness
        self.point_radius = point_radius

    def draw_skeleton(self, frame: np.ndarray, pose: PoseFrame) -> np.ndarray:
        h, w = frame.shape[:2]
        result = frame.copy()
        landmarks = pose.landmarks

        for start_idx, end_idx in POSE_CONNECTIONS:
            if landmarks[start_idx, 3] < 0.5 or landmarks[end_idx, 3] < 0.5:
                continue
            start = (int(landmarks[start_idx, 0] * w), int(landmarks[start_idx, 1] * h))
            end = (int(landmarks[end_idx, 0] * w), int(landmarks[end_idx, 1] * h))
            cv2.line(result, start, end, self.line_color, self.line_thickness)

        for i in range(33):
            if landmarks[i, 3] < 0.5:
                continue
            point = (int(landmarks[i, 0] * w), int(landmarks[i, 1] * h))
            cv2.circle(result, point, self.point_radius, self.point_color, -1)

        return result

    def process_video(
        self,
        input_path: str,
        output_path: str,
        pose_frames: list[PoseFrame],
        on_progress: callable = None,
    ) -> None:
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        pose_map = {pf.frame_index: pf for pf in pose_frames}

        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx in pose_map:
                frame = self.draw_skeleton(frame, pose_map[frame_idx])

            writer.write(frame)

            if on_progress and total > 0:
                on_progress(50 + int(frame_idx / total * 30))

            frame_idx += 1

        cap.release()
        writer.release()

        # Re-encode to H.264 for browser compatibility
        self._reencode_h264(output_path)

    @staticmethod
    def _reencode_h264(path: str) -> None:
        tmp = path + ".tmp.mp4"
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", path,
                "-c:v", "libx264", "-preset", "fast",
                "-crf", "23", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-an", tmp,
            ],
            capture_output=True,
            check=True,
        )
        os.replace(tmp, path)

    def extract_keyframes(
        self, video_path: str, pose_frames: list[PoseFrame], count: int = 5
    ) -> list[np.ndarray]:
        if not pose_frames:
            return []

        cap = cv2.VideoCapture(video_path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, total // count)
        target_indices = set(range(0, total, step))

        pose_map = {pf.frame_index: pf for pf in pose_frames}
        keyframes = []
        frame_idx = 0
        while cap.isOpened() and len(keyframes) < count:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx in target_indices:
                if frame_idx in pose_map:
                    frame = self.draw_skeleton(frame, pose_map[frame_idx])
                keyframes.append(frame)
            frame_idx += 1

        cap.release()
        return keyframes

    def save_frames_at_timestamps(
        self,
        video_path: str,
        timestamps_sec: list[float],
        pose_frames: list[PoseFrame],
        output_dir: str,
        file_id: str,
    ) -> dict[float, str]:
        """Extract frames at given timestamps, draw skeleton, save as JPEG.
        Returns mapping of timestamp -> saved image filename."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            cap.release()
            return {}

        pose_map = {pf.frame_index: pf for pf in pose_frames}
        target_frames = {round(t * fps): t for t in timestamps_sec}
        result: dict[float, str] = {}

        frame_idx = 0
        while cap.isOpened() and len(result) < len(target_frames):
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx in target_frames:
                ts = target_frames[frame_idx]
                if frame_idx in pose_map:
                    frame = self.draw_skeleton(frame, pose_map[frame_idx])
                filename = f"{file_id}_frame_{ts:.2f}s.jpg"
                cv2.imwrite(os.path.join(output_dir, filename), frame)
                result[ts] = filename
            frame_idx += 1

        cap.release()
        return result
