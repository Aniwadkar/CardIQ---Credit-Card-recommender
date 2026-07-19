# CardIQ

CardIQ is a data-backed credit card recommendation system built around a curated catalog of 25 U.S. cards. It validates issuer-sourced card data, produces an analytics-ready dataset, and ranks active consumer cards using deterministic calculations based on a user's monthly spending.

The project intentionally stays focused on 25 cards. Its goal is transparent data quality and explainable results, not catalog size.

## What It Demonstrates

- Data ingestion from a versioned raw JSON catalog
- Source provenance and offer verification dates
- Validation with blocking errors and reviewable warnings
- Raw-to-processed ETL with deterministic derived features
- Explainable first-year and multi-year value calculations
- FastAPI web and JSON interfaces
- Reproducible evaluation scenarios
- Container deployment to Google Cloud Run

## Architecture

```text
Official issuer pages
        |
        v
data/raw credit card catalog
        |
        v
Validation -> quality report
        |
        v
Transformation -> data/processed/cards_processed.json
        |
        v
Repository -> deterministic scoring -> top 3 recommendations
        |                                  |
        v                                  v
FastAPI JSON API                    Web comparison UI
```

The active recommendation path does not ask an LLM to calculate or rank cards. This keeps the financial output reproducible and testable. Experimental agent and RAG modules remain in `src/agents` and `src/rag`, but they do not control the production ranking.

## Data Layers

| Layer | Purpose |
| --- | --- |
| `data/raw/` | Curated issuer-sourced input records |
| `data/processed/` | Normalized records and derived features used by the app |
| `data/quality/` | Pipeline status and per-card validation results |
| `outputs/evaluation/` | Fixed scenario results for portfolio review |

The application reads `data/processed/cards_processed.json` by default. The pipeline always reads the raw catalog and regenerates the processed artifact.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the data pipeline:

```powershell
python scripts/run_card_pipeline.py
```

Expected result:

```text
Card pipeline complete: 25/25 processed, 0 errors, 0 warnings.
```

Run the web application:

```powershell
python app.py
```

Open [http://localhost:8000](http://localhost:8000). Use `localhost` or `127.0.0.1` in the browser; `0.0.0.0` is only the server bind address.

## API

Start the JSON API:

```powershell
python run_api.py
```

Interactive documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

Main endpoints:

- `GET /health`
- `POST /recommendations`

## Evaluation Scenarios

Generate the food-focused, frequent-traveler, and no-annual-fee examples:

```powershell
python scripts/run_evaluation_scenarios.py
```

Outputs:

- `outputs/evaluation/scenario_results.json`
- `outputs/evaluation/scenario_summary.md`

These examples demonstrate that rankings change with spending behavior and fee constraints.

## Tests

```powershell
python -m pytest -q
```

The suite covers the API, catalog provenance, processed-data loading, validation, ETL, scoring, recommendation behavior, and evaluation scenarios.

## Google Cloud Run

The production container uses `requirements-web.txt`, while `requirements.txt` retains the optional local RAG and experimentation dependencies.

Deploy from the repository root:

```powershell
gcloud run deploy cardiq `
  --source . `
  --project project-dda6cdb1-a2ba-470b-a47 `
  --region us-central1 `
  --allow-unauthenticated
```

Cloud Run supplies the `PORT` environment variable. The included Dockerfile starts FastAPI on that port and packages the processed catalog with the application.

## Important Limitations

- Card offers can change after their recorded verification date.
- Point values are estimates and vary by redemption method.
- Annual credits are counted at face value even when a user may not use every credit.
- Reward caps and issuer-portal restrictions are not yet modeled as fully structured rules.
- Recommendations are educational estimates, not financial advice.
