
from nutrition_scoring import calculate_health_score


def test_normal_meal():
    result = calculate_health_score(
        calories_kcal=480,
        protein_g=42,
        fiber_g=6,
        portion_weight_g=250,
    )

    assert result["health_score"] == 79
    assert result["health_label"] == "Healthy"


def test_zero_nutrients():
    result = calculate_health_score(
        calories_kcal=0,
        protein_g=0,
        fiber_g=0,
        portion_weight_g=250,
    )

    assert result["health_score"] == 30


def test_invalid_portion():
    try:
        calculate_health_score(
            calories_kcal=100,
            protein_g=5,
            fiber_g=2,
            portion_weight_g=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Zero portion weight should be rejected.")


if __name__ == "__main__":
    test_normal_meal()
    test_zero_nutrients()
    test_invalid_portion()
    print("All nutrition scoring tests passed!")