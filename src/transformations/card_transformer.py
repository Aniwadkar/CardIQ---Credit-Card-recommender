"""Transform raw card records into analytics-ready records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from urllib.parse import urlparse


ISSUER_NAMES = {
    "citibank": "Citi",
    "citi": "Citi",
}

REWARDS_TYPE_NAMES = {
    "hotel points": "hotel_points",
}


class CardTransformer:
    """Normalize labels and add deterministic features used by scoring and analysis."""

    def transform(self, card: dict[str, Any]) -> dict[str, Any]:
        processed = deepcopy(card)
        processed["issuer"] = self._normalize_issuer(str(processed["issuer"]))
        processed["rewards_type"] = self._normalize_rewards_type(str(processed["rewards_type"]))

        rewards = {key: float(value) for key, value in processed["rewards"].items()}
        processed["rewards"] = rewards

        annual_fee = float(processed["annual_fee"])
        annual_credit_value = round(
            sum(float(credit.get("value") or 0) for credit in processed.get("annual_credits", [])),
            2,
        )
        base_reward_rate = rewards.get("other", min(rewards.values()))
        max_reward_rate = max(rewards.values())
        source_host = urlparse(processed["source_url"]).netloc.lower().removeprefix("www.")

        processed["derived_features"] = {
            "is_active": processed.get("product_status") == "active",
            "has_annual_fee": annual_fee > 0,
            "has_foreign_transaction_fee": float(processed["foreign_transaction_fee"]) > 0,
            "annual_credit_value": annual_credit_value,
            "effective_annual_fee": round(annual_fee - annual_credit_value, 2),
            "base_reward_rate": float(base_reward_rate),
            "max_reward_rate": float(max_reward_rate),
            "source_domain": source_host,
            "reward_rules_need_review": max_reward_rate > base_reward_rate,
        }
        return processed

    @staticmethod
    def _normalize_issuer(issuer: str) -> str:
        clean = issuer.strip()
        return ISSUER_NAMES.get(clean.casefold(), clean)

    @staticmethod
    def _normalize_rewards_type(rewards_type: str) -> str:
        clean = rewards_type.strip().lower().replace("-", "_").replace(" ", "_")
        return REWARDS_TYPE_NAMES.get(clean, clean)
