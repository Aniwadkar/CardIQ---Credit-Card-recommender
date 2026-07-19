"""Pydantic models for agent outputs"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class SpendingAnalysis(BaseModel):
    """Output from Spending Analyzer Agent"""
    total_monthly_spend: float
    total_annual_spend: float
    top_categories: List[str]
    spending_profile: str
    insights: List[str]
    category_percentages: Dict[str, float]

class CardEvaluation(BaseModel):
    """Evaluation for a single card"""
    card_id: str
    card_name: str
    annual_rewards: float
    signup_bonus_value: float
    annual_fee: float
    annual_credits_value: float
    net_value_year_1: float
    net_value_year_2: float
    net_value_year_3: float
    ranking_score: float

class CardEvaluations(BaseModel):
    """Output from Card Evaluator Agent"""
    top_cards: List[CardEvaluation]
    total_cards_evaluated: int

class OptimizationStrategy(BaseModel):
    """Card optimization strategy"""
    use_this_card_for: List[str]
    pair_with: Optional[str] = None
    avoid_using_for: List[str]

class Recommendation(BaseModel):
    """Single card recommendation"""
    rank: int
    card_id: str
    card_name: str
    issuer: str
    source_url: str
    source_last_checked: str
    why_this_card: str
    financial_summary: Dict[str, float]
    how_to_maximize: List[str]
    watch_out_for: List[str]
    optimization_strategy: OptimizationStrategy
    long_term_projection: Dict[str, str]

class RecommendationOutput(BaseModel):
    """Output from Recommendation Synthesizer Agent"""
    recommendations: List[Recommendation]
    portfolio_strategy: str
