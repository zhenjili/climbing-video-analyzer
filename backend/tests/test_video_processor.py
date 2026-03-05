import cv2
import numpy as np
import pytest

from app.services.pose_estimator import PoseFrame
from app.services.video_processor import VideoProcessor


def test_draw_skeleton_on_frame():
    processor = VideoProcessor()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    landmarks = np.full((33, 4), 0.5)
    landmarks[:, 3] = 1.0
    pose = PoseFrame(frame_index=0, landmarks=landmarks)

    result = processor.draw_skeleton(frame, pose)
    assert result.shape == frame.shape
    assert np.any(result != 0)


def test_process_video_creates_output(tmp_path):
    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "output.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(input_path), fourcc, 30.0, (640, 480))
    for _ in range(10):
        writer.write(np.zeros((480, 640, 3), dtype=np.uint8))
    writer.release()

    processor = VideoProcessor()
    processor.process_video(str(input_path), str(output_path), [])
    assert output_path.exists()
