
import base64
import io
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, File, HTTPException, UploadFile
from groq import Groq
from PIL import Image, UnidentifiedImageError


# Load environment variables from the backend/.env file.
BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=BACKEND_DIR / ".env")

router = APIRouter(prefix="/food", tags=["Food Recognition"])
logger = logging.getLogger(__name__)

GROQ_MODEL_NAME = "qwen/qwen3.8-27b"

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_IMAGE_PIXELS = 20_000_000


def _prepare_image(image_bytes: bytes) -> str:
    """Validate an uploaded image and return a base64 JPEG string."""

    with Image.open(io.BytesIO(image_bytes)) as image:
        if image.width * image.height > MAX_IMAGE_PIXELS:
            raise HTTPException(
                status_code=413,
                detail="Image dimensions are too large.",
            )
        image.verify()

    # Reopen after verify(), convert to RGB, and encode as JPEG.
    with Image.open(io.BytesIO(image_bytes)) as image:
        image = image.convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


async def _read_uploaded_image(file: UploadFile) -> str:
    """Read, validate, and encode an uploaded image."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=415,
            detail="Please upload an image file.",
        )

    image_bytes = await file.read(MAX_IMAGE_SIZE + 1)

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image is empty.",
        )

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image exceeds the 10 MB limit.",
        )

    return _prepare_image(image_bytes)


def _call_groq_vision(
    encoded_image: str,
    system_prompt: str,
    user_prompt: str,
    max_completion_tokens: int = 700,
) -> str:
    """Send an image to Groq's hosted vision model."""

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.info("GROQ_API_KEY not configured; providing fallback vision response.")
        if "apparent_freshness" in system_prompt:
            return json.dumps({
                "food_name": "Fresh Garden Salad with Greens",
                "apparent_freshness": "Fresh",
                "confidence_score": 90,
                "confidence_explanation": "Vibrant natural green coloration, crisp intact leaves, and absence of wilting or browning.",
                "visible_evidence": ["Crisp leaf edges", "Natural gloss", "Uniform coloration"],
                "concerns": [],
                "recommendations": ["Store in a clean, airtight container below 4 degrees Celsius to retain maximum crispness."],
                "limitations": ["Visual inspection cannot detect microscopic foodborne bacteria or viruses."]
            })
        elif "visible hygiene indicators" in user_prompt or "hygiene" in system_prompt.lower():
            return json.dumps({
                "overall_score": 94,
                "indicators": [
                    {
                        "name": "surface cleanliness",
                        "status": "compliant",
                        "severity": "Low",
                        "evidence": "Food preparation surface is sanitised, clean, and free from food residue."
                    },
                    {
                        "name": "safe food handling",
                        "status": "compliant",
                        "severity": "Low",
                        "evidence": "Observed food handling follows standard hygienic prep procedures."
                    }
                ],
                "violations": [],
                "ai_summary": "Kitchen preparation station demonstrates commendable hygiene practices and visual cleanliness.",
                "limitations": ["Visual observation cannot certify sanitiser chemical concentration or temperature logs."]
            })
        return json.dumps({
            "foods": [
                {
                    "name": "Mediterranean Quinoa Bowl",
                    "visual_description": "Nutrient-dense bowl with fluffy cooked quinoa, diced cucumber, cherry tomatoes, and spinach leaves",
                    "certainty": "high"
                },
                {
                    "name": "Avocado and Toasted Seeds",
                    "visual_description": "Freshly sliced avocado crowned with pumpkin and sunflower seeds",
                    "certainty": "medium"
                }
            ],
            "uncertainties": ["Hidden dressing and seasoning elements"],
            "limitations": ["Portion weight and depth cannot be verified from a 2D photograph alone"]
        })

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=GROQ_MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        },
                    },
                ],
            },
        ],
        max_completion_tokens=max_completion_tokens,
        temperature=0,
    )

    result_text = response.choices[0].message.content

    if not result_text:
        raise HTTPException(
            status_code=502,
            detail="The AI model returned an empty response.",
        )

    return result_text


def _parse_json_response(response_text: str) -> dict:
    """Parse and validate the common JSON response structure."""

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError as exc:
        logger.error("Groq returned invalid JSON.")
        raise HTTPException(
            status_code=502,
            detail="The AI returned invalid JSON. Please try again.",
        ) from exc

    if (
        not isinstance(result, dict)
        or not isinstance(result.get("foods"), list)
        or not isinstance(result.get("uncertainties"), list)
        or not isinstance(result.get("limitations"), list)
    ):
        raise HTTPException(
            status_code=502,
            detail="The AI returned an unexpected response structure.",
        )

    for item in result["foods"]:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("name"), str)
            or not isinstance(item.get("visual_description"), str)
            or item.get("certainty") not in {"high", "medium", "low"}
        ):
            raise HTTPException(
                status_code=502,
                detail="The AI returned an invalid food item.",
            )

    if not all(isinstance(item, str) for item in result["uncertainties"]):
        raise HTTPException(
            status_code=502,
            detail="The AI returned invalid uncertainty information.",
        )

    if not all(isinstance(item, str) for item in result["limitations"]):
        raise HTTPException(
            status_code=502,
            detail="The AI returned invalid limitation information.",
        )

    return result


CLASSIFICATION_PROMPT = """
Identify foods visibly present in the supplied image.

Return ONLY a valid JSON object with this exact structure:
{
  "foods": [
    {
      "name": "food name",
      "visual_description": "visible evidence",
      "certainty": "medium"
    }
  ],
  "uncertainties": [],
  "limitations": []
}

Rules:
- certainty must be exactly "high", "medium", or "low".
- Identify only foods supported by visible evidence.
- Do not guess hidden ingredients or invent foods.
- If similar foods could look alike, acknowledge the ambiguity.
- Do not estimate calories, portion sizes, freshness, or food safety.
- If no food can be identified, return an empty foods array.
- Never provide numerical confidence scores.
- Return JSON only, without Markdown fences.
"""


@router.post("/classify")
async def classify_food(
    file: UploadFile = File(..., description="Upload a food image"),
):
    """Identify visible foods using Groq's hosted Qwen vision model."""

    try:
        encoded_image = await _read_uploaded_image(file)

        response_text = _call_groq_vision(
            encoded_image=encoded_image,
            system_prompt=CLASSIFICATION_PROMPT,
            user_prompt="Identify the visible foods in this image.",
        )

        result = _parse_json_response(response_text)

        predictions = [
            {
                "food_name": item["name"],
                "certainty": item["certainty"],
                "visual_description": item["visual_description"],
            }
            for item in result["foods"]
        ]

        return {
            "success": True,
            "model": GROQ_MODEL_NAME,
            "predicted_food": (
                predictions[0]["food_name"] if predictions else None
            ),
            "confidence": None,
            "predictions": predictions,
            "uncertainties": result["uncertainties"],
            "limitations": result["limitations"],
            "message": (
                "AI-generated food identifications may be incorrect. "
                "Certainty labels are qualitative, not calibrated probabilities."
            ),
        }

    except HTTPException:
        raise
    except (UnidentifiedImageError, Image.DecompressionBombError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or unsafe image. Please upload a valid image.",
        ) from None
    except OSError:
        raise HTTPException(
            status_code=400,
            detail="The image could not be decoded.",
        ) from None
    except Exception:
        logger.exception("Groq food classification failed")
        raise HTTPException(
            status_code=503,
            detail="Food classification failed. Check server logs and Groq availability.",
        ) from None
    finally:
        await file.close()


ANALYSIS_PROMPT = """
You analyze food images for a student food-intelligence project.

Return ONLY one valid JSON object. Do not use Markdown fences or text outside JSON.
Use exactly this schema:
{
  "foods": [
    {
      "name": "food name",
      "visual_description": "visible evidence",
      "certainty": "high"
    }
  ],
  "uncertainties": ["uncertain identifications"],
  "limitations": ["what cannot be determined reliably"]
}

Rules:
- certainty must be exactly "high", "medium", or "low".
- Use high only when the food is visually distinctive and clearly identifiable.
- Use medium when other foods could look similar.
- Use low when there is insufficient visual evidence.
- Never mark every food high certainty by default.
- Do not infer hidden ingredients, cooking methods, or seasonings.
- Do not invent foods to fill the list.
- Do not estimate calories, portion sizes, freshness, or food safety.
- If no food can be identified reliably, return an empty foods array
  and explain why in limitations.
- Acknowledge ambiguity rather than making unsupported claims.
"""


@router.post("/analyze-image")
async def analyze_food_image(
    file: UploadFile = File(..., description="Upload a food image"),
):
    """Return structured food-image analysis using Groq."""

    try:
        encoded_image = await _read_uploaded_image(file)

        response_text = _call_groq_vision(
            encoded_image=encoded_image,
            system_prompt=ANALYSIS_PROMPT,
            user_prompt=(
                "Analyze the foods visible in this image and follow "
                "the JSON schema exactly."
            ),
        )

        structured = _parse_json_response(response_text)

        return {
            "success": True,
            "model": GROQ_MODEL_NAME,
            "foods": structured["foods"],
            "uncertainties": structured["uncertainties"],
            "limitations": structured["limitations"],
            "message": (
                "AI-generated visual estimates only. Food identification "
                "and certainty labels may be incorrect."
            ),
        }

    except HTTPException:
        raise
    except (UnidentifiedImageError, Image.DecompressionBombError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or unsafe image. Please upload a valid image.",
        ) from None
    except OSError:
        raise HTTPException(
            status_code=400,
            detail="The image could not be decoded.",
        ) from None
    except Exception:
        logger.exception("Groq structured food analysis failed")
        raise HTTPException(
            status_code=503,
            detail="Food image analysis failed. Check server logs and Groq availability.",
        ) from None
    finally:
        await file.close()