"""
Video frame extraction utility.
Extracts the most informative frames from a video clip for AI vision analysis.
"""

import io
import logging
import tempfile
import os
from typing import Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Max frames to send to vision model (balance cost vs coverage)
MAX_FRAMES = 6
# Minimum interval between sampled frames (seconds) to avoid duplicates
MIN_FRAME_INTERVAL_S = 1.0


def _laplacian_variance(frame: np.ndarray) -> float:
    """Sharpness score — higher = clearer frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def extract_frames_from_video(video_bytes: bytes, max_frames: int = MAX_FRAMES) -> list[dict[str, Any]]:
    """
    Extract the sharpest, most spread-out frames from a video.

    Returns a list of image_part dicts:
        [{"mime_type": "image/jpeg", "data": bytes}, ...]
    """
    # Write to a temp file — OpenCV needs a file path
    suffix = ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(video_bytes)
        tmp_path = tmp.name

    try:
        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file — unsupported format or corrupted data.")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_s = total_frames / fps

        logger.info(
            "Video loaded: %.1fs duration, %.0f fps, %d total frames",
            duration_s, fps, total_frames
        )

        # Sample candidate frames evenly across the video
        # More candidates than max_frames so we can pick the sharpest
        num_candidates = min(total_frames, max(max_frames * 4, 24))
        candidate_positions = np.linspace(0, total_frames - 1, num_candidates, dtype=int)

        candidates: list[tuple[int, float, np.ndarray]] = []  # (frame_idx, sharpness, frame)

        for pos in candidate_positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(pos))
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
            sharpness = _laplacian_variance(frame)
            candidates.append((int(pos), sharpness, frame))

        cap.release()

        if not candidates:
            raise ValueError("No readable frames found in video.")

        # Sort by sharpness descending, then pick top frames
        # but ensure they're spread across the video (min interval)
        candidates.sort(key=lambda x: x[1], reverse=True)

        min_frame_gap = int(fps * MIN_FRAME_INTERVAL_S)
        selected: list[tuple[int, np.ndarray]] = []
        used_positions: list[int] = []

        for frame_idx, sharpness, frame in candidates:
            # Check minimum gap from all already-selected frames
            too_close = any(abs(frame_idx - used) < min_frame_gap for used in used_positions)
            if not too_close:
                selected.append((frame_idx, frame))
                used_positions.append(frame_idx)
            if len(selected) >= max_frames:
                break

        # Sort selected by time order for the prompt
        selected.sort(key=lambda x: x[0])

        logger.info(
            "Selected %d frames from video (positions: %s)",
            len(selected),
            [s[0] for s in selected]
        )

        # Encode frames as JPEG bytes
        image_parts = []
        for _idx, frame in selected:
            # Resize large frames to max 1280px wide to control token usage
            h, w = frame.shape[:2]
            if w > 1280:
                scale = 1280 / w
                frame = cv2.resize(frame, (1280, int(h * scale)), interpolation=cv2.INTER_AREA)

            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            image_parts.append({
                "mime_type": "image/jpeg",
                "data": buf.tobytes(),
            })

        return image_parts

    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
