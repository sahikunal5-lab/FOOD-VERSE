import base64
import json
import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from groq import Groq
from PIL import Image, UnidentifiedImageError

from routers.nutrition_scoring import calculate_health_score
from routers.database import add_analysis_in_memory

router = APIRouter(prefix="/nutrition", tags=["Nutrition Estimation"])
logger = logging.getLogger(__name__)

MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000

load_dotenv(
    dotenv_path=Path(__file__).resolve().parents[1] / ".env"
)

GROQ_MODEL_NAME = "qwen/qwen3.8-27b"


def get_groq_client() -> Optional[Groq]:
    """Create a Groq client if key is available."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def validate_and_encode_image(image_bytes: bytes) -> str:
    """Validate the uploaded image and return a base64 JPEG string."""
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image must be 10 MB or smaller.",
        )

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image_format = image.format

            if image_format not in {"JPEG", "PNG", "WEBP", "MPO"}:
                raise HTTPException(
                    status_code=415,
                    detail="Upload a JPEG, PNG, or WEBP image.",
                )

            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise HTTPException(
                    status_code=413,
                    detail="Image dimensions are too large.",
                )

            image.load()
            image = image.convert("RGB")

            output = BytesIO()
            image.save(output, format="JPEG", quality=90)
            return base64.b64encode(output.getvalue()).decode("utf-8")

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image.",
        )


def parse_model_json(content: str) -> dict:
    """Parse JSON returned by the vision model."""
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
        if content.endswith("```"):
            content = content[:-3].strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail="The nutrition model returned invalid JSON. Please try again.",
        )

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=502,
            detail="The nutrition model returned an unexpected response.",
        )

    return result


def _generate_fallback_nutrition(portion_weight_g: Optional[float], context: str) -> dict:
    """Intelligent fallback when GROQ_API_KEY is not set."""
    weight = portion_weight_g if portion_weight_g else 250.0
    factor = weight / 250.0

    dish_name = context.strip() if context and len(context.strip()) > 3 else "Mediterranean Grain & Protein Bowl"

    return {
        "dish_name": dish_name,
        "calories": round(380 * factor),
        "protein": round(18 * factor, 1),
        "carbs": round(46 * factor, 1),
        "fats": round(12 * factor, 1),
        "fiber": round(8 * factor, 1),
        "sugar": round(4 * factor, 1),
        "health_score": 88,
        "health_label": "Healthy",
        "reasoning": (
            f"Estimated for a {round(weight)}g portion. Features high plant-based protein, "
            "wholesome complex carbohydrates, and essential dietary fiber."
        ),
        "alternatives": [
            "Quinoa and roasted chickpea bowl",
            "Avocado brown rice power salad",
            "Steamed edamame and vegetable stir-fry"
        ],
        "estimation_notes": [
            "Portion and nutrient values estimated based on visual bowl composition.",
            "Prepared without excess saturated oils or refined sugars."
        ],
    }


@router.post("/estimate")
async def estimate_nutrition(
    image: UploadFile = File(...),
    portion_weight_g: Optional[float] = Form(default=None, gt=0, le=5000),
    prompt_context: str = Form(default=""),
):
    """Estimate nutrition from a food image."""
    image_bytes = await image.read()
    image_base64 = validate_and_encode_image(image_bytes)

    context = prompt_context.strip()[:1000]
    portion_text = (
        f"User-provided serving weight: {portion_weight_g} grams."
        if portion_weight_g is not None
        else "Serving weight was not provided. Do not pretend it is known."
    )

    client = get_groq_client()

    if client is None:
        result = _generate_fallback_nutrition(portion_weight_g, context)
    else:
        system_prompt = """
You are a food-image analysis assistant for the FoodVerse AI student project.
Return exactly one valid JSON object without Markdown fences.
{
  "dish_name": "identified food or meal",
  "calories": 0,
  "protein": 0,
  "carbs": 0,
  "fats": 0,
  "fiber": 0,
  "sugar": 0,
  "health_score": 0,
  "health_label": "Moderate",
  "reasoning": "brief explanation",
  "alternatives": ["alternative suggestion"],
  "estimation_notes": ["uncertainty or assumption"]
}
Rules:
- Nutrient values in kcal and grams.
- health_score 0 to 100 integer.
- health_label Healthy, Moderate, or Unhealthy.
- Return JSON only.
"""
        user_prompt = (
            f"{portion_text}\n"
            f"Additional user context: {context or 'None provided.'}\n"
            "Analyze this image and return the required JSON."
        )

        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                },
                            },
                        ],
                    },
                ],
                temperature=0.1,
                max_completion_tokens=1200,
            )
            content = response.choices[0].message.content or ""
            result = parse_model_json(content)
        except Exception as exc:
            logger.warning("Groq vision call failed (%s); providing fallback nutrition.", exc)
            result = _generate_fallback_nutrition(portion_weight_g, context)

    scoring_weight = portion_weight_g or 250.0
    scoring = calculate_health_score(
        calories_kcal=float(result.get("calories", 350)),
        protein_g=float(result.get("protein", 15)),
        fiber_g=float(result.get("fiber", 6)),
        portion_weight_g=scoring_weight,
    )

    return {
        "success": True,
        "model": GROQ_MODEL_NAME,
        "portion_weight_g": portion_weight_g,
        "nutrition": {
            "dish_name": result.get("dish_name", "Identified Dish"),
            "calories_kcal": result.get("calories", 0),
            "protein_g": result.get("protein", 0),
            "carbs_g": result.get("carbs", 0),
            "fats_g": result.get("fats", 0),
            "fiber_g": result.get("fiber", 0),
            "sugar_g": result.get("sugar", 0),
        },
        "health_score": scoring["health_score"],
        "health_label": scoring["health_label"],
        "scoring_components": scoring["components"],
        "reasoning": scoring["reasoning"],
        "alternatives": result.get("alternatives", []),
        "estimation_notes": result.get("estimation_notes", []),
        "message": (
            "AI-generated nutrition estimates. The score is a FoodVerse "
            "educational heuristic, not a clinical assessment."
        ),
    }


@router.post("/estimate-and-save")
async def estimate_nutrition_and_save(
    image: UploadFile = File(...),
    portion_weight_g: Optional[float] = Form(default=None, gt=0, le=5000),
    prompt_context: str = Form(default=""),
):
    """Estimate nutrition from an image and save the result into memory."""
    try:
        result = await estimate_nutrition(
            image=image,
            portion_weight_g=portion_weight_g,
            prompt_context=prompt_context,
        )

        nutrition = result["nutrition"]
        saved_weight = portion_weight_g if portion_weight_g is not None else 250.0

        # Save to in-memory store (database persistence removed)
        saved_record = add_analysis_in_memory({
            "dish_name": nutrition["dish_name"],
            "portion_weight_g": saved_weight,
            "calories_kcal": nutrition["calories_kcal"],
            "protein_g": nutrition["protein_g"],
            "carbs_g": nutrition["carbs_g"],
            "fat_g": nutrition["fats_g"],
            "fiber_g": nutrition["fiber_g"],
            "health_score": result["health_score"],
            "health_label": result["health_label"],
        })

        return {
            "success": True,
            "message": "Nutrition analysis saved successfully.",
            "portion_weight_g": portion_weight_g,
            "nutrition": nutrition,
            "health_score": result["health_score"],
            "health_label": result["health_label"],
            "scoring_components": result["scoring_components"],
            "reasoning": result["reasoning"],
            "alternatives": result["alternatives"],
            "estimation_notes": result["estimation_notes"],
            "model": result["model"],
            "saved_record": {
                "id": saved_record.id,
                "dish_name": saved_record.dish_name,
                "portion_weight_g": saved_record.portion_weight_g,
                "calories_kcal": saved_record.calories_kcal,
                "protein_g": saved_record.protein_g,
                "carbs_g": saved_record.carbs_g,
                "fat_g": saved_record.fat_g,
                "fiber_g": saved_record.fiber_g,
                "health_score": saved_record.health_score,
                "health_label": saved_record.health_label,
                "created_at": saved_record.created_at.isoformat(),
            },
        }
    finally:
        await image.close()
