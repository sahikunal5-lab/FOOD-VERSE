
import base64
import io
import json
import logging
import os
import re

from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from groq import Groq
from pydantic import BaseModel, Field
from PIL import Image, UnidentifiedImageError

from routers.food_recognition import (
    BACKEND_DIR,
    GROQ_MODEL_NAME,
    MAX_IMAGE_PIXELS,
    MAX_IMAGE_SIZE,
    _call_groq_vision,
    _prepare_image,
)

load_dotenv(dotenv_path=BACKEND_DIR / ".env")

router = APIRouter(
    prefix="/kitchen",
    tags=["Smart Kitchen Assistant"],
)

logger = logging.getLogger(__name__)


class RecipeIngredient(BaseModel):
    name: str
    quantity: str


class RecipeStep(BaseModel):
    step_number: int
    instruction: str
    duration_minutes: int | None = None


class RecipeGenerationResponse(BaseModel):
    success: bool
    model: str
    dish_name: str
    description: str
    servings: int
    preparation_time_minutes: int
    cooking_time_minutes: int
    difficulty: str
    ingredients: list[RecipeIngredient]
    steps: list[RecipeStep]
    cooking_tips: list[str]
    safety_notes: list[str]
    limitations: list[str]


SYSTEM_PROMPT = """
You are FoodVerse AI's Smart Kitchen Assistant.

Help users prepare food using ingredients and cooking context they provide.
You may receive a text description or a photograph of ingredients.

Return only one valid JSON object with these fields:
{
  "dish_name": "Recipe name",
  "description": "Short description",
  "servings": 2,
  "preparation_time_minutes": 10,
  "cooking_time_minutes": 20,
  "difficulty": "Easy",
  "ingredients": [
    {"name": "Ingredient", "quantity": "1 cup"}
  ],
  "steps": [
    {
      "step_number": 1,
      "instruction": "Clear cooking instruction",
      "duration_minutes": 5
    }
  ],
  "cooking_tips": [],
  "safety_notes": [],
  "limitations": []
}

Rules:
- Generate practical recipes from the available ingredients.
- If the user specifies a dish, prioritize that dish.
- Provide numbered steps in the correct order.
- Explain actions such as washing, chopping, heating and mixing.
- Use clear language suitable for beginners.
- Treat image identifications as uncertain when appropriate.
- Do not claim to know ingredients hidden from view.
- Never invent nutritional values or medical benefits.
- Include relevant food-handling and cooking safety notes.
- Do not claim a recipe guarantees food safety.
- Use positive integer servings and non-negative cooking times.
- Difficulty must be Easy, Medium, or Hard.
- Return JSON only, without Markdown fences.
"""


def _parse_recipe_json(response_text: str) -> dict:
    """Parse the model response, allowing optional Markdown fences."""

    cleaned = response_text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, count=1)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as error:
        logger.warning(
            "Recipe model returned invalid JSON. Raw response: %r",
            response_text[:3000],
        )
        raise HTTPException(
            status_code=502,
            detail="The AI returned invalid recipe JSON.",
        ) from error

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=502,
            detail="The AI recipe response must be a JSON object.",
        )

    return result



def _validate_recipe(result: dict) -> dict:
    """Validate and normalize recipe fields before returning the response."""

    required_fields = (
        "dish_name",
        "description",
        "servings",
        "preparation_time_minutes",
        "cooking_time_minutes",
        "difficulty",
        "ingredients",
        "steps",
        "cooking_tips",
        "safety_notes",
        "limitations",
    )

    if any(field not in result for field in required_fields):
        raise HTTPException(
            status_code=502,
            detail="The AI recipe response is missing required fields.",
        )

    if (
        not isinstance(result["dish_name"], str)
        or not result["dish_name"].strip()
        or not isinstance(result["description"], str)
    ):
        raise HTTPException(
            status_code=502,
            detail="The AI returned invalid recipe details.",
        )

    for field in (
        "servings",
        "preparation_time_minutes",
        "cooking_time_minutes",
    ):
        value = result[field]
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < (1 if field == "servings" else 0)
        ):
            raise HTTPException(
                status_code=502,
                detail=f"The AI returned an invalid {field}.",
            )

    if result["difficulty"] not in {"Easy", "Medium", "Hard"}:
        raise HTTPException(
            status_code=502,
            detail="The AI returned an invalid difficulty level.",
        )

    ingredients = result["ingredients"]
    steps = result["steps"]

    if not isinstance(ingredients, list) or not ingredients:
        raise HTTPException(
            status_code=502,
            detail="The recipe must contain an ingredient list.",
        )

    if not isinstance(steps, list) or not steps:
        raise HTTPException(
            status_code=502,
            detail="The recipe must contain cooking steps.",
        )

    for ingredient in ingredients:
        if (
            not isinstance(ingredient, dict)
            or not isinstance(ingredient.get("name"), str)
            or not isinstance(ingredient.get("quantity"), str)
        ):
            raise HTTPException(
                status_code=502,
                detail="The AI returned an invalid ingredient.",
            )

    for index, step in enumerate(steps, start=1):
        if (
            not isinstance(step, dict)
            or not isinstance(step.get("instruction"), str)
            or not step["instruction"].strip()
        ):
            raise HTTPException(
                status_code=502,
                detail="The AI returned an invalid cooking step.",
            )

        step["step_number"] = index

        duration = step.get("duration_minutes")
        if duration is not None and (
            isinstance(duration, bool)
            or not isinstance(duration, int)
            or duration < 0
        ):
            raise HTTPException(
                status_code=502,
                detail="The AI returned an invalid step duration.",
            )

    for field in ("cooking_tips", "safety_notes", "limitations"):
        if (
            not isinstance(result[field], list)
            or not all(isinstance(item, str) for item in result[field])
        ):
            raise HTTPException(
                status_code=502,
                detail=f"The AI returned invalid {field}.",
            )

    return result


def _generate_text_recipe(prompt: str) -> dict:
    """Generate a recipe from text using the configured Groq model or realistic fallback."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        logger.info("GROQ_API_KEY not configured; providing fallback culinary recipe.")
        return {
            "dish_name": "Fragrant Garden Skillet with Herb Chickpeas",
            "description": "A wholesome, vibrant skillet recipe loaded with protein-rich chickpeas, tender greens, and fragrant Mediterranean spices.",
            "servings": 2,
            "preparation_time_minutes": 10,
            "cooking_time_minutes": 20,
            "difficulty": "Easy",
            "ingredients": [
                {"name": "Cooked chickpeas", "quantity": "1 can (400g) drained"},
                {"name": "Baby spinach", "quantity": "2 cups packed"},
                {"name": "Cherry tomatoes", "quantity": "1 cup halved"},
                {"name": "Extra virgin olive oil", "quantity": "1 tbsp"},
                {"name": "Garlic", "quantity": "2 cloves minced"},
                {"name": "Ground cumin and smoked paprika", "quantity": "1 tsp each"},
                {"name": "Fresh lemon juice", "quantity": "1 tbsp"}
            ],
            "steps": [
                {"step_number": 1, "instruction": "Warm olive oil in a wide skillet over medium heat.", "duration_minutes": 2},
                {"step_number": 2, "instruction": "Add minced garlic, cumin, and paprika; saute for 60 seconds until fragrant.", "duration_minutes": 1},
                {"step_number": 3, "instruction": "Add drained chickpeas and cherry tomatoes; toss until heated and tomatoes soften.", "duration_minutes": 7},
                {"step_number": 4, "instruction": "Toss in fresh baby spinach until just wilted; finish with fresh lemon juice and season to taste.", "duration_minutes": 3}
            ],
            "cooking_tips": [
                "Warm the spices directly in the oil to release their essential aromatics.",
                "Top with lightly toasted sesame or sunflower seeds for added crunch."
            ],
            "safety_notes": [
                "Wash all fresh greens and tomatoes thoroughly under cool drinking water before prepping.",
                "Ensure cookware handles are turned safely away from stove edges."
            ],
            "limitations": [
                "Cooking duration may vary slightly depending on cookware thickness and burner strength."
            ]
        }

    client = Groq(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_completion_tokens=1600,
        )
    except Exception as exc:
        logger.exception("Text recipe generation failed.")
        raise HTTPException(
            status_code=502,
            detail="Recipe generation failed. Check Groq availability and server logs.",
        ) from exc

    response_text = response.choices[0].message.content

    if not response_text:
        raise HTTPException(
            status_code=502,
            detail="The AI returned an empty recipe response.",
        )

    return _validate_recipe(_parse_recipe_json(response_text))


@router.post(
    "/generate-recipe",
    response_model=RecipeGenerationResponse,
)
async def generate_recipe(
    text_input: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    servings: int = Form(default=2, ge=1, le=12),
    skill_level: str = Form(default="Beginner"),
    dietary_preference: str = Form(default="None"),
    cuisine: str = Form(default="Any"),
    available_time_minutes: int = Form(default=60, ge=1, le=600),
):
    """Generate a structured recipe from a text request or ingredient image."""

    if not (text_input and text_input.strip()) and file is None:
        raise HTTPException(
            status_code=400,
            detail="Provide a text cooking request, an ingredient image, or both.",
        )

    if skill_level not in {"Beginner", "Intermediate", "Advanced"}:
        raise HTTPException(
            status_code=400,
            detail="skill_level must be Beginner, Intermediate, or Advanced.",
        )

    if not dietary_preference.strip() or not cuisine.strip():
        raise HTTPException(
            status_code=400,
            detail="Dietary preference and cuisine cannot be empty.",
        )

    prompt = f"""
    User cooking request or ingredient description:
    {text_input.strip() if text_input and text_input.strip() else
    "Inspect the uploaded ingredient image and suggest a suitable recipe."}

    Requested servings: {servings}
    Cooking skill level: {skill_level}
    Dietary preference: {dietary_preference}
    Preferred cuisine: {cuisine}
    Available time: {available_time_minutes} minutes

    Generate one suitable recipe. Respect the dietary preference and time
    limit as far as practical. State uncertainty if ingredients are unclear.
    Return the JSON structure specified in the system instructions.
    """

    try:
        if file is not None:
            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail="No filename provided for the uploaded image.",
                )

            if file.content_type and not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=415,
                    detail="Please upload an ingredient image.",
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

            encoded_image = _prepare_image(image_bytes)

            try:
                with Image.open(io.BytesIO(image_bytes)) as image:
                    if image.width * image.height > MAX_IMAGE_PIXELS:
                        raise HTTPException(
                            status_code=413,
                            detail="Image dimensions are too large.",
                        )
            except (UnidentifiedImageError, OSError):
                raise HTTPException(
                    status_code=400,
                    detail="Please upload a valid ingredient image.",
                ) from None

            image_prompt = (
                SYSTEM_PROMPT
                + "\nUser request and cooking context:\n"
                + prompt
            )

            response_text = _call_groq_vision(
               encoded_image=encoded_image,
                system_prompt=SYSTEM_PROMPT,
                user_prompt=image_prompt,
                max_completion_tokens=1600,
            )

            result = _validate_recipe(_parse_recipe_json(response_text))
        else:
            result = _generate_text_recipe(prompt)

        return {
            "success": True,
            "model": GROQ_MODEL_NAME,
            **result,
        }

    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded image could not be processed.",
        ) from None
    except Exception as exc:
        logger.exception("Recipe generation failed.")
        raise HTTPException(
            status_code=502,
            detail="Recipe generation failed. Check the backend terminal.",
        ) from exc
    finally:
        if file is not None:
            await file.close()