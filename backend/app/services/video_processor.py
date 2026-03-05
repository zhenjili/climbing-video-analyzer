import os
import subprocess
import textwrap

import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from app.models.schemas import ImprovementFrame
from app.services.pose_estimator import PoseFrame

POSE_CONNECTIONS = mp.solutions.pose.POSE_CONNECTIONS


def normalize_video(input_path: str) -> str:
    """Apply rotation metadata so OpenCV reads frames in correct orientation."""
    normalized = input_path + ".normalized.mp4"
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-i", input_path,
            "-c:v", "libx264", "-preset", "fast",
            "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            normalized,
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        return input_path
    return normalized


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

        # Re-encode to H.264 for browser compatibility, merge audio from original
        self._reencode_h264(output_path, original_path=input_path)

    @staticmethod
    def _reencode_h264(path: str, original_path: str | None = None) -> None:
        tmp = path + ".tmp.mp4"
        cmd = ["ffmpeg", "-y", "-i", path]
        if original_path:
            cmd += ["-i", original_path]
        cmd += [
            "-c:v", "libx264", "-preset", "fast",
            "-crf", "23", "-pix_fmt", "yuv420p",
        ]
        if original_path:
            cmd += ["-map", "0:v:0", "-map", "1:a:0?", "-c:a", "aac", "-b:a", "128k"]
        else:
            cmd += ["-an"]
        cmd += ["-movflags", "+faststart", tmp]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"ffmpeg failed (exit {result.returncode}): {result.stderr.decode(errors='replace')}"
            )
        os.replace(tmp, path)

    @staticmethod
    def _put_chinese_text(
        frame: np.ndarray, text: str, position: tuple[int, int],
        font_size: int = 24, color: tuple[int, int, int] = (255, 255, 255),
        bg_color: tuple[int, int, int, int] = (0, 0, 0, 180),
    ) -> np.ndarray:
        """Draw Chinese text on a frame using PIL (OpenCV putText doesn't support CJK)."""
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        overlay = Image.new("RGBA", pil_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Look for bundled font first, then system fonts
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        font_paths = [
            os.path.join(base_dir, "fonts", "NotoSansSC.ttf"),
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
        ]
        font = ImageFont.load_default()
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    font = ImageFont.truetype(fp, font_size)
                    print(f"[overlay] Loaded font: {fp}")
                except Exception as e:
                    print(f"[overlay] Font load error for {fp}: {e}")
                    continue
                break

        # Wrap text to fit within frame width
        max_chars = max(10, (frame.shape[1] - position[0] * 2) // (font_size // 2))
        lines = []
        for paragraph in text.split("\n"):
            lines.extend(textwrap.wrap(paragraph, width=max_chars) or [""])

        # Calculate text block size
        line_height = font_size + 6
        block_height = len(lines) * line_height + 20
        block_width = frame.shape[1] - position[0] * 2

        # Draw semi-transparent background
        x, y = position
        draw.rectangle(
            [x - 10, y - 10, x + block_width + 10, y + block_height],
            fill=bg_color,
        )

        # Draw text lines
        for i, line in enumerate(lines):
            draw.text((x, y + i * line_height), line, font=font, fill=(*color, 255))

        # Composite overlay onto original image
        pil_img = pil_img.convert("RGBA")
        pil_img = Image.alpha_composite(pil_img, overlay)
        return cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)

    def overlay_text_on_video(
        self,
        video_path: str,
        improvement_frames: list[ImprovementFrame],
        display_duration: float = 3.0,
    ) -> None:
        """Overlay improvement text onto the video at corresponding timestamps.
        Modifies the video file in-place."""
        if not improvement_frames:
            print("[overlay] No improvement frames, skipping")
            return

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"[overlay] Video: {video_path}, fps={fps}, {width}x{height}")
        print(f"[overlay] Improvement frames: {len(improvement_frames)}")
        for imp in improvement_frames:
            print(f"[overlay]   time_sec={imp.time_sec}, issue={imp.issue[:30]}...")

        if fps <= 0:
            cap.release()
            print("[overlay] fps <= 0, skipping")
            return

        # Build time ranges: each improvement shows for display_duration seconds
        half = display_duration / 2.0
        text_ranges = []
        for idx, imp in enumerate(improvement_frames):
            start = max(0, imp.time_sec - half)
            end = imp.time_sec + half
            label = f"[{idx + 1}/{len(improvement_frames)}] "
            text = f"{label}问题: {imp.issue}\n建议: {imp.suggestion}"
            text_ranges.append((start, end, text))
            print(f"[overlay] Range {idx}: {start:.2f}s - {end:.2f}s")

        tmp_path = video_path + ".overlay.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(tmp_path, fourcc, fps, (width, height))

        if not writer.isOpened():
            print(f"[overlay] ERROR: VideoWriter failed to open {tmp_path}")
            cap.release()
            return

        # Adaptive font size based on video resolution
        font_size = max(16, min(32, height // 25))
        margin = max(10, width // 40)
        y_position = height - max(120, height // 5)
        print(f"[overlay] font_size={font_size}, margin={margin}, y_position={y_position}")

        frame_idx = 0
        overlaid_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            current_time = frame_idx / fps

            # Check if any improvement text should be displayed
            for start, end, text in text_ranges:
                if start <= current_time <= end:
                    frame = self._put_chinese_text(
                        frame, text,
                        position=(margin, y_position),
                        font_size=font_size,
                    )
                    overlaid_count += 1
                    break  # Only show one at a time

            writer.write(frame)
            frame_idx += 1

        cap.release()
        writer.release()

        print(f"[overlay] Processed {frame_idx} frames, overlaid text on {overlaid_count} frames")

        if overlaid_count == 0:
            print("[overlay] WARNING: No frames were overlaid! Removing tmp file.")
            os.remove(tmp_path)
            return

        # Re-encode with H.264, keep audio from the original skeleton video
        self._reencode_h264(tmp_path, original_path=video_path)
        os.replace(tmp_path, video_path)
        print(f"[overlay] Done, replaced {video_path}")

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
