import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from database import SessionLocal, get_db_info, init_db
from models import FoodItem, FoodLog, FoodRecommendation, MealAnalysis, MealPlan, User, UserProfileRecord


def test_database():
    print("--- 1. Testing Database Initialization & Engine Status ---")
    info = get_db_info()
    print(f"Active Engine: {info['engine']}")
    print(f"Database Alive: {info['is_alive']}")
    print(f"Target DB: {info['db_name']}")

    init_db()

    db = SessionLocal()
    try:
        print("\n--- 2. Testing FoodItem Catalog Query ---")
        item_count = db.query(FoodItem).count()
        print(f"Verified Food Items in DB: {item_count}")
        assert item_count >= 10, f"Expected at least 10 food items, found {item_count}"

        sample_item = db.query(FoodItem).first()
        print(f"Sample Food: {sample_item.name} ({sample_item.category}, {sample_item.calories_kcal} kcal)")

        print("\n--- 3. Testing MealAnalysis CRUD (Preserved Model) ---")
        meal = MealAnalysis(
            dish_name="Roasted Paneer & Vegetable Medley",
            portion_weight_g=280.0,
            calories_kcal=410.0,
            protein_g=22.0,
            carbs_g=28.0,
            fat_g=24.0,
            fiber_g=7.0,
            health_score=86,
            health_label="Healthy",
        )
        db.add(meal)
        db.commit()
        db.refresh(meal)
        saved_id = meal.id
        print(f"Created MealAnalysis ID: {saved_id}")

        retrieved_meal = db.get(MealAnalysis, saved_id)
        assert retrieved_meal is not None
        assert retrieved_meal.dish_name == "Roasted Paneer & Vegetable Medley"
        print(f"Retrieved MealAnalysis: {retrieved_meal.dish_name} (Score: {retrieved_meal.health_score})")

        print("\n--- 4. Testing UserProfileRecord Persistence ---")
        profile = UserProfileRecord(
            age=25,
            height_cm=175.0,
            weight_kg=70.0,
            activity_level="moderate",
            goal="maintain_weight",
            dietary_preference="vegetarian",
            allergies=["peanuts"],
            dietary_restrictions=[],
            disliked_foods=["mushroom"],
            preferred_cuisine="Indian",
            meals_per_day=3,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        profile_id = profile.id
        print(f"Created UserProfile ID: {profile_id}")

        print("\n--- 5. Testing FoodLog Entry & Daily Summary ---")
        log_entry = FoodLog(
            dish_name="Warm Quinoa Buddha Bowl",
            meal_type="lunch",
            portion_weight_g=300.0,
            calories_kcal=390.0,
            protein_g=15.0,
            carbs_g=58.0,
            fat_g=12.0,
            fiber_g=10.0,
            health_score=91,
            health_label="Healthy",
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        print(f"Logged Meal: {log_entry.dish_name} on {log_entry.logged_at}")

        print("\n--- 6. Testing MealPlan Persistence ---")
        plan = MealPlan(
            profile_id=profile_id,
            plan_name="Sample Balanced Daily Plan",
            target_calories_kcal=2100.0,
            planned_calories_kcal=2080.0,
            meals_data=[
                {"name": "Oats with milk and banana", "type": "breakfast", "calories": 420},
                {"name": "Dal with rice and vegetables", "type": "lunch", "calories": 650},
                {"name": "Paneer with roti", "type": "dinner", "calories": 710},
                {"name": "Roasted chana", "type": "snack", "calories": 300},
            ],
            nutrition_summary={
                "calories_kcal": 2080,
                "protein_g": 98,
                "carbs_g": 265,
                "fat_g": 62,
            },
            notes=["Within target range", "Verified nutrition heuristic"],
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        print(f"Saved Meal Plan ID: {plan.id} ('{plan.plan_name}')")

        print("\n--- 7. Testing FoodRecommendation Persistence ---")
        rec = FoodRecommendation(
            profile_id=profile_id,
            recommendation_type="daily_targets",
            goal="maintain_weight",
            target_calories_kcal=2100.0,
            recommended_items=["Dal rice", "Paneer roti", "Greek salad"],
            target_macros={"protein": 105, "carbohydrates": 260, "fat": 70},
            reasoning="Balanced protein and complex carbohydrates suited for moderate activity.",
            health_score=88,
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        print(f"Saved Recommendation ID: {rec.id}")

        print("\n[SUCCESS] ALL DATABASE INTEGRATION TESTS PASSED!")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    test_database()
