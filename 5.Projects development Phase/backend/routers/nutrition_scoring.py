
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/nutrition",
    tags=["Nutrition Scoring"],
)


class NutritionScoreRequest(BaseModel):
    calories_kcal: float = Field(ge=0)
    protein_g: float = Field(ge=0)
    fiber_g: float = Field(ge=0)
    portion_weight_g: float = Field(gt=0)


def calculate_health_score(
    calories_kcal: float,
    protein_g: float,
    fiber_g: float,
    portion_weight_g: float,
) -> dict:
    """Calculate a simplified FoodVerse AI meal score from 0 to 100."""

    values = [calories_kcal, protein_g, fiber_g, portion_weight_g]

    if any(value < 0 for value in values):
        raise ValueError("Nutrition values cannot be negative.")

    if portion_weight_g <= 0:
        raise ValueError("Portion weight must be greater than zero.")

    protein_score = min(protein_g / 25, 1.0) * 40
    fiber_score = min(fiber_g / 8, 1.0) * 30

    calories_per_100g = calories_kcal / portion_weight_g * 100

    if calories_per_100g <= 100:
        energy_score = 30
    elif calories_per_100g >= 300:
        energy_score = 0
    else:
        energy_score = (300 - calories_per_100g) / 200 * 30

    score = round(protein_score + fiber_score + energy_score)
    score = max(0, min(100, score))

    if score >= 75:
        label = "Healthy"
    elif score >= 50:
        label = "Moderate"
    else:
        label = "Unhealthy"

    return {
        "health_score": score,
        "health_label": label,
        "components": {
            "protein_score": round(protein_score, 2),
            "fiber_score": round(fiber_score, 2),
            "energy_density_score": round(energy_score, 2),
            "calories_per_100g": round(calories_per_100g, 2),
        },
        "reasoning": (
            "The score uses protein (40 points), fiber (30 points), "
            "and energy density (30 points). This is a simplified "
            "project heuristic, not a clinical nutrition rating."
        ),
    }


@router.post("/score")
def score_nutrition(request: NutritionScoreRequest):
    try:
        return calculate_health_score(
            calories_kcal=request.calories_kcal,
            protein_g=request.protein_g,
            fiber_g=request.fiber_g,
            portion_weight_g=request.portion_weight_g,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc