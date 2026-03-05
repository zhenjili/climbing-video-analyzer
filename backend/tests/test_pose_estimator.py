import numpy as np
import pytest

from app.services.pose_estimator import PoseEstimator, PoseFrame


def test_pose_frame_has_landmarks():
    landmarks = np.random.rand(33, 4)
    frame = PoseFrame(frame_index=0, landmarks=landmarks)
    assert frame.landmarks.shape == (33, 4)
    assert frame.frame_index == 0


def test_estimate_single_frame():
    estimator = PoseEstimator()
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    result = estimator.estimate_frame(image, frame_index=0)
    assert result is None or isinstance(result, PoseFrame)


def test_estimate_video_returns_list(tmp_path):
    import cv2

    video_path = tmp_path / "test.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))
    for _ in range(10):
        writer.write(np.zeros((480, 640, 3), dtype=np.uint8))
    writer.release()

    estimator = PoseEstimator()
    frames, fps, total_frames = estimator.estimate_video(str(video_path))
    assert isinstance(frames, list)
    assert fps == 30.0
    assert total_frames == 10
