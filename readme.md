# CardIQ: AI-Powered Credit Card Recommendation System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**CardIQ** is a multi-agent system that provides personalized credit card recommendations using Retrieval-Augmented Generation (RAG) and large language models (LLMs).

## 🎯 Project Overview

CardIQ analyzes your monthly spending habits and recommends the best credit cards for YOUR specific situation, complete with:
- ✅ Exact dollar value projections (Year 1, 2, 3)
- ✅ Personalized optimization strategies
- ✅ Smart warnings about fees and restrictions
- ✅ Multi-card portfolio recommendations

### Key Features

- **Multi-Agent Architecture**: 4 specialized agents (Spending Analyzer, Card Evaluator, Recommendation Synthesizer, Orchestrator)
- **RAG Integration**: FAISS vector database with semantic search
- **Hybrid Model Strategy**: Claude Haiku for calculations, Sonnet for explanations (31% cost savings)
- **Interactive CLI**: User-friendly command-line interface
- **25 Credit Cards**: Curated database covering major categories

---

## 🏗️ System Architecture
```
User Input → Agent 1 (Analyze Spending) → Agent 2 (Calculate Values) → 
Agent 3 (Generate Recommendations) → Formatted Output

                    ↓
            RAG Database (FAISS)
            25 Credit Cards
```

### Agents

1. **Spending Analyzer** (Haiku): Analyzes spending patterns, identifies top categories
2. **Card Evaluator** (Haiku): Calculates rewards, fees, and net value for all 25 cards
3. **Recommendation Synthesizer** (Sonnet): Generates personalized explanations with RAG
4. **Orchestrator** (Haiku): Coordinates workflow and formats output

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/cardiq.git
cd cardiq
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

5. **Build vector database** (one-time setup)
```bash
python scripts/build_vector_db.py
```

6. **Run the system!**
```bash
python interactive_main.py
```

### Run As API Service

Start the HTTP API:

```bash
python run_api.py
```

API endpoints:

- `GET /health`
- `POST /recommendations`

Interactive API docs:

- `http://localhost:8000/docs`

Example request:

```bash
curl -X POST "http://localhost:8000/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_spending": {
      "dining": 1200,
      "groceries": 300,
      "travel": 400,
      "gas": 150,
      "streaming": 50,
      "other": 300,
      "flights": 100,
      "hotels": 100,
      "transit": 50
    },
    "credit_score": "excellent",
    "max_annual_fee": 500,
    "preferred_rewards_type": null,
    "planning_to_travel": false,
    "include_formatted_text": true
  }'
```

---

## 🧪 Run Tests

Run the API test suite:

```bash
pytest -q
```

---

## 🐳 Run With Docker

Build and start CardIQ API:

```bash
docker compose up --build
```

Then open:

- `http://localhost:8000/health`
- `http://localhost:8000/docs`

Stop containers:

```bash
docker compose down
```

---

## 📊 Example Usage
```bash
$ python interactive_main.py

Welcome to CardIQ!
============================================================

Monthly spending on DINING: 1200
Monthly spending on GROCERIES: 300
Monthly spending on TRAVEL: 400
...

🎯 YOUR PERSONALIZED CREDIT CARD RECOMMENDATIONS
============================================================

🥇 RANK #1: American Express Gold
WHY THIS CARD:
With your $1,200 monthly dining spend, the Amex Gold's 4x points 
earn you $720/year in rewards...

FINANCIAL SUMMARY:
  • Year 1 Value: $2,294.00
  • Year 2 Value: $3,338.00
  • Annual Fee: $325.00

HOW TO MAXIMIZE:
  ✓ Use this card exclusively for all grocery shopping to earn 3% cash back on your largest spending category
  ✓ Fill up with gas using this card to maximize the 3% rate on your second-highest expense
  ✓ Take advantage of the $7 monthly Disney+ credit if you subscribe to any Disney streaming services
  ✓ Consider the $15 monthly Home Chef credit if you're interested in meal kits - could save $180/year
  ✓ Use the 3% 'other' category rate for miscellaneous purchases that don't fit other bonus categories

WATCH OUT FOR:
  ⚠  American Express isn't accepted everywhere - some smaller grocery stores and gas stations may not take it
  ⚠  No foreign transaction fee information provided - verify before international purchases
  ⚠  The 3% 'other' category may have spending caps or restrictions not clearly specified
  
```

---

## 📁 Project Structure
```
cardiq/
├── data/
│   ├── raw/
│   │   └── credit_cards_llm_special_features_filled.json  # 25 credit cards
│   └── vector_db/                    # FAISS index (generated)
├── src/
│   ├── agents/                       # 4 agent implementations
│   │   ├── orchestrator.py
│   │   ├── spending_analyzer.py
│   │   ├── card_evaluator.py
│   │   └── recommendation_synthesizer.py
│   ├── api/
│   │   └── claude_client.py          # Anthropic API wrapper
│   ├── config/
│   │   └── settings.py               # Configuration
│   ├── data/
│   │   ├── card_loader.py            # Load card data
│   │   └── text_chunker.py           # Create embeddings
│   ├── models/                       # Pydantic data models
│   ├── prompts/                      # LLM prompts
│   ├── rag/                          # RAG pipeline
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── retriever.py
│   └── utils/
│       └── calculations.py           # Financial calculations
├── scripts/
│   └── build_vector_db.py            # Setup script
├── notebooks/
│   └── 02_test_rag_retrieval.ipynb   # RAG testing
├── interactive_main.py               # Main entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🧪 Testing

### Test RAG Retrieval
```bash
python test_rag_simple.py
```

### Test Different Profiles
Edit `interactive_main.py` and modify spending amounts, or use the interactive CLI.

---

## 💰 Cost Estimation

- **Per recommendation**: ~$0.04
- **With $50 API credit**: ~1,250 recommendations
- **Cost breakdown**:
  - Agent 1 (Haiku): $0.002
  - Agent 2 (Haiku): $0.006
  - Agent 3 (Sonnet): $0.0315
  - Orchestrator (Haiku): $0.0008

**Savings**: 31% cheaper than all-Sonnet approach while maintaining quality.

---

## 🎓 Academic Context

This project was developed as part of the **Introduction to LLMs** course at Indiana University (Fall 2024).

### Key Learning Objectives Demonstrated

- Multi-agent system design
- Retrieval-Augmented Generation (RAG)
- Prompt engineering
- Cost optimization strategies
- Pydantic data validation
- Vector databases (FAISS)

### Evaluation Results

- **Top-1 Accuracy**: 90% (9/10 correct recommendations)
- **Financial Calculation Accuracy**: 100% (deterministic math)
- **Compared to Baselines**:
  - Random selection: 4%
  - Rule-based: 60%
  - Single-agent LLM: 70%
  - Multi-agent (ours): 90%

---

## 🔧 Technical Details

### Models Used

- **Claude 3.5 Haiku**: Fast, cost-efficient for calculations
- **Claude Sonnet 4**: High-quality for explanations
- **sentence-transformers/all-MiniLM-L6-v2**: Local embeddings (free)

### RAG Pipeline

1. Text chunking: 150-250 tokens per card
2. Embedding: 384-dimensional vectors
3. Storage: FAISS IndexFlatL2
4. Retrieval: Top-k semantic search (k=3)

---

## 🚧 Limitations

- Dataset: 25 cards (manually curated)
- No real-time offers or approval modeling
- Point valuations are estimated
- Requires Anthropic API access

---

## 🔮 Future Work

- [ ] Expand to 100+ cards
- [ ] Real-time scraping of card offers
- [ ] Approval likelihood modeling
- [ ] Web UI (Streamlit/Gradio)
- [ ] User feedback loop
- [ ] Multi-year portfolio optimization
- [ ] Integration with transaction data (Plaid API)

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Anish Wadkar** 
- **Atharva Parab** 
- **Anish Nair** 
---




**Built with ❤️ at Indiana University**
```
