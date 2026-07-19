from src.data.card_loader import CardLoader
from src.repositories import CardRepository
from src.config import CARDS_JSON_PATH, PROCESSED_CARDS_JSON_PATH


def test_all_catalog_cards_have_official_source_metadata():
    cards = CardLoader().load_cards_as_models()

    assert len(cards) == 25
    assert all(card.source_url.startswith("https://") for card in cards)
    assert all(card.source_last_checked == "2026-07-19" for card in cards)


def test_application_uses_processed_catalog_by_default():
    assert CARDS_JSON_PATH == PROCESSED_CARDS_JSON_PATH
    assert CardLoader().json_path == PROCESSED_CARDS_JSON_PATH


def test_unavailable_products_are_not_recommendation_candidates():
    candidates = CardRepository().find_candidates()
    candidate_ids = {card["card_id"] for card in candidates}

    assert "bilt_mastercard" not in candidate_ids
    assert "citi_custom_cash" not in candidate_ids
    assert "ink_business_unlimited_credit_card" not in candidate_ids
    assert len(candidates) == 22


def test_business_cards_can_be_requested_explicitly():
    candidate_ids = {
        card["card_id"] for card in CardRepository().find_candidates(include_business=True)
    }

    assert "ink_business_unlimited_credit_card" in candidate_ids
