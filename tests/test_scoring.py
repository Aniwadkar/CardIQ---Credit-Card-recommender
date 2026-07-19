from src.models.user_input import MonthlySpending, UserProfile
from src.scoring import CardScorer
from src.utils.calculations import calculate_category_rewards


def _profile():
    return UserProfile(
        monthly_spending=MonthlySpending(
            dining=100,
            groceries=0,
            travel=100,
            gas=0,
            streaming=0,
            other=0,
            flights=80,
            hotels=40,
            transit=20,
        ),
        credit_score="good",
    )


def test_travel_subcategories_do_not_create_negative_remaining_travel():
    rewards = calculate_category_rewards(
        monthly_spending=_profile().monthly_spending.model_dump(),
        card_rewards={"travel": 3, "flights": 5, "hotels": 5, "transit": 2},
        point_value=0.01,
    )

    assert rewards == 76.8


def test_card_scorer_uses_blended_multi_year_score():
    card = {
        "card_id": "test",
        "card_name": "Test Card",
        "annual_fee": 100,
        "signup_bonus": {"estimated_value": 300},
        "rewards": {"dining": 2, "travel": 1, "flights": 1, "hotels": 1, "transit": 1},
        "point_value": 0.01,
        "annual_credits": [{"name": "Test Credit", "value": 50, "category": "general"}],
    }

    evaluation = CardScorer().evaluate_card(card, _profile())

    assert evaluation.net_value_year_1 == 290.8
    assert evaluation.net_value_year_2 == 281.6
    assert evaluation.net_value_year_3 == 272.4
    assert evaluation.ranking_score == 281.6
