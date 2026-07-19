from src.models.user_input import MonthlySpending, UserProfile
from src.services import RecommendationService


class _FakeRepository:
    def __init__(self, cards):
        self.cards = cards

    def find_candidates(self, max_annual_fee=None, preferred_rewards_type=None, include_business=False):
        cards = self.cards
        if max_annual_fee is not None:
            cards = [card for card in cards if card["annual_fee"] <= max_annual_fee]
        if preferred_rewards_type is not None:
            cards = [card for card in cards if card["rewards_type"] == preferred_rewards_type]
        return cards

    def get_by_id(self, card_id):
        return next(card for card in self.cards if card["card_id"] == card_id)


def _card(card_id, name, rewards, annual_fee=0, signup_bonus=0, rewards_type="cash_back"):
    return {
        "card_id": card_id,
        "card_name": name,
        "issuer": "Test Issuer",
        "source_url": f"https://example.com/cards/{card_id}",
        "source_last_checked": "2026-07-19",
        "annual_fee": annual_fee,
        "signup_bonus": {
            "amount": signup_bonus,
            "currency": "usd",
            "spend_requirement": 0,
            "timeframe_months": 3,
            "estimated_value": signup_bonus,
        },
        "rewards": rewards,
        "rewards_type": rewards_type,
        "point_value": 0.01,
        "eligibility": {"credit_tier": "good_to_excellent", "min_credit_score": 690},
        "annual_credits": [],
        "description": "Test card",
        "best_for": [],
        "foreign_transaction_fee": 0,
        "special_features": [],
    }


def _profile(**overrides):
    spending = {
        "dining": 1000,
        "groceries": 200,
        "travel": 300,
        "gas": 100,
        "streaming": 50,
        "other": 100,
        "flights": 100,
        "hotels": 100,
        "transit": 50,
    }
    spending.update(overrides.pop("spending", {}))
    return UserProfile(
        monthly_spending=MonthlySpending(**spending),
        credit_score="good",
        **overrides,
    )


def test_service_ranks_cards_by_deterministic_value():
    dining_card = _card("dining", "Dining Card", {"dining": 5, "other": 1})
    flat_card = _card("flat", "Flat Card", {"dining": 1.5, "groceries": 1.5, "travel": 1.5, "gas": 1.5, "streaming": 1.5, "other": 1.5})
    service = RecommendationService(card_repository=_FakeRepository([flat_card, dining_card]))

    output = service.recommend(_profile())

    assert output.recommendations[0].card_name == "Dining Card"
    assert output.recommendations[0].optimization_strategy.use_this_card_for == ["dining"]
    assert "Dining Card" in output.portfolio_strategy


def test_service_applies_fee_and_rewards_type_filters():
    no_fee = _card("free", "No Fee", {"dining": 2}, annual_fee=0, rewards_type="cash_back")
    premium = _card("premium", "Premium", {"dining": 6}, annual_fee=500, rewards_type="travel")
    service = RecommendationService(card_repository=_FakeRepository([no_fee, premium]))

    output = service.recommend(_profile(max_annual_fee=100, preferred_rewards_type="cash_back"))

    assert [rec.card_name for rec in output.recommendations] == ["No Fee"]


def test_service_supports_explicit_business_card_filter():
    business = _card("business", "Business Card", {"other": 2}, rewards_type="business")
    service = RecommendationService(card_repository=_FakeRepository([business]))

    output = service.recommend(_profile(preferred_rewards_type="business"))

    assert [rec.card_name for rec in output.recommendations] == ["Business Card"]


def test_spending_analysis_does_not_double_count_travel_subcategories():
    service = RecommendationService(card_repository=_FakeRepository([]))

    analysis = service.analyze_spending(
        _profile(spending={"travel": 300, "flights": 100, "hotels": 100, "transit": 100})
    )

    assert analysis.total_monthly_spend == 1750
    assert "travel subcategories" in analysis.insights[-1]
