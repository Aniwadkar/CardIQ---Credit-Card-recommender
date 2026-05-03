from types import SimpleNamespace

from fastapi.testclient import TestClient

from src.api.server import app


class _FakeRecommendation:
    def model_dump(self):
        return {
            "rank": 1,
            "card_id": "test_card",
            "card_name": "Test Card",
            "why_this_card": "Strong fit for your spending mix.",
            "financial_summary": {
                "year_1_value": 500.0,
                "year_2_value": 800.0,
                "year_3_value": 1100.0,
                "annual_rewards": 400.0,
                "annual_fee": 95.0,
                "signup_bonus": 200.0,
            },
            "how_to_maximize": ["Use for dining", "Use for groceries"],
            "watch_out_for": ["Annual fee applies"],
            "optimization_strategy": {
                "use_this_card_for": ["dining"],
                "pair_with": "No-fee 2% card",
                "avoid_using_for": ["uncategorized spend"],
            },
            "long_term_projection": {
                "one_year": "Positive",
                "two_years": "Stronger",
                "three_years": "Compounds well",
            },
        }


class _FakeOrchestrator:
    def process(self, user_profile, verbose=False):
        return SimpleNamespace(
            recommendations=[_FakeRecommendation()],
            portfolio_strategy="Use Test Card as primary.",
        )

    def format_recommendation_output(self, recommendations):
        return "Formatted recommendation output"


class _FakeClaudeClient:
    def __init__(self):
        self.mock_mode = True


def _sample_payload(include_formatted_text=True):
    return {
        "monthly_spending": {
            "dining": 500,
            "groceries": 300,
            "travel": 200,
            "gas": 100,
            "streaming": 50,
            "other": 400,
            "flights": 50,
            "hotels": 50,
            "transit": 50,
        },
        "credit_score": "good",
        "include_formatted_text": include_formatted_text,
    }


def test_health_endpoint(monkeypatch):
    monkeypatch.setattr("src.api.server.ClaudeClient", _FakeClaudeClient)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "cardiq-api"
    assert payload["mock_mode"] is True


def test_recommendations_endpoint_success(monkeypatch):
    monkeypatch.setattr("src.api.server.get_orchestrator", lambda: _FakeOrchestrator())
    client = TestClient(app)

    response = client.post("/recommendations", json=_sample_payload(include_formatted_text=True))

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["recommendations"]) == 1
    assert payload["recommendations"][0]["card_name"] == "Test Card"
    assert payload["portfolio_strategy"] == "Use Test Card as primary."
    assert payload["formatted_text"] == "Formatted recommendation output"


def test_recommendations_validation_error():
    client = TestClient(app)

    bad_payload = _sample_payload()
    bad_payload["credit_score"] = "invalid-tier"

    response = client.post("/recommendations", json=bad_payload)

    assert response.status_code == 422
