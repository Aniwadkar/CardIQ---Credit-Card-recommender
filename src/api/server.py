"""FastAPI server for CardIQ recommendations."""
from functools import lru_cache

from fastapi import FastAPI, HTTPException

from src.api.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    HealthResponse,
)
from src.models.user_input import UserProfile, MonthlySpending
from src.services import RecommendationService


app = FastAPI(
    title="CardIQ API",
    description="AI-powered credit card recommendation service",
    version="1.0.0",
)


@lru_cache(maxsize=1)
def get_recommendation_service() -> RecommendationService:
    """Create a single recommendation service for the process."""
    return RecommendationService()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health endpoint for readiness/liveness checks."""
    return HealthResponse(status="ok", service="cardiq-api", mock_mode=False)


@app.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(payload: RecommendationRequest) -> RecommendationResponse:
    """Generate personalized recommendations from spending profile."""
    try:
        user_profile = UserProfile(
            monthly_spending=MonthlySpending(**payload.monthly_spending.model_dump()),
            credit_score=payload.credit_score,
            max_annual_fee=payload.max_annual_fee,
            preferred_rewards_type=payload.preferred_rewards_type,
            planning_to_travel=payload.planning_to_travel,
        )

        recommendation_service = get_recommendation_service()
        output_model = recommendation_service.recommend(user_profile)

        formatted_text = None
        if payload.include_formatted_text:
            formatted_text = _format_recommendation_output(output_model)

        return RecommendationResponse(
            recommendations=[r.model_dump() for r in output_model.recommendations],
            portfolio_strategy=output_model.portfolio_strategy,
            formatted_text=formatted_text,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {exc}") from exc


def _format_recommendation_output(output_model) -> str:
    """Format structured recommendations for simple API consumers."""
    lines = ["YOUR PERSONALIZED CREDIT CARD RECOMMENDATIONS", "=" * 48, ""]

    for rec in output_model.recommendations:
        lines.extend(
            [
                f"RANK #{rec.rank}: {rec.card_name}",
                "-" * 48,
                f"WHY THIS CARD: {rec.why_this_card}",
                "FINANCIAL SUMMARY:",
                f"  Year 1 Value: ${rec.financial_summary['year_1_value']:,.2f}",
                f"  Year 2 Value: ${rec.financial_summary['year_2_value']:,.2f}",
                f"  Year 3 Value: ${rec.financial_summary['year_3_value']:,.2f}",
                f"  Annual Fee: ${rec.financial_summary['annual_fee']:,.2f}",
                "",
                "HOW TO MAXIMIZE:",
            ]
        )
        lines.extend(f"  - {tip}" for tip in rec.how_to_maximize)
        lines.extend(["", "WATCH OUT FOR:"])
        lines.extend(f"  - {warning}" for warning in rec.watch_out_for)
        lines.append("")

    lines.extend(["PORTFOLIO STRATEGY:", output_model.portfolio_strategy])
    return "\n".join(lines)
