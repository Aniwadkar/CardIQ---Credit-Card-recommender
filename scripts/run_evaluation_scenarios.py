"""Generate the CardIQ portfolio evaluation artifacts."""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation import write_evaluation_outputs


def main() -> int:
    json_path, markdown_path = write_evaluation_outputs(PROJECT_ROOT / "outputs/evaluation")
    print(f"Scenario results: {json_path}")
    print(f"Scenario summary: {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
