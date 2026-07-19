"""Data-quality checks for raw credit card records."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Iterable
from urllib.parse import urlparse


REQUIRED_FIELDS = {
    "card_id",
    "card_name",
    "issuer",
    "annual_fee",
    "signup_bonus",
    "rewards",
    "rewards_type",
    "point_value",
    "eligibility",
    "annual_credits",
    "description",
    "best_for",
    "foreign_transaction_fee",
    "special_features",
    "product_status",
    "source_url",
    "source_last_checked",
}

VALID_PRODUCT_STATUSES = {"active", "closed_to_new_applicants", "replaced", "discontinued"}

OFFICIAL_DOMAINS = {
    "american express": {"americanexpress.com"},
    "apple": {"apple.com"},
    "bilt": {"bilt.com"},
    "capital one": {"capitalone.com"},
    "chase": {"chase.com"},
    "citi": {"citi.com"},
    "citibank": {"citi.com"},
    "discover": {"discover.com"},
    "wells fargo": {"wellsfargo.com"},
}


@dataclass(frozen=True)
class ValidationIssue:
    card_id: str
    severity: str
    code: str
    field: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class CardCatalogValidator:
    """Validate catalog structure, values, uniqueness, and source provenance."""

    def __init__(self, today: date | None = None, stale_after_days: int = 90):
        self.today = today or date.today()
        self.stale_after_days = stale_after_days

    def validate(self, cards: list[dict[str, Any]]) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        issues.extend(self._validate_duplicates(cards))
        for index, card in enumerate(cards):
            issues.extend(self._validate_card(card, index))
        return issues

    def _validate_duplicates(self, cards: Iterable[dict[str, Any]]) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        seen_ids: set[str] = set()
        seen_names: set[str] = set()
        for card in cards:
            card_id = str(card.get("card_id", "<missing>"))
            normalized_name = str(card.get("card_name", "")).strip().casefold()
            if card_id in seen_ids:
                issues.append(self._issue(card_id, "error", "duplicate_card_id", "card_id", "Card ID must be unique."))
            seen_ids.add(card_id)
            if normalized_name and normalized_name in seen_names:
                issues.append(self._issue(card_id, "error", "duplicate_card_name", "card_name", "Card name must be unique."))
            seen_names.add(normalized_name)
        return issues

    def _validate_card(self, card: dict[str, Any], index: int) -> list[ValidationIssue]:
        card_id = str(card.get("card_id", f"row_{index}"))
        issues: list[ValidationIssue] = []

        for field in sorted(REQUIRED_FIELDS - card.keys()):
            issues.append(self._issue(card_id, "error", "missing_required_field", field, f"Missing required field: {field}."))

        issues.extend(self._validate_nonnegative_number(card_id, card, "annual_fee"))
        issues.extend(self._validate_nonnegative_number(card_id, card, "foreign_transaction_fee"))

        point_value = card.get("point_value")
        if not self._is_number(point_value) or float(point_value) <= 0:
            issues.append(self._issue(card_id, "error", "invalid_point_value", "point_value", "Point value must be greater than zero."))

        rewards = card.get("rewards")
        if not isinstance(rewards, dict) or not rewards:
            issues.append(self._issue(card_id, "error", "invalid_rewards", "rewards", "Rewards must be a non-empty object."))
        else:
            for category, rate in rewards.items():
                if not self._is_number(rate) or float(rate) < 0:
                    issues.append(self._issue(card_id, "error", "invalid_reward_rate", f"rewards.{category}", "Reward rates must be nonnegative numbers."))

        status = card.get("product_status")
        if status not in VALID_PRODUCT_STATUSES:
            issues.append(self._issue(card_id, "error", "invalid_product_status", "product_status", f"Status must be one of {sorted(VALID_PRODUCT_STATUSES)}."))

        issues.extend(self._validate_source(card_id, card))
        issues.extend(self._validate_signup_bonus(card_id, card.get("signup_bonus")))
        return issues

    def _validate_source(self, card_id: str, card: dict[str, Any]) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        source_url = card.get("source_url")
        parsed = urlparse(source_url) if isinstance(source_url, str) else None
        if not parsed or parsed.scheme != "https" or not parsed.netloc:
            return [self._issue(card_id, "error", "invalid_source_url", "source_url", "Source URL must be a valid HTTPS URL.")]

        host = parsed.netloc.lower().removeprefix("www.")
        issuer = str(card.get("issuer", "")).strip().casefold()
        allowed_domains = OFFICIAL_DOMAINS.get(issuer)
        if allowed_domains and not any(host == domain or host.endswith(f".{domain}") for domain in allowed_domains):
            issues.append(self._issue(card_id, "error", "unofficial_source_domain", "source_url", f"{host} is not an official domain configured for {card.get('issuer')}."))

        checked = card.get("source_last_checked")
        try:
            checked_date = date.fromisoformat(str(checked))
        except ValueError:
            issues.append(self._issue(card_id, "error", "invalid_source_date", "source_last_checked", "Source date must use YYYY-MM-DD."))
            return issues

        age_days = (self.today - checked_date).days
        if age_days < 0:
            issues.append(self._issue(card_id, "error", "future_source_date", "source_last_checked", "Source check date cannot be in the future."))
        elif age_days > self.stale_after_days:
            issues.append(self._issue(card_id, "warning", "stale_source", "source_last_checked", f"Source was last checked {age_days} days ago."))
        return issues

    def _validate_signup_bonus(self, card_id: str, bonus: Any) -> list[ValidationIssue]:
        if not isinstance(bonus, dict):
            return [self._issue(card_id, "error", "invalid_signup_bonus", "signup_bonus", "Signup bonus must be an object.")]

        amount = bonus.get("amount")
        if amount in (None, 0):
            return []

        qualification_type = bonus.get("qualification_type", "spend")
        if qualification_type == "on_approval":
            return []
        if qualification_type not in {"spend", "tiered_spend", "variable_spend"}:
            return [
                self._issue(
                    card_id,
                    "error",
                    "invalid_bonus_qualification_type",
                    "signup_bonus.qualification_type",
                    "Unknown signup bonus qualification type.",
                )
            ]

        issues: list[ValidationIssue] = []
        for field in ("spend_requirement", "timeframe_months"):
            if bonus.get(field) in (None, 0):
                issues.append(self._issue(card_id, "warning", "incomplete_signup_bonus", f"signup_bonus.{field}", "Published bonus is missing a qualification condition."))
        return issues

    def _validate_nonnegative_number(self, card_id: str, card: dict[str, Any], field: str) -> list[ValidationIssue]:
        value = card.get(field)
        if not self._is_number(value) or float(value) < 0:
            return [self._issue(card_id, "error", "invalid_nonnegative_number", field, f"{field} must be a nonnegative number.")]
        return []

    @staticmethod
    def _is_number(value: Any) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    @staticmethod
    def _issue(card_id: str, severity: str, code: str, field: str, message: str) -> ValidationIssue:
        return ValidationIssue(card_id=card_id, severity=severity, code=code, field=field, message=message)
