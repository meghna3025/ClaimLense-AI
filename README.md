# ClaimSense AI

An intelligent automobile insurance claim processing system powered by Google Gemini and LangGraph.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    FastAPI Layer                     │
│              POST /api/v1/claims/process             │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│               LangGraph Orchestrator                 │
│  Vision → Assessment → Policy → Repair → Fraud → Decision │
└─────────────────────────────────────────────────────┘
        │           │            │            │
   Gemini Vision  ChromaDB   Repair DB   Fraud Rules
```

## Agents

| Agent | Role |
|-------|------|
| Vision Agent | Detects damaged parts via Gemini Vision |
| Damage Assessment Agent | Converts observations to insurance terminology |
| Policy Agent | RAG over insurance PDFs to check coverage |
| Repair Estimation Agent | Estimates parts + labour costs |
| Fraud Risk Agent | Flags inconsistencies, scores fraud risk |
| Decision Agent | Final APPROVE / REJECT / HUMAN REVIEW |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
cp .env.example .env
# Add your GEMINI_API_KEY

# 3. Generate synthetic datasets
python scripts/generate_datasets.py

# 4. Build the RAG knowledge base
python scripts/build_rag.py

# 5. Run the API server
uvicorn app.main:app --reload --port 8000
```

## API Usage

```bash
curl -X POST http://localhost:8000/api/v1/claims/process \
  -F "image=@accident.jpg" \
  -F "description=Front collision at low speed" \
  -F "policy_number=POL-STANDARD-001" \
  -F "vehicle_model=Toyota Corolla"
```

## Project Structure

```
claimsense_ai/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── api/routes.py            # API routes
│   ├── agents/                  # All 6 agents
│   ├── graph/orchestrator.py    # LangGraph pipeline
│   ├── models/schemas.py        # Pydantic models
│   └── core/config.py           # Configuration
├── rag/
│   ├── policies/                # Insurance PDFs / markdown
│   ├── repair_catalog/          # Repair cost data
│   ├── fraud_rules/             # Fraud detection rules
│   └── claims_history/          # Historical claims
├── scripts/
│   ├── generate_datasets.py     # Synthetic data generator
│   └── build_rag.py             # RAG indexing script
├── data/
│   ├── repair_costs.json
│   ├── historical_claims.json
│   └── policies/
├── tests/
└── requirements.txt
```
