
import base64
import json
import logging
import math
import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from services.image_preprocessing import preprocess_food_image
from routers.food_recognition import (
    GROQ_MODEL_NAME,
    _call_groq_vision,
    _read_uploaded_image,
)

router = APIRouter(
    prefix="/freshness",
    tags=["Food Freshness Assessment"],
)

logger = logging.getLogger(__name__)


def extract_uploaded_image_features(encoded_image: str) -> dict:
    """Extract OpenCV features from a validated base64 JPEG."""
    image_bytes = base64.b64decode(encoded_image, validate=True)
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".jpg",
            delete=False,
        ) as temp_file:
            temp_file.write(image_bytes)
            temp_path = temp_file.name

        _, features = preprocess_food_image(temp_path)
        return features

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


FRESHNESS_PROMPT = """
You assess the apparent visual freshness of food from a photograph
for a student food-intelligence project.

Return exactly one valid JSON object without Markdown fences:
{
  "food_name": "identified food or unknown",
  "apparent_freshness": "Fresh",
  "confidence_score": 75,
  "confidence_explanation": "Brief explanation of the visual evidence",
  "visible_evidence": ["visible observation"],
  "concerns": [],
  "recommendations": ["practical recommendation"],
  "limitations": ["uncertainty or limitation"]
}

Rules:
- apparent_freshness must be exactly one of:
  "Fresh", "Moderately Fresh", "Possibly Spoiled", "Inconclusive".
- confidence_score must be a number from 0 to 100.
- It represents estimated confidence in visual classification,
  NOT the probability that food is safe to eat.
- Do not present the score as scientifically calibrated.
- Explain uncertainty in confidence_explanation.
- Describe only visible evidence such as discoloration, visible mold,
  wilting, bruising, or unusual surface changes.
- Do not claim to detect invisible microorganisms.
- Do not claim that a photograph proves food is safe to eat.
- Do not infer storage temperature, age, smell, or handling history.
- Use "Inconclusive" if visual evidence is insufficient.
- If visible mold or serious spoilage signs appear, advise not to taste
  the food and recommend discarding it.
- For uncertain cases, recommend checking storage history and reliable
  food-safety guidance.
- Every list field must be a list of strings.
- Return JSON only.
"""


SAFETY_GUIDANCE = {
    "Fresh": {
        "message": (
            "The food appears visually fresh, but its safety cannot be "
            "confirmed from an image. Follow proper storage and cooking "
            "guidance."
        ),
        "action": (
            "Check storage history and required cooking conditions."
        ),
    },
    "Moderately Fresh": {
        "message": (
            "Visible quality changes may be present. An image cannot "
            "determine whether the food is safe to consume."
        ),
        "action": (
            "Check the food's storage history, expiry information where "
            "applicable, and reliable food-safety guidance."
        ),
    },
    "Possibly Spoiled": {
        "message": (
            "Possible visible spoilage indicators were identified. "
            "Do not taste the food to test it."
        ),
        "action": (
            "Avoid consuming food with suspected spoilage. Discard it "
            "when spoilage is suspected, following local food-safety guidance."
        ),
    },
    "Inconclusive": {
        "message": (
            "There is insufficient visual evidence to classify freshness "
            "reliably."
        ),
        "action": (
            "Do not use this image result to decide that the food is safe. "
            "Check storage history and reliable food-safety guidance."
        ),
    },
}


@router.post("/assess")
async def assess_freshness(
    file: UploadFile = File(..., description="Upload a food image"),
):
    """Assess apparent freshness and return OpenCV image features."""

    try:
        # Read and validate the image using the existing shared helper.
        encoded_image = await _read_uploaded_image(file)

        # Extract visual descriptors using the existing OpenCV service.
        visual_features = extract_uploaded_image_features(encoded_image)

        # Ask the vision model to assess the original validated image.
        response_text = _call_groq_vision(
            encoded_image=encoded_image,
            system_prompt=FRESHNESS_PROMPT,
            user_prompt=(
                "Assess only the visible condition of the food. "
                "Return the required JSON, including a qualified "
                "visual-classification confidence score."
            ),
        )

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=502,
                detail="The AI returned invalid JSON. Please try again.",
            ) from exc

        if not isinstance(result, dict):
            raise HTTPException(
                status_code=502,
                detail="The AI returned an unexpected response.",
            )

        required_fields = [
            "food_name",
            "apparent_freshness",
            "confidence_score",
            "confidence_explanation",
            "visible_evidence",
            "concerns",
            "recommendations",
            "limitations",
        ]

        if any(field not in result for field in required_fields):
            raise HTTPException(
                status_code=502,
                detail="The AI response is missing required fields.",
            )

        label = result["apparent_freshness"]

        if not isinstance(label, str) or label not in SAFETY_GUIDANCE:
            raise HTTPException(
                status_code=502,
                detail="The AI returned an invalid freshness category.",
            )

        confidence = result["confidence_score"]

        if (
            isinstance(confidence, bool)
            or not isinstance(confidence, (int, float))
            or not math.isfinite(confidence)
            or not 0 <= confidence <= 100
        ):
            raise HTTPException(
                status_code=502,
                detail="The AI returned an invalid confidence score.",
            )

        for field in ("food_name", "confidence_explanation"):
            if not isinstance(result[field], str):
                raise HTTPException(
                    status_code=502,
                    detail=f"The AI returned an invalid {field} field.",
                )

        for field in (
            "visible_evidence",
            "concerns",
            "recommendations",
            "limitations",
        ):
            if (
                not isinstance(result[field], list)
                or not all(
                    isinstance(item, str) for item in result[field]
                )
            ):
                raise HTTPException(
                    status_code=502,
                    detail=f"The AI returned an invalid {field} field.",
                )

        return {
            "success": True,
            "model": GROQ_MODEL_NAME,
            "assessment": result,
            "visual_features": visual_features,
            "safety_guidance": SAFETY_GUIDANCE[label],
            "safety_notice": (
                "A photograph cannot establish whether food is safe to eat. "
                "The confidence score is the model's estimate of its visual "
                "classification confidence, not a probability of food safety. "
                "Do not taste food to test freshness."
            ),
        }

    except HTTPException:
        raise

    except (UnidentifiedImageError, Image.DecompressionBombError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or unsafe image. Upload a valid image.",
        ) from None

    except OSError:
        raise HTTPException(
            status_code=400,
            detail="The image could not be decoded.",
        ) from None

    except Exception:
        logger.exception("Freshness assessment failed.")
        raise HTTPException(
            status_code=503,
            detail="Freshness assessment failed. Check server logs.",
        ) from None

    finally:
        await file.close()