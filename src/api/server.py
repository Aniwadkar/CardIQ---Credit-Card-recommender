"""FastAPI server for CardIQ recommendations."""
from functools import lru_cache

from fastapi import FastAPI, HTTPException

from src.agents.orchestrator import Orchestrator
from src.api.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    HealthResponse,
)
from src.models.user_input import UserProfile, MonthlySpending
from src.api.claude_client import ClaudeClient


app = FastAPI(
    title="CardIQ API",
    description="AI-powered credit card recommendation service",
    version="1.0.0",
)


@lru_cache(maxsize=1)
def get_orchestrator() -> Orchestrator:
    """Create a single orchestrator instance for the process."""
    return Orchestrator()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health endpoint for readiness/liveness checks."""
    client = ClaudeClient()
    return HealthResponse(status="ok", service="cardiq-api", mock_mode=client.mock_mode)


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

        orchestrator = get_orchestrator()
        output_model = orchestrator.process(user_profile, verbose=False)

        formatted_text = None
        if payload.include_formatted_text:
            formatted_text = orchestrator.format_recommendation_output(output_model)

        return RecommendationResponse(
            recommendations=[r.model_dump() for r in output_model.recommendations],
            portfolio_strategy=output_model.portfolio_strategy,
            formatted_text=formatted_text,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {exc}") from exc
