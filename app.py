"""CardIQ FastAPI Web Application"""
import sys
import os
from pathlib import Path
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import uvicorn

# Add project root to path so existing src/ imports work
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.orchestrator import Orchestrator
from src.models.user_input import UserProfile, MonthlySpending
from src.data.card_loader import CardLoader

app = FastAPI(title="CardIQ")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_available_rewards_types():
    try:
        loader = CardLoader()
        all_cards = loader.load_cards()
        return sorted(set(card['rewards_type'] for card in all_cards))
    except Exception:
        return ["cashback", "travel", "points"]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    rewards_types = get_available_rewards_types()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "rewards_types": rewards_types
    })


@app.post("/recommend", response_class=HTMLResponse)
async def recommend(
    request: Request,
    dining: float = Form(0),
    groceries: float = Form(0),
    travel: float = Form(0),
    gas: float = Form(0),
    streaming: float = Form(0),
    other: float = Form(0),
    flights: float = Form(0),
    hotels: float = Form(0),
    transit: float = Form(0),
    credit_score: str = Form("good"),
    max_annual_fee: Optional[str] = Form(None),
    preferred_rewards_type: Optional[str] = Form(None),
):
    try:
        max_fee = int(max_annual_fee) if max_annual_fee and max_annual_fee.strip() else None
        rewards_pref = preferred_rewards_type if preferred_rewards_type and preferred_rewards_type.strip() else None

        user_profile = UserProfile(
            monthly_spending=MonthlySpending(
                dining=dining,
                groceries=groceries,
                travel=travel,
                gas=gas,
                streaming=streaming,
                other=other,
                flights=flights,
                hotels=hotels,
                transit=transit,
            ),
            credit_score=credit_score,
            max_annual_fee=max_fee,
            preferred_rewards_type=rewards_pref,
        )

        orchestrator = Orchestrator()
        result = orchestrator.process(user_profile, verbose=False)

        total_monthly = dining + groceries + travel + gas + streaming + other

        spending_data = {
            "Dining": dining,
            "Groceries": groceries,
            "Travel": travel,
            "Gas": gas,
            "Streaming": streaming,
            "Other": other,
        }

        return templates.TemplateResponse("results.html", {
            "request": request,
            "recommendations": result.recommendations,
            "portfolio_strategy": result.portfolio_strategy,
            "spending_data": spending_data,
            "total_monthly": total_monthly,
            "credit_score": credit_score,
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)