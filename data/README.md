# CardIQ data layers

The card catalog follows a simple raw-to-processed pipeline:

- `raw/` contains source records collected from issuer pages. Treat these files as pipeline inputs.
- `processed/` contains normalized records and deterministic derived features for analytics and scoring.
- `quality/` contains validation results and the manual-review queue for each pipeline run.
- `vector_db/` contains generated retrieval artifacts used by the AI explanation layer.

Run the pipeline from the project root:

```powershell
python scripts/run_card_pipeline.py
```

The command exits with a nonzero status when validation finds a blocking error. Warnings do not block processing and are recorded in `quality/card_quality_report.json`.
