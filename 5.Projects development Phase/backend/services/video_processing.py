
import os
import tempfile

import cv2
from fastapi import HTTPException


MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB


def extract_video_frames(
    video_bytes: bytes,
    interval_seconds: int = 5,
    max_frames: int = 5,
) -> list[dict]:
    """
    Extract representative frames from uploaded video bytes.

    Returns frame timestamps and JPEG image bytes.
    This function does not perform hygiene analysis.
    """

    if not video_bytes:
        raise ValueError("The uploaded video is empty.")

    if len(video_bytes) > MAX_VIDEO_SIZE:
        raise ValueError("Video exceeds the 50 MB limit.")

    if interval_seconds < 1:
        raise ValueError("interval_seconds must be at least 1.")

    if max_frames < 1 or max_frames > 10:
        raise ValueError("max_frames must be between 1 and 10.")

    temp_path = None
    capture = None
    frames = []

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".mp4",
            delete=False,
        ) as temp_file:
            temp_file.write(video_bytes)
            temp_path = temp_file.name

        capture = cv2.VideoCapture(temp_path)

        if not capture.isOpened():
            raise ValueError(
                "Could not open this video. Please upload a supported video file."
            )

        fps = capture.get(cv2.CAP_PROP_FPS)
        frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT)

        if fps <= 0 or frame_count <= 0:
            raise ValueError("The video metadata is invalid or unreadable.")

        duration_seconds = frame_count / fps
        timestamp = 0.0

        while timestamp < duration_seconds and len(frames) < max_frames:
            capture.set(
                cv2.CAP_PROP_POS_MSEC,
                timestamp * 1000,
            )
            success, frame = capture.read()

            if success:
                encoded_ok, buffer = cv2.imencode(
                    ".jpg",
                    frame,
                    [cv2.IMWRITE_JPEG_QUALITY, 85],
                )

                if encoded_ok:
                    frames.append({
                        "timestamp_seconds": round(timestamp, 2),
                        "image_bytes": buffer.tobytes(),
                    })

            timestamp += interval_seconds

        if not frames:
            raise ValueError("No readable frames were extracted from the video.")

        return frames

    finally:
        if capture is not None:
            capture.release()

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)