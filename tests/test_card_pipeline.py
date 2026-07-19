import json
from datetime import date
from pathlib import Path

from src.pipelines import CardEtlPipeline
from src.transformations import CardTransformer
from src.validation import CardCatalogValidator


PROJECT_ROOT = Path(__file__).parent.parent
RAW_CATALOG = PROJECT_ROOT / "data/raw/credit_cards_llm_special_features_filled.json"


def test_pipeline_writes_processed_catalog_and_quality_report(tmp_path):
    output_path = tmp_path / "processed" / "cards.json"
    report_path = tmp_path / "quality" / "report.json"
    pipeline = CardEtlPipeline(
        input_path=RAW_CATALOG,
        output_path=output_path,
        quality_report_path=report_path,
        validator=CardCatalogValidator(today=date(2026, 7, 19)),
    )

    result = pipeline.run()
    processed = json.loads(output_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert result.total_cards == 25
    assert result.processed_cards == 25
    assert result.error_count == 0
    assert processed["schema_version"] == "1.0"
    assert processed["card_count"] == 25
    assert all("derived_features" in card for card in processed["cards"])
    assert result.warning_count == 0
    assert report["pipeline_status"] == "passed"
    assert report["summary"]["product_status_counts"] == {
        "active": 23,
        "closed_to_new_applicants": 1,
        "replaced": 1,
    }


def test_validator_rejects_unofficial_source_domain():
    card = json.loads(RAW_CATALOG.read_text(encoding="utf-8"))[0]
    card["source_url"] = "https://example.com/card"

    issues = CardCatalogValidator(today=date(2026, 7, 19)).validate([card])

    assert "unofficial_source_domain" in {issue.code for issue in issues}


def test_validator_accepts_bonus_granted_on_approval():
    card = json.loads(RAW_CATALOG.read_text(encoding="utf-8"))[15]
    card["signup_bonus"].update(
        spend_requirement=None,
        timeframe_months=None,
        qualification_type="on_approval",
    )

    issues = CardCatalogValidator(today=date(2026, 7, 19)).validate([card])

    assert "incomplete_signup_bonus" not in {issue.code for issue in issues}


def test_transformer_normalizes_issuer_and_builds_features():
    card = json.loads(RAW_CATALOG.read_text(encoding="utf-8"))[7]

    processed = CardTransformer().transform(card)

    assert processed["issuer"] == "Citi"
    assert processed["derived_features"]["source_domain"] == "citi.com"
    assert processed["derived_features"]["is_active"] is True
    assert processed["derived_features"]["max_reward_rate"] == 5.0
    assert processed["derived_features"]["reward_rules_need_review"] is True
