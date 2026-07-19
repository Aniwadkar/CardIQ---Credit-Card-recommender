"""Repository for credit card data access.

This keeps the application from depending directly on JSON files. A future
Postgres implementation can preserve this public interface.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from src.data.card_loader import CardLoader


class CardRepository:
    """Read credit cards from the configured backing store."""

    def __init__(self, loader: Optional[CardLoader] = None):
        self.loader = loader or CardLoader()

    def list_cards(self) -> List[Dict]:
        """Return all known cards."""
        return self.loader.load_cards()

    def get_by_id(self, card_id: str) -> Optional[Dict]:
        """Return a card by its stable ID."""
        return self.loader.get_card_by_id(card_id)

    def list_rewards_types(self) -> List[str]:
        """Return rewards types available in the card catalog."""
        return sorted({card["rewards_type"] for card in self.list_cards()})

    def find_candidates(
        self,
        max_annual_fee: Optional[int] = None,
        preferred_rewards_type: Optional[str] = None,
        include_business: bool = False,
    ) -> List[Dict]:
        """Return cards matching user preference filters."""
        cards = [
            card
            for card in self.list_cards()
            if card.get("product_status", "active") == "active"
            and (include_business or card.get("rewards_type") != "business")
        ]

        if max_annual_fee is not None:
            cards = [card for card in cards if float(card["annual_fee"]) <= max_annual_fee]

        if preferred_rewards_type:
            requested = self._normalize_rewards_type(preferred_rewards_type)
            cards = [
                card
                for card in cards
                if self._normalize_rewards_type(card["rewards_type"]) == requested
            ]

        return cards

    @staticmethod
    def _normalize_rewards_type(rewards_type: str) -> str:
        return rewards_type.lower().replace("_", "").replace("-", "").replace(" ", "")
