from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/database", tags=["Database"])


class MealAnalysisCreate(BaseModel):
    dish_name: str = Field(min_length=1, max_length=255)
    image_path: Optional[str] = Field(default=None, max_length=500)
    portion_weight_g: Optional[float] = Field(default=None, gt=0)
    calories_kcal: Optional[float] = Field(default=None, ge=0)
    protein_g: Optional[float] = Field(default=None, ge=0)
    carbs_g: Optional[float] = Field(default=None, ge=0)
    fat_g: Optional[float] = Field(default=None, ge=0)
    fiber_g: Optional[float] = Field(default=None, ge=0)
    health_score: Optional[int] = Field(default=None, ge=0, le=100)
    health_label: Optional[str] = Field(default=None, max_length=50)


class MealAnalysisResponse(BaseModel):
    id: int
    dish_name: str
    image_path: Optional[str] = None
    portion_weight_g: Optional[float] = None
    calories_kcal: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    health_score: Optional[int] = None
    health_label: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# In-memory store (database persistence removed as requested)
_analyses_store: List[MealAnalysisResponse] = [
    MealAnalysisResponse(
        id=1,
        dish_name="Warm Quinoa Buddha Bowl",
        image_path=None,
        portion_weight_g=300.0,
        calories_kcal=390.0,
        protein_g=15.0,
        carbs_g=58.0,
        fat_g=12.0,
        fiber_g=10.0,
        health_score=91,
        health_label="Healthy",
        created_at=datetime.now(),
    ),
    MealAnalysisResponse(
        id=2,
        dish_name="Avocado & Seed Sourdough Toast",
        image_path=None,
        portion_weight_g=180.0,
        calories_kcal=280.0,
        protein_g=7.0,
        carbs_g=26.0,
        fat_g=17.0,
        fiber_g=8.0,
        health_score=88,
        health_label="Healthy",
        created_at=datetime.now(),
    ),
]
_analysis_id_counter = 3


def add_analysis_in_memory(item_data: dict) -> MealAnalysisResponse:
    """Helper to append an analysis into the in-memory store."""
    global _analysis_id_counter
    new_record = MealAnalysisResponse(
        id=_analysis_id_counter,
        dish_name=item_data.get("dish_name", "Analyzed Meal"),
        image_path=item_data.get("image_path"),
        portion_weight_g=item_data.get("portion_weight_g", 250.0),
        calories_kcal=item_data.get("calories_kcal", 0.0),
        protein_g=item_data.get("protein_g", 0.0),
        carbs_g=item_data.get("carbs_g", 0.0),
        fat_g=item_data.get("fat_g", 0.0),
        fiber_g=item_data.get("fiber_g", 0.0),
        health_score=item_data.get("health_score", 75),
        health_label=item_data.get("health_label", "Healthy"),
        created_at=datetime.now(),
    )
    _analysis_id_counter += 1
    _analyses_store.insert(0, new_record)
    return new_record


@router.post("/analyses", response_model=MealAnalysisResponse)
def save_analysis(data: MealAnalysisCreate):
    """Save a meal analysis to memory (no external database persistence)."""
    return add_analysis_in_memory(data.model_dump())


@router.get("/analyses", response_model=List[MealAnalysisResponse])
def get_analyses(limit: int = 20):
    """Retrieve saved meal analyses from memory."""
    if not 1 <= limit <= 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100.",
        )
    return _analyses_store[:limit]
