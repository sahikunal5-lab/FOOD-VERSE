import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_api_endpoints():
    print("=== Testing FastAPI Endpoints ===")

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, f"/health failed: {res.text}"
    health_data = res.json()
    print(f"1. /health: OK (Engine: {health_data['database']['engine']}, Alive: {health_data['database']['is_alive']})")

    # 2. Food items catalog
    res = client.get("/food-items?limit=5")
    assert res.status_code == 200, f"/food-items failed: {res.text}"
    items = res.json()
    assert len(items) > 0, "No food items returned"
    print(f"2. /food-items: OK ({len(items)} items retrieved, first: '{items[0]['name']}')")

    # 3. Food categories
    res = client.get("/food-items/categories")
    assert res.status_code == 200, f"/food-items/categories failed: {res.text}"
    categories = res.json()["categories"]
    print(f"3. /food-items/categories: OK ({len(categories)} categories found: {categories[:4]}...)")

    # 4. Search food items
    res = client.get("/food-items?q=oats")
    assert res.status_code == 200
    search_results = res.json()
    print(f"4. /food-items search 'oats': OK ({len(search_results)} matching dishes)")

    # 5. Recommendations generate
    rec_payload = {
        "age": 24,
        "height_cm": 172.0,
        "weight_kg": 68.0,
        "activity_level": "moderate",
        "goal": "maintain_weight",
        "dietary_preference": "vegetarian",
        "preferred_cuisine": "Indian",
        "save_to_db": True,
    }
    res = client.post("/recommendations/generate", json=rec_payload)
    assert res.status_code == 200, f"/recommendations/generate failed: {res.text}"
    rec_data = res.json()
    assert "target_calories_kcal" in rec_data
    assert len(rec_data["recommended_meals"]) > 0
    print(f"5. /recommendations/generate: OK (Target: {rec_data['target_calories_kcal']} kcal, Meals: {len(rec_data['recommended_meals'])})")

    # 6. Recommendation history
    res = client.get("/recommendations/history")
    assert res.status_code == 200
    rec_history = res.json()
    print(f"6. /recommendations/history: OK ({len(rec_history)} records in DB)")

    # 7. Food log recording
    log_payload = {
        "dish_name": "Vegetable Poha",
        "meal_type": "breakfast",
        "portion_weight_g": 200.0,
        "calories_kcal": 300.0,
        "protein_g": 7.0,
        "carbs_g": 48.0,
        "fat_g": 9.0,
        "fiber_g": 4.0,
        "health_score": 75,
        "health_label": "Healthy",
    }
    res = client.post("/food-logs", json=log_payload)
    assert res.status_code == 201, f"/food-logs POST failed: {res.text}"
    created_log = res.json()
    print(f"7. /food-logs POST: OK (Log ID: {created_log['id']})")

    # 8. Food log summary today
    res = client.get("/food-logs/summary/today")
    assert res.status_code == 200
    summary = res.json()
    print(f"8. /food-logs/summary/today: OK (Calories: {summary['total_calories_kcal']} kcal, Protein: {summary['total_protein_g']}g)")

    # 9. Meal plans save
    plan_payload = {
        "plan_name": "API Test Plan",
        "goal": "maintain_weight",
        "target_calories_kcal": 2100.0,
        "planned_calories_kcal": 2050.0,
        "meals_data": [{"name": "Dal Rice", "type": "lunch", "calories": 480}],
        "nutrition_summary": {"calories": 2050, "protein": 85},
        "notes": ["Test notes"],
    }
    res = client.post("/meal-plans", json=plan_payload)
    assert res.status_code == 201, f"/meal-plans POST failed: {res.text}"
    created_plan = res.json()
    print(f"9. /meal-plans POST: OK (Plan ID: {created_plan['id']})")

    # 10. Database statistics
    res = client.get("/database/stats")
    assert res.status_code == 200
    stats = res.json()
    print(f"10. /database/stats: OK (Status: {stats['status']}, Counts: {stats['counts']})")

    # 11. Meal planner profile & daily plan (existing endpoints)
    profile_payload = {
        "age": 22,
        "height_cm": 168.0,
        "weight_kg": 62.0,
        "activity_level": "moderate",
        "goal": "lose_weight",
        "dietary_preference": "vegetarian",
        "preferred_cuisine": "Indian",
        "allergies": [],
        "dietary_restrictions": [],
        "disliked_foods": [],
        "meals_per_day": 3,
    }
    res = client.post("/meal-planner/profile", json=profile_payload)
    assert res.status_code == 200, f"/meal-planner/profile failed: {res.text}"
    profile_id = res.json()["profile_id"]

    res = client.post(f"/meal-planner/daily/{profile_id}")
    assert res.status_code == 200, f"/meal-planner/daily failed: {res.text}"
    daily_plan = res.json()
    print(f"11. /meal-planner/daily/{profile_id}: OK ({len(daily_plan['meals'])} meals planned, Target: {daily_plan['targets']['estimated_daily_calories_kcal']} kcal)")

    print("\n[SUCCESS] ALL FASTAPI ENDPOINT INTEGRATION TESTS PASSED!")


if __name__ == "__main__":
    test_api_endpoints()

