"""Add verified official product sources to the starter card catalog."""

import json
from pathlib import Path


CATALOG_PATH = Path("data/raw/credit_cards_llm_special_features_filled.json")
CHECKED_ON = "2026-07-19"

SOURCES = {
    "ink_business_unlimited_credit_card": "https://creditcards.chase.com/business-credit-cards/ink/unlimited",
    "american_express_platinum": "https://www.americanexpress.com/us/credit-cards/card/platinum/",
    "capital_one_quicksilver": "https://www.capitalone.com/credit-cards/quicksilver/",
    "capital_one_venture_x": "https://www.capitalone.com/credit-cards/venture-x/",
    "wells_fargo_autograph_journey": "https://creditcards.wellsfargo.com/autograph-journey-visa-credit-card/",
    "chase_world_of_hyatt": "https://creditcards.chase.com/travel-credit-cards/world-of-hyatt-credit-card",
    "bilt_mastercard": "https://www.bilt.com/card",
    "coscto_anywhere_visa": "https://www.citi.com/credit-cards/citi-costco-anywhere-visa-credit-card",
    "american_express_gold": "https://www.americanexpress.com/us/credit-cards/card/gold-card/",
    "wells_fargo_autograph": "https://creditcards.wellsfargo.com/autograph-visa-credit-card/",
    "capital_one_savor": "https://www.capitalone.com/credit-cards/savor/",
    "chase_freedom_unlimited": "https://creditcards.chase.com/cash-back-credit-cards/freedom/unlimited",
    "discover_it_cash_back": "https://www.discover.com/credit-cards/cash-back/it-card/",
    "american_express_blue_cash_everyday": "https://www.americanexpress.com/us/credit-cards/card/blue-cash-everyday/",
    "wells_fargo_active_cash": "https://creditcards.wellsfargo.com/active-cash-credit-card/",
    "chase_amazon_prime_visa": "https://creditcards.chase.com/cash-back-credit-cards/amazon-prime-rewards",
    "citi_doublecash": "https://www.citi.com/credit-cards/citi-double-cash-credit-card/",
    "chase_sapphire_preferred_card": "https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred",
    "chase_sapphire_reserve": "https://creditcards.chase.com/rewards-credit-cards/sapphire/reserve",
    "citi_custom_cash": "https://www.citi.com/credit-cards/citi-custom-cash-credit-card/",
    "chase_freedom_flex": "https://creditcards.chase.com/cash-back-credit-cards/freedom/flex",
    "apple_card": "https://www.apple.com/apple-card/",
    "citi_strata_elite_card": "https://www.citi.com/credit-cards/citi-strata-elite-credit-card",
    "blue_cash_preferred_card_from_american_express": "https://www.americanexpress.com/us/credit-cards/card/blue-cash-preferred/",
    "capital_one_venture_rewards_credit_card": "https://www.capitalone.com/credit-cards/venture/",
}

STATUS_NOTES = {
    "bilt_mastercard": (
        "replaced",
        "The original Bilt Mastercard is no longer the current product. Bilt now offers Blue, Obsidian, and Palladium cards.",
    ),
    "citi_custom_cash": (
        "closed_to_new_applicants",
        "Citi stopped accepting new applications on May 28, 2026; existing cardmembers are not affected.",
    ),
}


def apply_verified_corrections(cards: list[dict]) -> None:
    by_id = {card["card_id"]: card for card in cards}

    ink_bonus = by_id["ink_business_unlimited_credit_card"]["signup_bonus"]
    ink_bonus.update(amount=1000, spend_requirement=8000, timeframe_months=4, estimated_value=1000.0)

    by_id["american_express_platinum"]["signup_bonus"]["spend_requirement"] = 12000

    quicksilver_bonus = by_id["capital_one_quicksilver"]["signup_bonus"]
    quicksilver_bonus.update(spend_requirement=500, timeframe_months=3)

    by_id["capital_one_venture_x"]["signup_bonus"]["timeframe_months"] = 3

    hyatt_bonus = by_id["chase_world_of_hyatt"]["signup_bonus"]
    hyatt_bonus.update(
        amount=75000,
        spend_requirement=5000,
        timeframe_months=6,
        estimated_value=937.5,
        qualification_type="tiered_spend",
        details=(
            "45,000 points after $5,000 in 3 months, plus up to 30,000 points "
            "by earning 2X total on normally 1X purchases for 6 months, capped at $15,000 spend."
        ),
    )

    savor = by_id["capital_one_savor"]
    savor["signup_bonus"].update(
        amount=250,
        spend_requirement=500,
        timeframe_months=3,
        estimated_value=250.0,
    )
    savor["rewards"].update(dining=3.0, groceries=3.0, streaming=3.0)
    savor["foreign_transaction_fee"] = 0.0

    costco = by_id["coscto_anywhere_visa"]
    costco["card_name"] = "Costco Anywhere Visa Card by Citi"
    costco["foreign_transaction_fee"] = 0.0

    by_id["chase_amazon_prime_visa"]["foreign_transaction_fee"] = 0.0
    prime_bonus = by_id["chase_amazon_prime_visa"]["signup_bonus"]
    prime_bonus.update(
        qualification_type="on_approval",
        details="Amazon Gift Card is loaded to the eligible Prime member's account upon approval.",
    )

    freedom_bonus = by_id["chase_freedom_unlimited"]["signup_bonus"]
    freedom_bonus["spend_requirement"] = 500

    everyday_bonus = by_id["american_express_blue_cash_everyday"]["signup_bonus"]
    everyday_bonus.update(
        spend_requirement=2000,
        timeframe_months=6,
        qualification_type="variable_spend",
        details="Apply to learn the welcome offer; the published offer is as high as $200.",
    )
    by_id["chase_freedom_flex"]["rewards"]["dining"] = 3.0
    by_id["blue_cash_preferred_card_from_american_express"]["foreign_transaction_fee"] = 2.7
    by_id["american_express_blue_cash_everyday"]["foreign_transaction_fee"] = 2.7

    preferred = by_id["chase_sapphire_preferred_card"]
    preferred["signup_bonus"]["spend_requirement"] = 5000
    preferred["annual_credits"] = [
        {"name": "$100 Chase Travel hotel credit", "value": 100, "category": "travel"}
    ]
    preferred["rewards"].update(gas=3.0, streaming=3.0)

    reserve = by_id["chase_sapphire_reserve"]
    reserve["signup_bonus"].update(amount=100000, estimated_value=1250.0)

    venture = by_id["capital_one_venture_rewards_credit_card"]
    venture["signup_bonus"]["timeframe_months"] = 3


def main() -> None:
    cards = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    card_ids = {card["card_id"] for card in cards}

    missing_sources = card_ids - SOURCES.keys()
    unknown_sources = SOURCES.keys() - card_ids
    if missing_sources or unknown_sources:
        raise ValueError(
            f"Source map mismatch; missing={sorted(missing_sources)}, unknown={sorted(unknown_sources)}"
        )

    apply_verified_corrections(cards)

    for card in cards:
        card_id = card["card_id"]
        status, note = STATUS_NOTES.get(card_id, ("active", None))
        if card["signup_bonus"].get("amount") is not None:
            card["signup_bonus"].setdefault("qualification_type", "spend")
        card["product_status"] = status
        card["source_url"] = SOURCES[card_id]
        card["source_last_checked"] = CHECKED_ON
        if note:
            card["source_note"] = note
        else:
            card.pop("source_note", None)

    CATALOG_PATH.write_text(
        json.dumps(cards, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
