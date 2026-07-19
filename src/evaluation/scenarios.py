"""Reproducible recommendation scenarios for portfolio evaluation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.models.user_input import MonthlySpending, UserProfile
from src.services import RecommendationService


EVALUATION_SCENARIOS: dict[str, dict[str, Any]] = {
    "food_focused": {
        "description": "High monthly dining and grocery spending.",
        "profile": {
            "monthly_spending": {
                "dining": 1200,
                "groceries": 900,
                "travel": 100,
                "gas": 150,
                "streaming": 80,
                "other": 300,
                "flights": 0,
                "hotels": 0,
                "transit": 0,
            },
            "credit_score": "good",
            "max_annual_fee": 500,
        },
    },
    "frequent_traveler": {
        "description": "Heavy travel spending split across flights, hotels, and transit.",
        "profile": {
            "monthly_spending": {
                "dining": 400,
                "groceries": 250,
                "travel": 1800,
                "gas": 100,
                "streaming": 50,
                "other": 300,
                "flights": 900,
                "hotels": 700,
                "transit": 200,
            },
            "credit_score": "excellent",
            "max_annual_fee": 500,
        },
    },
    "no_annual_fee": {
        "description": "Everyday spending with a strict zero-dollar annual-fee limit.",
        "profile": {
            "monthly_spending": {
                "dining": 300,
                "groceries": 500,
                "travel": 100,
                "gas": 250,
                "streaming": 60,
                "other": 900,
                "flights": 0,
                "hotels": 0,
                "transit": 0,
            },
            "credit_score": "good",
            "max_annual_fee": 0,
        },
    },
}


def evaluate_scenarios(
    service: RecommendationService | None = None,
) -> dict[str, Any]:
    """Run the fixed scenarios through the production recommendation service."""
    recommendation_service = service or RecommendationService()
    results = []

    for scenario_id, scenario in EVALUATION_SCENARIOS.items():
        profile_data = scenario["profile"]
        user_profile = UserProfile(
            monthly_spending=MonthlySpending(**profile_data["monthly_spending"]),
            credit_score=profile_data["credit_score"],
            max_annual_fee=profile_data["max_annual_fee"],
        )
        output = recommendation_service.recommend(user_profile)
        results.append(
            {
                "scenario_id": scenario_id,
                "description": scenario["description"],
                "profile": profile_data,
                "recommendations": [recommendation.model_dump() for recommendation in output.recommendations],
                "portfolio_strategy": output.portfolio_strategy,
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scenario_count": len(results),
        "scenarios": results,
    }


def write_evaluation_outputs(
    output_dir: Path = Path("outputs/evaluation"),
) -> tuple[Path, Path]:
    """Write machine-readable results and a compact presentation summary."""
    payload = evaluate_scenarios()
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "scenario_results.json"
    markdown_path = output_dir / "scenario_summary.md"

    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(_render_markdown(payload), encoding="utf-8")
    return json_path, markdown_path


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# CardIQ Evaluation Scenarios",
        "",
        "These fixed profiles demonstrate that the deterministic ranking changes with spending behavior and fee preferences.",
        "",
    ]
    for scenario in payload["scenarios"]:
        lines.extend(
            [
                f"## {scenario['scenario_id'].replace('_', ' ').title()}",
                "",
                scenario["description"],
                "",
                "| Rank | Card | Issuer | Year 1 value | 3-year value | Annual fee |",
                "| ---: | --- | --- | ---: | ---: | ---: |",
            ]
        )
        for recommendation in scenario["recommendations"]:
            financial = recommendation["financial_summary"]
            lines.append(
                f"| {recommendation['rank']} | {recommendation['card_name']} | "
                f"{recommendation['issuer']} | ${financial['year_1_value']:,.0f} | "
                f"${financial['year_3_value']:,.0f} | ${financial['annual_fee']:,.0f} |"
            )
        lines.extend(["", f"Strategy: {scenario['portfolio_strategy']}", ""])
    return "\n".join(lines) + "\n"
