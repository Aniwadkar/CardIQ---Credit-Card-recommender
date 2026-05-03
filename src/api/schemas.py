"""Request and response schemas for CardIQ HTTP API."""
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class MonthlySpendingRequest(BaseModel):
    """Monthly spend payload received from API consumers."""

    dining: float = Field(ge=0)
    groceries: float = Field(ge=0)
    travel: float = Field(ge=0)
    gas: float = Field(ge=0)
    streaming: float = Field(ge=0)
    other: float = Field(ge=0)
    flights: Optional[float] = Field(default=0, ge=0)
    hotels: Optional[float] = Field(default=0, ge=0)
    transit: Optional[float] = Field(default=0, ge=0)


class RecommendationRequest(BaseModel):
    """Top-level recommendation request payload."""

    monthly_spending: MonthlySpendingRequest
    credit_score: str = Field(pattern="^(excellent|good|fair)$")
    max_annual_fee: Optional[int] = Field(default=None, ge=0)
    preferred_rewards_type: Optional[str] = None
    planning_to_travel: Optional[bool] = False
    include_formatted_text: bool = True


class RecommendationResponse(BaseModel):
    """Recommendation response for API clients."""

    recommendations: List[Dict[str, Any]]
    portfolio_strategy: str
    formatted_text: Optional[str] = None


class HealthResponse(BaseModel):
    """Service health payload."""

    status: str
    service: str
    mock_mode: bool
