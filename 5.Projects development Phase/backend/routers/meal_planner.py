from typing import Literal, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator

from services.meal_recommendation import (
    calculate_targets,
    filter_meals,
    scale_meal_portion,
)

router = APIRouter(
    prefix="/meal-planner",
    tags=["Personalized Meal Planner"],
)


class UserProfile(BaseModel):
    """Validated user information for personalized meal planning."""
    age: int = Field(ge=18, le=100)
    height_cm: float = Field(ge=100, le=250)
    weight_kg: float = Field(ge=25, le=300)

    activity_level: Literal[
        "sedentary", "light", "moderate", "active", "very_active"
    ]
    goal: Literal["lose_weight", "maintain_weight", "gain_weight"]
    dietary_preference: Literal[
        "vegetarian", "vegan", "non_vegetarian", "eggetarian"
    ]

    allergies: List[str] = Field(default_factory=list, max_length=50)
    dietary_restrictions: List[str] = Field(default_factory=list, max_length=50)
    disliked_foods: List[str] = Field(default_factory=list, max_length=50)

    preferred_cuisine: str = Field(default="Any", min_length=1, max_length=60)
    meals_per_day: int = Field(default=3, ge=1, le=8)

    @field_validator("allergies", "dietary_restrictions", "disliked_foods")
    @classmethod
    def clean_food_lists(cls, values: List[str]) -> List[str]:
        cleaned = []
        for value in values:
            item = value.strip()
            if not item:
                raise ValueError("Food preference entries cannot be empty.")
            if len(item) > 100:
                raise ValueError(
                    "Food preference entries must be 100 characters or fewer."
                )
            cleaned.append(item)
        return list(dict.fromkeys(cleaned))

    @field_validator("preferred_cuisine")
    @classmethod
    def clean_cuisine(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Preferred cuisine cannot be empty.")
        return value

    @model_validator(mode="after")
    def validate_profile_consistency(self):
        return self


class UserProfileResponse(BaseModel):
    success: bool
    message: str
    profile_id: int
    profile: UserProfile


# In-memory profile store (database persistence removed)
_profiles_db: Dict[int, dict] = {}
_profile_id_counter = 1


@router.post("/profile", response_model=UserProfileResponse)
def process_user_profile(profile: UserProfile):
    """Validate a profile and store it in memory without external database."""
    global _profile_id_counter
    profile_id = _profile_id_counter
    _profile_id_counter += 1

    profile_dict = profile.model_dump()
    _profiles_db[profile_id] = profile_dict

    return UserProfileResponse(
        success=True,
        message="User profile validated and saved successfully.",
        profile_id=profile_id,
        profile=profile,
    )


@router.get("/profile/{profile_id}", response_model=UserProfileResponse)
def get_user_profile(profile_id: int):
    """Retrieve a profile from memory by its ID."""
    if profile_id not in _profiles_db:
        raise HTTPException(
            status_code=404,
            detail="User profile not found.",
        )

    profile = UserProfile.model_validate(_profiles_db[profile_id])
    return UserProfileResponse(
        success=True,
        message="User profile retrieved successfully.",
        profile_id=profile_id,
        profile=profile,
    )


def choose_meal(profile: dict, meal_type: str, used_ids: set):
    """Choose a compatible meal, preferring meals not already selected."""
    candidates = filter_meals(profile, meal_type)
    unused = [meal for meal in candidates if meal["id"] not in used_ids]
    options = unused or candidates
    if not options:
        return None
    return options[0]


@router.post("/daily/{profile_id}")
def generate_daily_plan(profile_id: int):
    """Generate a daily plan with approximate portion scaling."""
    if profile_id not in _profiles_db:
        raise HTTPException(
            status_code=404,
            detail="User profile not found.",
        )

    profile = _profiles_db[profile_id]
    targets = calculate_targets(profile)
    calorie_target = targets["estimated_daily_calories_kcal"]

    meal_types = ["breakfast", "lunch", "dinner"]
    if profile.get("meals_per_day", 3) >= 4:
        meal_types.append("snack")

    used_ids = set()
    base_meals = []

    for meal_type in meal_types:
        meal = choose_meal(profile, meal_type, used_ids)
        if meal is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"No compatible {meal_type} found. "
                    "Review the dietary preferences and meal catalog."
                ),
            )
        used_ids.add(meal["id"])
        base_meals.append(meal)

    base_calories = sum(meal["calories"] for meal in base_meals)
    if base_calories <= 0:
        raise HTTPException(
            status_code=500,
            detail="Meal catalog contains invalid calorie values.",
        )

    multiplier = max(
        0.5,
        min(2.5, calorie_target / base_calories),
    )

    selected_meals = [
        scale_meal_portion(meal, multiplier)
        for meal in base_meals
    ]

    total = {
        "calories_kcal": sum(meal["calories"] for meal in selected_meals),
        "protein_g": sum(meal["protein"] for meal in selected_meals),
        "carbs_g": sum(meal["carbs"] for meal in selected_meals),
        "fat_g": sum(meal["fat"] for meal in selected_meals),
    }

    calorie_difference = total["calories_kcal"] - calorie_target

    return {
        "success": True,
        "profile_id": profile_id,
        "goal": profile.get("goal"),
        "targets": targets,
        "meals": selected_meals,
        "nutrition_summary": total,
        "calorie_comparison": {
            "target_kcal": calorie_target,
            "planned_kcal": total["calories_kcal"],
            "difference_kcal": calorie_difference,
            "within_10_percent": (
                abs(calorie_difference) <= calorie_target * 0.10
            ),
        },
        "notes": [
            "Nutrition values are illustrative estimates from FoodVerse catalog.",
            "Portion scaling approximates daily target caloric requirements.",
            "Daily calorie targets are educational estimates, not clinical prescription.",
            "Allergen filtering verifies visible declared ingredients.",
        ],
    }
