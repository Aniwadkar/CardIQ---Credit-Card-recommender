"""End-to-end ETL pipeline for the CardIQ starter catalog."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import CARD_QUALITY_REPORT_PATH, PROCESSED_CARDS_JSON_PATH, RAW_CARDS_JSON_PATH
from src.transformations import CardTransformer
from src.validation import CardCatalogValidator, ValidationIssue


SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class PipelineResult:
    total_cards: int
    processed_cards: int
    error_count: int
    warning_count: int
    output_path: Path
    quality_report_path: Path


class CardEtlPipeline:
    """Extract raw JSON, validate it, transform it, and write pipeline artifacts."""

    def __init__(
        self,
        input_path: Path = RAW_CARDS_JSON_PATH,
        output_path: Path = PROCESSED_CARDS_JSON_PATH,
        quality_report_path: Path = CARD_QUALITY_REPORT_PATH,
        validator: CardCatalogValidator | None = None,
        transformer: CardTransformer | None = None,
    ):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.quality_report_path = Path(quality_report_path)
        self.validator = validator or CardCatalogValidator()
        self.transformer = transformer or CardTransformer()

    def run(self) -> PipelineResult:
        cards = self._extract()
        issues = self.validator.validate(cards)
        error_count = sum(issue.severity == "error" for issue in issues)
        warning_count = sum(issue.severity == "warning" for issue in issues)
        run_at = datetime.now(timezone.utc).isoformat()

        processed_cards = [] if error_count else [self.transformer.transform(card) for card in cards]
        if not error_count:
            self._write_json(
                self.output_path,
                {
                    "schema_version": SCHEMA_VERSION,
                    "generated_at": run_at,
                    "source_file": self.input_path.as_posix(),
                    "card_count": len(processed_cards),
                    "cards": processed_cards,
                },
            )

        self._write_json(
            self.quality_report_path,
            self._build_quality_report(cards, issues, run_at, len(processed_cards)),
        )

        return PipelineResult(
            total_cards=len(cards),
            processed_cards=len(processed_cards),
            error_count=error_count,
            warning_count=warning_count,
            output_path=self.output_path,
            quality_report_path=self.quality_report_path,
        )

    def _extract(self) -> list[dict[str, Any]]:
        payload = json.loads(self.input_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("Raw card catalog must be a JSON array.")
        return payload

    def _build_quality_report(
        self,
        cards: list[dict[str, Any]],
        issues: list[ValidationIssue],
        run_at: str,
        processed_count: int,
    ) -> dict[str, Any]:
        issues_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
        for issue in issues:
            issues_by_card[issue.card_id].append(issue.to_dict())

        severity_counts = Counter(issue.severity for issue in issues)
        issue_code_counts = Counter(issue.code for issue in issues)
        status_counts = Counter(str(card.get("product_status", "missing")) for card in cards)

        return {
            "schema_version": SCHEMA_VERSION,
            "generated_at": run_at,
            "input_file": self.input_path.as_posix(),
            "output_file": self.output_path.as_posix(),
            "pipeline_status": "failed" if severity_counts["error"] else "passed_with_warnings" if severity_counts["warning"] else "passed",
            "summary": {
                "total_cards": len(cards),
                "processed_cards": processed_count,
                "error_count": severity_counts["error"],
                "warning_count": severity_counts["warning"],
                "cards_requiring_review": len(issues_by_card),
                "product_status_counts": dict(sorted(status_counts.items())),
                "issue_code_counts": dict(sorted(issue_code_counts.items())),
            },
            "card_results": [
                {
                    "card_id": str(card.get("card_id", "<missing>")),
                    "passed": not any(issue["severity"] == "error" for issue in issues_by_card.get(str(card.get("card_id")), [])),
                    "issues": issues_by_card.get(str(card.get("card_id")), []),
                }
                for card in cards
            ],
        }

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
