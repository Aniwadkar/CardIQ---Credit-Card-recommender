"""Deterministic recommendation service.

The service owns ranking and structured recommendations. LLM/AI layers can
decorate this output later without changing the core decision engine.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from src.models.agent_outputs import (
    CardEvaluation,
    OptimizationStrategy,
    Recommendation,
    RecommendationOutput,
    SpendingAnalysis,
)
from src.models.user_input import UserProfile
from src.repositories import CardRepository
from src.scoring import CardScorer


CORE_SPENDING_CATEGORIES = ("dining", "groceries", "travel", "gas", "streaming", "other")


class RecommendationService:
    """Generate card recommendations from data and deterministic scoring."""

    def __init__(
        self,
        card_repository: Optional[CardRepository] = None,
        card_scorer: Optional[CardScorer] = None,
    ):
        self.card_repository = card_repository or CardRepository()
        self.card_scorer = card_scorer or CardScorer()

    def recommend(self, user_profile: UserProfile, limit: int = 3) -> RecommendationOutput:
        """Return ranked, explainable recommendations for a user."""
        spending_analysis = self.analyze_spending(user_profile)
        candidates = self.card_repository.find_candidates(
            max_annual_fee=user_profile.max_annual_fee,
            preferred_rewards_type=user_profile.preferred_rewards_type,
            include_business=user_profile.preferred_rewards_type == "business",
        )
        evaluations = self.card_scorer.rank_cards(candidates, user_profile)

        recommendations: List[Recommendation] = []
        for rank, evaluation in enumerate(evaluations.top_cards[:limit], start=1):
            card = self.card_repository.get_by_id(evaluation.card_id)
            if card is None:
                continue
            pair_with = evaluations.top_cards[1].card_name if rank == 1 and len(evaluations.top_cards) > 1 else None
            recommendations.append(
                self._build_recommendation(
                    rank=rank,
                    card=card,
                    evaluation=evaluation,
                    spending_analysis=spending_analysis,
                    pair_with=pair_with,
                )
            )

        return RecommendationOutput(
            recommendations=recommendations,
            portfolio_strategy=self._build_portfolio_strategy(recommendations, spending_analysis),
        )

    def analyze_spending(self, user_profile: UserProfile) -> SpendingAnalysis:
        """Create a deterministic spending profile without an LLM call."""
        spending = user_profile.monthly_spending.model_dump()
        core_spending = {category: float(spending.get(category) or 0) for category in CORE_SPENDING_CATEGORIES}
        total_monthly = sum(core_spending.values())
        total_annual = total_monthly * 12

        top_categories = [
            category
            for category, amount in sorted(core_spending.items(), key=lambda item: item[1], reverse=True)
            if amount > 0
        ][:3]

        category_percentages = {
            category: round((amount / total_monthly) * 100, 1) if total_monthly else 0.0
            for category, amount in core_spending.items()
        }

        return SpendingAnalysis(
            total_monthly_spend=round(total_monthly, 2),
            total_annual_spend=round(total_annual, 2),
            top_categories=top_categories,
            spending_profile=self._classify_spending_profile(top_categories, core_spending),
            insights=self._build_spending_insights(top_categories, category_percentages, spending),
            category_percentages=category_percentages,
        )

    def _build_recommendation(
        self,
        rank: int,
        card: Dict,
        evaluation: CardEvaluation,
        spending_analysis: SpendingAnalysis,
        pair_with: Optional[str],
    ) -> Recommendation:
        use_categories = self._best_use_categories(card, spending_analysis.top_categories)
        avoid_categories = self._avoid_categories(card, use_categories)

        return Recommendation(
            rank=rank,
            card_id=card["card_id"],
            card_name=card["card_name"],
            issuer=card["issuer"],
            source_url=card["source_url"],
            source_last_checked=card["source_last_checked"],
            why_this_card=self._why_this_card(card, evaluation, spending_analysis),
            financial_summary={
                "year_1_value": evaluation.net_value_year_1,
                "year_2_value": evaluation.net_value_year_2,
                "year_3_value": evaluation.net_value_year_3,
                "annual_rewards": evaluation.annual_rewards,
                "annual_fee": evaluation.annual_fee,
                "signup_bonus": evaluation.signup_bonus_value,
                "annual_credits": evaluation.annual_credits_value,
                "ranking_score": evaluation.ranking_score,
            },
            how_to_maximize=self._how_to_maximize(card, use_categories),
            watch_out_for=self._watch_out_for(card, evaluation),
            optimization_strategy=OptimizationStrategy(
                use_this_card_for=use_categories,
                pair_with=pair_with,
                avoid_using_for=avoid_categories,
            ),
            long_term_projection={
                "one_year": f"Estimated net value of ${evaluation.net_value_year_1:,.2f}, including first-year bonus value.",
                "two_years": f"Estimated cumulative value of ${evaluation.net_value_year_2:,.2f} after two years.",
                "three_years": f"Estimated cumulative value of ${evaluation.net_value_year_3:,.2f} after three years.",
            },
        )

    def _classify_spending_profile(self, top_categories: List[str], spending: Dict[str, float]) -> str:
        if not top_categories:
            return "low_spend"
        top = top_categories[0]
        if top == "dining":
            return "dining_focused"
        if top == "travel":
            return "travel_focused"
        if top == "groceries":
            return "household_spender"
        if top == "gas":
            return "commuter"
        if spending.get("travel", 0) + spending.get("dining", 0) > spending.get("other", 0):
            return "lifestyle_rewards"
        return "general_spender"

    def _build_spending_insights(
        self,
        top_categories: List[str],
        category_percentages: Dict[str, float],
        spending: Dict[str, float],
    ) -> List[str]:
        if not top_categories:
            return ["No monthly spending was provided, so recommendations are based mainly on card baseline value."]

        insights = [
            f"Your largest category is {top_categories[0]}, representing {category_percentages[top_categories[0]]}% of core monthly spend."
        ]

        if len(top_categories) > 1:
            insights.append(
                f"Your top categories are {', '.join(top_categories)}, so bonus-category fit matters more than flat-rate rewards."
            )

        travel_detail = sum(float(spending.get(category) or 0) for category in ("flights", "hotels", "transit"))
        if travel_detail:
            insights.append(
                f"You provided ${travel_detail:,.2f} in travel subcategories, which are scored without double-counting general travel."
            )

        return insights[:3]

    def _why_this_card(
        self,
        card: Dict,
        evaluation: CardEvaluation,
        spending_analysis: SpendingAnalysis,
    ) -> str:
        top_categories = ", ".join(spending_analysis.top_categories) or "your entered categories"
        return (
            f"{card['card_name']} ranks well for {top_categories} with an estimated "
            f"${evaluation.annual_rewards:,.2f} in annual rewards. After fees, credits, and signup value, "
            f"its blended ranking score is ${evaluation.ranking_score:,.2f}."
        )

    def _best_use_categories(self, card: Dict, top_categories: List[str]) -> List[str]:
        rewards = card["rewards"]
        categories = [category for category in top_categories if rewards.get(category, 0) > 1]
        if categories:
            return categories

        best_rate = max(rewards.values()) if rewards else 0
        return [category for category, rate in rewards.items() if rate == best_rate][:3]

    def _avoid_categories(self, card: Dict, use_categories: List[str]) -> List[str]:
        rewards = card["rewards"]
        if not rewards:
            return []

        best_rate = max(rewards.values())
        avoid = [
            category
            for category, rate in rewards.items()
            if category not in use_categories and rate < best_rate
        ]
        return avoid[:3]

    def _how_to_maximize(self, card: Dict, use_categories: List[str]) -> List[str]:
        tips = [f"Use this card for {category} purchases to capture its stronger reward rate." for category in use_categories[:3]]

        if card.get("annual_credits"):
            tips.append("Use eligible annual credits only when they match purchases you would already make.")

        if card.get("signup_bonus", {}).get("spend_requirement"):
            requirement = card["signup_bonus"]["spend_requirement"]
            months = card["signup_bonus"].get("timeframe_months")
            tips.append(f"Plan spending carefully if pursuing the ${requirement:,.0f} signup-bonus requirement over {months} months.")

        return tips[:5] or ["Use this card where its reward rate is strongest relative to your alternatives."]

    def _watch_out_for(self, card: Dict, evaluation: CardEvaluation) -> List[str]:
        warnings = []

        if evaluation.annual_fee:
            warnings.append(f"This card has a ${evaluation.annual_fee:,.0f} annual fee, so ongoing value matters after year one.")

        if card.get("foreign_transaction_fee", 0):
            warnings.append(f"It has a {card['foreign_transaction_fee']}% foreign transaction fee, which can hurt travel value.")

        if card.get("annual_credits"):
            warnings.append("Annual credits may require specific merchants or usage patterns, so do not treat all credits as automatic cash.")

        return warnings[:3] or ["Confirm current issuer terms before applying because card offers change over time."]

    def _build_portfolio_strategy(
        self,
        recommendations: List[Recommendation],
        spending_analysis: SpendingAnalysis,
    ) -> str:
        if not recommendations:
            return "No cards matched the current filters. Try increasing the annual fee limit or clearing the rewards-type preference."

        if len(recommendations) == 1:
            return f"Use {recommendations[0].card_name} as the primary card for your {spending_analysis.spending_profile} profile."

        return (
            f"Use {recommendations[0].card_name} as the primary card, then compare it with "
            f"{recommendations[1].card_name} for categories where the second card has stronger rewards or lower friction."
        )
