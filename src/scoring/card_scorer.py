"""Deterministic credit card scoring."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from src.models.agent_outputs import CardEvaluation, CardEvaluations
from src.models.user_input import UserProfile
from src.utils.calculations import (
    calculate_category_rewards,
    calculate_net_value,
    calculate_total_annual_credits,
)


@dataclass(frozen=True)
class RankingWeights:
    """Weights used to balance signup-bonus value against ongoing value."""

    year_1: float = 0.30
    year_2: float = 0.40
    year_3: float = 0.30


class CardScorer:
    """Score and rank cards from structured card and user data."""

    def __init__(self, ranking_weights: RankingWeights | None = None):
        self.ranking_weights = ranking_weights or RankingWeights()

    def rank_cards(self, cards: Iterable[Dict], user_profile: UserProfile) -> CardEvaluations:
        """Evaluate cards and return them sorted by ranking score."""
        evaluations = [self.evaluate_card(card, user_profile) for card in cards]
        evaluations.sort(key=lambda card: card.ranking_score, reverse=True)

        return CardEvaluations(
            top_cards=evaluations[:5],
            total_cards_evaluated=len(evaluations),
        )

    def evaluate_card(self, card: Dict, user_profile: UserProfile) -> CardEvaluation:
        """Calculate rewards, net values, and ranking score for one card."""
        spending_dict = user_profile.monthly_spending.model_dump()

        annual_rewards = calculate_category_rewards(
            monthly_spending=spending_dict,
            card_rewards=card["rewards"],
            point_value=float(card["point_value"]),
        )

        signup_bonus_value = float(card["signup_bonus"].get("estimated_value") or 0)
        annual_credits_value = calculate_total_annual_credits(card.get("annual_credits", []))
        annual_fee = float(card["annual_fee"])

        net_value_year_1 = calculate_net_value(
            annual_rewards=annual_rewards,
            signup_bonus_value=signup_bonus_value,
            annual_fee=annual_fee,
            annual_credits_value=annual_credits_value,
            year=1,
        )
        net_value_year_2 = calculate_net_value(
            annual_rewards=annual_rewards,
            signup_bonus_value=signup_bonus_value,
            annual_fee=annual_fee,
            annual_credits_value=annual_credits_value,
            year=2,
        )
        net_value_year_3 = calculate_net_value(
            annual_rewards=annual_rewards,
            signup_bonus_value=signup_bonus_value,
            annual_fee=annual_fee,
            annual_credits_value=annual_credits_value,
            year=3,
        )

        ranking_score = (
            net_value_year_1 * self.ranking_weights.year_1
            + net_value_year_2 * self.ranking_weights.year_2
            + net_value_year_3 * self.ranking_weights.year_3
        )

        return CardEvaluation(
            card_id=card["card_id"],
            card_name=card["card_name"],
            annual_rewards=round(annual_rewards, 2),
            signup_bonus_value=round(signup_bonus_value, 2),
            annual_fee=annual_fee,
            annual_credits_value=round(annual_credits_value, 2),
            net_value_year_1=round(net_value_year_1, 2),
            net_value_year_2=round(net_value_year_2, 2),
            net_value_year_3=round(net_value_year_3, 2),
            ranking_score=round(ranking_score, 2),
        )
