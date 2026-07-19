from src.evaluation import evaluate_scenarios


def test_evaluation_scenarios_produce_distinct_primary_recommendations():
    payload = evaluate_scenarios()

    assert payload["scenario_count"] == 3
    assert [scenario["scenario_id"] for scenario in payload["scenarios"]] == [
        "food_focused",
        "frequent_traveler",
        "no_annual_fee",
    ]

    primary_cards = {
        scenario["recommendations"][0]["card_name"] for scenario in payload["scenarios"]
    }
    assert len(primary_cards) == 3

    no_fee = payload["scenarios"][2]
    assert all(
        recommendation["financial_summary"]["annual_fee"] == 0
        for recommendation in no_fee["recommendations"]
    )
