# CardIQ

CardIQ is a hybrid AI credit card recommendation system built around a curated catalog of 25 U.S. cards. It validates issuer-sourced data, calculates and ranks cards deterministically, retrieves relevant source-linked evidence, and uses Gemini on Vertex AI to generate grounded explanations.

The project intentionally stays focused on 25 cards. Its goal is transparent data quality and explainable results, not catalog size.

## Live Demo

**[Open the CardIQ web application](https://cardiq-331679307975.us-central1.run.app)**

The application is hosted on Google Cloud Run. Enter a spending profile to receive three ranked card recommendations with value calculations, grounded explanations, verification dates, and links to official issuer sources.

## Verified Results

| Metric | Result |
| --- | --- |
| Curated U.S. credit cards | 25 |
| Pipeline processing | 25/25 cards |
| Data-quality errors and warnings | 0 errors, 0 warnings |
| Automated tests | 24 passing |
| RAG retrieval benchmark | 100% Hit@3 across 6 queries |
| Official-source coverage | 100% in the retrieval benchmark |

## What It Demonstrates

- Data ingestion from a versioned raw JSON catalog
- Source provenance and offer verification dates
- Validation with blocking errors and reviewable warnings
- Raw-to-processed ETL with deterministic derived features
- Explainable first-year and multi-year value calculations
- Retrieval-augmented generation with Gemini and validated citations
- Automatic deterministic fallback when Vertex AI is unavailable
- FastAPI web and JSON interfaces
- Reproducible ranking and RAG retrieval evaluations
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
                                            |
                                            v
                              evidence retrieval from catalog
                                            |
                                            v
                              Gemini grounded explanations
                                            |
                         +------------------+------------------+
                         v                                     v
                 FastAPI JSON API                     Web comparison UI
```

Gemini never calculates or ranks cards. The deterministic engine remains the source of truth for financial values; the RAG layer only explains those results using retrieved catalog evidence. Citation IDs are validated before AI text is shown, and any Vertex AI failure returns the deterministic explanation instead.

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

AI explanations are disabled locally by default. To use Vertex AI with Application Default Credentials:

```powershell
$env:AI_EXPLANATIONS_ENABLED="true"
$env:GCP_PROJECT_ID="cardiq-anish-2026"
$env:GCP_LOCATION="global"
$env:GEMINI_MODEL="gemini-2.5-flash"
python app.py
```

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

Run the fixed RAG retrieval benchmark:

```powershell
python scripts/run_rag_evaluation.py
```

The benchmark currently contains 6 feature and card queries and reports Hit@3 plus official-source coverage in `outputs/evaluation/rag_retrieval_report.json`.

## Tests

```powershell
python -m pytest -q
```

The suite covers the API, catalog provenance, processed-data loading, validation, ETL, scoring, retrieval, citation validation, AI fallback behavior, and evaluation scenarios.

## Google Cloud Run

The production container uses `requirements-web.txt` with the Google Gen AI SDK. The full `requirements.txt` also retains optional legacy FAISS experimentation dependencies.

Deploy from the repository root:

```powershell
gcloud run deploy cardiq `
  --source . `
  --project cardiq-anish-2026 `
  --region us-central1 `
  --allow-unauthenticated `
  --service-account cardiq-runtime@cardiq-anish-2026.iam.gserviceaccount.com `
  --set-env-vars AI_EXPLANATIONS_ENABLED=true,GCP_PROJECT_ID=cardiq-anish-2026,GCP_LOCATION=global,GEMINI_MODEL=gemini-2.5-flash
```

Cloud Run supplies the `PORT` environment variable. The included Dockerfile starts FastAPI on that port and packages the processed catalog with the application.

## Important Limitations

- Card offers can change after their recorded verification date.
- Point values are estimates and vary by redemption method.
- Annual credits are counted at face value even when a user may not use every credit.
- Reward caps and issuer-portal restrictions are not yet modeled as fully structured rules.
- Recommendations are educational estimates, not financial advice.
- AI text is grounded in the fixed catalog and can only be as current as its verification date.
