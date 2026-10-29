
"""Local meal recommendation logic for FoodVerse AI.

Nutrition values are illustrative estimates for a student-project prototype.
They are not a substitute for verified nutrition data or medical advice.
"""

from typing import Any


MEALS: list[dict[str, Any]] = [
    {
        "id": "oats_milk",
        "name": "Oats with milk and banana",
        "meal_type": "breakfast",
        "diet": "vegetarian",
        "cuisine": "Any",
        "ingredients": ["oats", "milk", "banana"],
        "allergens": ["milk"],
        "calories": 350,
        "protein": 13,
        "carbs": 58,
        "fat": 8,
    },
    {
        "id": "vegan_oats",
        "name": "Oats with soy milk and banana",
        "meal_type": "breakfast",
        "diet": "vegan",
        "cuisine": "Any",
        "ingredients": ["oats", "soy milk", "banana"],
        "allergens": ["soy"],
        "calories": 330,
        "protein": 12,
        "carbs": 55,
        "fat": 7,
    },
    {
        "id": "poha",
        "name": "Vegetable poha",
        "meal_type": "breakfast",
        "diet": "vegan",
        "cuisine": "Indian",
        "ingredients": ["flattened rice", "onion", "peas", "peanuts"],
        "allergens": ["peanuts"],
        "calories": 300,
        "protein": 7,
        "carbs": 48,
        "fat": 9,
    },
    {
        "id": "idli_sambar",
        "name": "Idli with sambar",
        "meal_type": "breakfast",
        "diet": "vegan",
        "cuisine": "Indian",
        "ingredients": ["rice", "lentils", "vegetables"],
        "allergens": [],
        "calories": 320,
        "protein": 12,
        "carbs": 60,
        "fat": 4,
    },
    {
        "id": "dal_rice",
        "name": "Dal with rice and vegetables",
        "meal_type": "lunch",
        "diet": "vegan",
        "cuisine": "Indian",
        "ingredients": ["lentils", "rice", "vegetables"],
        "allergens": [],
        "calories": 480,
        "protein": 18,
        "carbs": 78,
        "fat": 9,
    },
    {
        "id": "paneer_roti",
        "name": "Paneer with roti",
        "meal_type": "lunch",
        "diet": "vegetarian",
        "cuisine": "Indian",
        "ingredients": ["paneer", "milk", "wheat", "tomato"],
        "allergens": ["milk", "wheat"],
        "calories": 520,
        "protein": 25,
        "carbs": 55,
        "fat": 20,
    },
    {
        "id": "chickpea_bowl",
        "name": "Chickpea and vegetable bowl",
        "meal_type": "lunch",
        "diet": "vegan",
        "cuisine": "Any",
        "ingredients": ["chickpeas", "vegetables", "olive oil"],
        "allergens": [],
        "calories": 430,
        "protein": 17,
        "carbs": 60,
        "fat": 13,
    },
    {
        "id": "chicken_rice",
        "name": "Chicken with rice and vegetables",
        "meal_type": "dinner",
        "diet": "non_vegetarian",
        "cuisine": "Any",
        "ingredients": ["chicken", "rice", "vegetables"],
        "allergens": [],
        "calories": 550,
        "protein": 38,
        "carbs": 62,
        "fat": 13,
    },
    {
        "id": "tofu_rice",
        "name": "Tofu with rice and vegetables",
        "meal_type": "dinner",
        "diet": "vegan",
        "cuisine": "Any",
        "ingredients": ["tofu", "soy", "rice", "vegetables"],
        "allergens": ["soy"],
        "calories": 460,
        "protein": 24,
        "carbs": 55,
        "fat": 15,
    },
    {
        "id": "egg_roti",
        "name": "Egg curry with roti",
        "meal_type": "dinner",
        "diet": "eggetarian",
        "cuisine": "Indian",
        "ingredients": ["eggs", "wheat", "tomato"],
        "allergens": ["eggs", "wheat"],
        "calories": 490,
        "protein": 24,
        "carbs": 48,
        "fat": 19,
    },
    {
        "id": "fruit_yogurt",
        "name": "Fruit with yogurt",
        "meal_type": "snack",
        "diet": "vegetarian",
        "cuisine": "Any",
        "ingredients": ["fruit", "yogurt", "milk"],
        "allergens": ["milk"],
        "calories": 180,
        "protein": 8,
        "carbs": 28,
        "fat": 4,
    },
    {
        "id": "roasted_chana",
        "name": "Roasted chana",
        "meal_type": "snack",
        "diet": "vegan",
        "cuisine": "Indian",
        "ingredients": ["chickpeas"],
        "allergens": [],
        "calories": 160,
        "protein": 8,
        "carbs": 25,
        "fat": 3,
    },
]


ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


def calculate_targets(profile: dict[str, Any]) -> dict[str, Any]:
    """Estimate daily calories and macro targets using a simple weight-based method.

    This deliberately avoids pretending to calculate medically precise energy needs.
    """

    weight = float(profile["weight_kg"])
    activity = profile["activity_level"]
    goal = profile["goal"]

    # Approximate resting-energy proxy, adjusted for activity.
    maintenance = weight * 24 * ACTIVITY_MULTIPLIERS[activity]

    goal_adjustments = {
        "lose_weight": -300,
        "maintain_weight": 0,
        "gain_weight": 300,
    }

    calories = max(1200, round(maintenance + goal_adjustments[goal]))

    # Illustrative macro split: 20% protein, 50% carbohydrate, 30% fat.
    protein_g = round(calories * 0.20 / 4)
    carbs_g = round(calories * 0.50 / 4)
    fat_g = round(calories * 0.30 / 9)

    return {
        "estimated_daily_calories_kcal": calories,
        "estimated_macros_g": {
            "protein": protein_g,
            "carbohydrates": carbs_g,
            "fat": fat_g,
        },
        "method": "Weight-based educational estimate; not medical advice.",
    }


def _normalise(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _diet_is_allowed(meal_diet: str, preference: str) -> bool:
    preference = _normalise(preference)
    meal_diet = _normalise(meal_diet)

    if preference == "vegan":
        return meal_diet == "vegan"

    if preference == "vegetarian":
        return meal_diet in {"vegan", "vegetarian"}

    if preference == "eggetarian":
        return meal_diet in {"vegan", "vegetarian", "eggetarian"}

    if preference == "non_vegetarian":
        return meal_diet in {"vegan", "vegetarian", "eggetarian", "non_vegetarian"}

    return False


def filter_meals(
    profile: dict[str, Any],
    meal_type: str | None = None,
) -> list[dict[str, Any]]:
    """Filter the local catalog against diet, allergies, restrictions and dislikes."""

    allergies = {_normalise(x) for x in profile.get("allergies", [])}
    restrictions = {_normalise(x) for x in profile.get("dietary_restrictions", [])}
    disliked = {_normalise(x) for x in profile.get("disliked_foods", [])}
    preference = profile["dietary_preference"]
    cuisine = _normalise(profile.get("preferred_cuisine", "Any"))

    result = []

    for meal in MEALS:
        if meal_type and meal["meal_type"] != meal_type:
            continue

        if not _diet_is_allowed(meal["diet"], preference):
            continue

        if cuisine not in {"any", ""} and _normalise(meal["cuisine"]) not in {
            "any",
            cuisine,
        }:
            continue

        ingredients = {_normalise(x) for x in meal["ingredients"]}
        meal_allergens = {_normalise(x) for x in meal["allergens"]}

        # Conservative exact token matching for this small demo catalog.
        # Real products may contain hidden/cross-contact allergens.
        if allergies & (ingredients | meal_allergens):
            continue

        if restrictions & (ingredients | meal_allergens):
            continue

        if disliked & ingredients:
            continue

        result.append(meal.copy())

    return result


def get_alternatives(
    profile: dict[str, Any],
    meal_id: str,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Return compatible alternatives from the local catalog."""

    original = next((meal for meal in MEALS if meal["id"] == meal_id), None)

    if original is None:
        raise ValueError("Unknown meal_id.")

    candidates = filter_meals(profile, original["meal_type"])
    candidates = [meal for meal in candidates if meal["id"] != meal_id]

    # Prefer alternatives with a similar calorie value.
    candidates.sort(
        key=lambda meal: abs(meal["calories"] - original["calories"])
    )

    return candidates[:limit]


    
def scale_meal_portion(
    meal: dict[str, Any],
    serving_multiplier: float,
) -> dict[str, Any]:
    """Scale illustrative nutrition values for a chosen serving size."""

    if serving_multiplier <= 0:
        raise ValueError("Serving multiplier must be greater than zero.")

    scaled = meal.copy()
    scaled["serving_multiplier"] = round(serving_multiplier, 2)

    for key in ("calories", "protein", "carbs", "fat"):
        scaled[key] = round(meal[key] * serving_multiplier)

    return scaled