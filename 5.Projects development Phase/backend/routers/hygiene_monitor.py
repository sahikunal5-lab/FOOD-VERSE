
import base64
import json
import logging
import math

from fastapi import APIRouter, File, HTTPException, UploadFile

from routers.food_recognition import (
    GROQ_MODEL_NAME,
    _call_groq_vision,
    _read_uploaded_image,
)
from services.video_processing import (
    MAX_VIDEO_SIZE,
    extract_video_frames,
)

router = APIRouter(
    prefix="/hygiene",
    tags=["Restaurant Hygiene Monitoring"],
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a visual restaurant hygiene observation assistant.
Return only valid JSON. Do not claim to certify food safety.
Report only what is visibly supported by the image.
If an indicator cannot be judged, mark it as unknown.
Do not assume that gloves or hair coverings are always legally required;
evaluate them according to the supplied context rules.
"""

CONTEXT_RULES = """
Inspect these visible indicators:
1. Gloves or appropriate hand protection, when applicable.
2. Hair covering, when applicable.
3. Visible cleanliness of food-contact surfaces and floors.
4. Potentially unsafe food handling.
5. Distracting phone use during food preparation, if visible.

Use severity values High, Medium, or Low for observed concerns.
Do not infer unseen events from a single image.
"""


def _parse_hygiene_result(response_text: str) -> dict:
    """Parse and validate the basic structure of an AI hygiene response."""

    cleaned = response_text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail="The AI returned invalid hygiene JSON.",
        ) from exc

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=502,
            detail="The AI response must be a JSON object.",
        )

    score = result.get("overall_score")

    if (
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not math.isfinite(score)
        or not 0 <= score <= 100
    ):
        raise HTTPException(
            status_code=502,
            detail="The AI returned an invalid overall_score.",
        )

    for field in ("indicators", "violations", "limitations"):
        if not isinstance(result.get(field), list):
            raise HTTPException(
                status_code=502,
                detail=f"The AI returned invalid {field}.",
            )

    return result


def _build_hygiene_prompt(timestamp: float | None = None) -> str:
    """Build the same structured analysis prompt for images and video frames."""

    timestamp_text = (
        f"\nVideo timestamp: {timestamp:.2f} seconds."
        if timestamp is not None
        else ""
    )

    return f"""
    TASK: Analyze the visible hygiene indicators in this kitchen image.
    {timestamp_text}

    CONTEXT RULES:
    {CONTEXT_RULES}

    Return exactly one JSON object with this structure:
    {{
      "overall_score": 0,
      "indicators": [
        {{
          "name": "visible cleanliness",
          "status": "compliant",
          "severity": "Low",
          "evidence": "Describe visible evidence"
        }}
      ],
      "violations": [
        {{
          "violation": "Description of visible concern",
          "severity": "Medium",
          "location": "Visible area or unknown",
          "reason": "Why this may need attention"
        }}
      ],
      "ai_summary": "Short summary",
      "limitations": ["What cannot be verified"]
    }}

    Rules:
    - overall_score must be a number from 0 to 100.
    - Indicator status must be compliant, concern, or unknown.
    - Severity must be High, Medium, or Low.
    - Do not invent observations.
    - Return an empty violations list if no violations are visible.
    - This is a preliminary visual observation, not a formal inspection.
    """


async def _analyze_one_frame(
    image_bytes: bytes,
    timestamp: float | None = None,
) -> dict:
    """Send one JPEG frame to the vision model and validate its result."""

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    prompt = _build_hygiene_prompt(timestamp)

    try:
        response_text = _call_groq_vision(
            encoded_image,
            SYSTEM_PROMPT,
            prompt,
        )
        return _parse_hygiene_result(response_text)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Hygiene frame analysis failed.")
        raise HTTPException(
            status_code=502,
            detail="Hygiene frame analysis failed. Check the model service.",
        ) from exc


@router.post("/analyze-image")
async def analyze_hygiene_image(file: UploadFile = File(...)):
    """Analyze one kitchen image for visible hygiene indicators."""

    encoded_image = await _read_uploaded_image(file)

    try:
        response_text = _call_groq_vision(
            encoded_image,
            SYSTEM_PROMPT,
            _build_hygiene_prompt(),
        )
        result = _parse_hygiene_result(response_text)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Hygiene image analysis failed.")
        raise HTTPException(
            status_code=502,
            detail="Hygiene image analysis failed. Check the model service.",
        ) from exc

    return {
        "success": True,
        "model": GROQ_MODEL_NAME,
        "analysis_type": "single_image",
        "overall_score": round(result["overall_score"], 2),
        "indicators": result["indicators"],
        "violations": result["violations"],
        "ai_summary": str(result.get("ai_summary", "")),
        "limitations": result["limitations"],
        "notice": (
            "This AI-generated visual assessment is preliminary. "
            "It cannot certify restaurant hygiene or food safety."
        ),
    }


@router.post("/analyze-video")
async def analyze_hygiene_video(file: UploadFile = File(...)):
    """Analyze selected frames from a kitchen video."""

    video_bytes = await file.read(MAX_VIDEO_SIZE + 1)

    if not video_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded video is empty.",
        )

    if len(video_bytes) > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Video exceeds the 50 MB upload limit.",
        )

    try:
        frames = extract_video_frames(
            video_bytes,
            interval_seconds=5,
            max_frames=5,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Video frame extraction failed.")
        raise HTTPException(
            status_code=400,
            detail="Could not process this video. Try a supported video file.",
        ) from exc
    finally:
        await file.close()

    frame_results = []

    # Analyze each selected frame separately.
    for frame in frames:
        timestamp = frame["timestamp_seconds"]

        result = await _analyze_one_frame(
            frame["image_bytes"],
            timestamp,
        )

        frame_results.append(
            {
                "timestamp_seconds": timestamp,
                "overall_score": round(result["overall_score"], 2),
                "indicators": result["indicators"],
                "violations": result["violations"],
                "ai_summary": str(result.get("ai_summary", "")),
                "limitations": result["limitations"],
            }
        )

    # Give every analyzed frame equal weight in the overall score.
    overall_score = sum(
        item["overall_score"] for item in frame_results
    ) / len(frame_results)

    # Keep the timestamp for every reported violation.
    timestamped_violations = []

    for frame_result in frame_results:
        for violation in frame_result["violations"]:
            timestamped_violations.append(
                {
                    "timestamp_seconds": frame_result["timestamp_seconds"],
                    **(
                        violation
                        if isinstance(violation, dict)
                        else {"violation": str(violation)}
                    ),
                }
            )

    limitations = sorted(
        {
            limitation
            for item in frame_results
            for limitation in item["limitations"]
            if isinstance(limitation, str)
        }
    )

    return {
        "success": True,
        "model": GROQ_MODEL_NAME,
        "analysis_type": "video",
        "frames_analyzed": len(frame_results),
        "overall_score": round(overall_score, 2),
        "frame_results": frame_results,
        "violations": timestamped_violations,
        "ai_summary": (
            f"Analyzed {len(frame_results)} selected video frames. "
            "Review the frame-level results and timestamps for details."
        ),
        "limitations": limitations + [
            "Only selected frames were analyzed; events between frames may be missed.",
            "The score is an AI-generated estimate, not an official compliance rating.",
            "A video cannot establish all food safety conditions.",
        ],
        "notice": (
            "This preliminary visual assessment cannot certify "
            "restaurant hygiene or food safety."
        ),
    }