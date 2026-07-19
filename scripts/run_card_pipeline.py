"""Run the CardIQ raw-to-processed data pipeline."""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipelines import CardEtlPipeline


def main() -> int:
    result = CardEtlPipeline().run()
    print(
        "Card pipeline complete: "
        f"{result.processed_cards}/{result.total_cards} processed, "
        f"{result.error_count} errors, {result.warning_count} warnings."
    )
    print(f"Processed data: {result.output_path}")
    print(f"Quality report: {result.quality_report_path}")
    return 1 if result.error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
