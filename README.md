# Groww RAG Chatbot — Mutual Fund FAQ Assistant

A RAG-powered FAQ assistant that answers **factual** questions about HDFC mutual fund schemes using only official Groww pages as sources. Every answer cites one source link. It does **not** give investment advice.

## Scope

| Field | Detail |
|---|---|
| AMC | HDFC Mutual Fund |
| Schemes | Large Cap, Flexi Cap (Equity), ELSS Tax Saver, Small Cap, Balanced Advantage |
| Corpus | 5 official Groww pages listed below |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` (Hugging Face) |
| Vector DB | ChromaDB (persistent, `data/chroma`) |
| LLM | Groq API (`qwen/qwen3.8-27b`) |

## Source list

| # | Scheme | URL |
|---|---|---|
| 1 | HDFC Large Cap Fund | https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |
| 2 | HDFC Equity (Flexi Cap) Fund | https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth |
| 3 | HDFC ELSS Tax Saver Fund | https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth |
| 4 | HDFC Small Cap Fund | https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth |
| 5 | HDFC Balanced Advantage Fund | https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth |

A machine-readable copy is also provided in `sources.csv`.

## Setup

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env from the example and add your Groq key
copy .env.example .env
# edit .env: set GROQ_API_KEY=gsk_... and GROQ_MODEL=qwen/qwen3.8-27b

# 3. Build the knowledge base (fetch/ingest the 5 pages)
$env:PYTHONPATH="."; py -3.11 tests\fetch_scheme_pages.py
$env:PYTHONPATH="."; py -3.11 tests\ingest_docs.py

# 4. Start the API
$env:PYTHONPATH="."; py -3.11 -m uvicorn app.main:app --reload

# 5. (optional) Start the Streamlit UI in another terminal
$env:PYTHONPATH="."; py -3.11 -m streamlit run app/ui/streamlit_app.py
```

API docs: http://localhost:8000/docs
UI: http://localhost:8501

## Deployment on Render

Two web services (both from the same GitHub repo):

**API service**
| Field | Value |
|---|---|
| Runtime | Python 3 |
| Root Directory | *(blank)* |
| Build Command | `pip install -r requirements.txt && PYTHONPATH=. python tests/ingest_docs.py` |
| Start Command | `PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Env vars | `PYTHON_VERSION=3.11.0`, `PYTHONPATH=.`, `GROQ_API_KEY`, `GROQ_MODEL=qwen/qwen3.8-27b`, plus chunking/retrieval/storage vars (see `.env.example`) |

**UI service** (Streamlit)
| Field | Value |
|---|---|
| Runtime | Python 3 |
| Root Directory | *(blank)* |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `PYTHONPATH=. streamlit run app/ui/streamlit_app.py --server.port $PORT --server.address 0.0.0.0` |
| Env vars | `PYTHON_VERSION=3.11.0`, `PYTHONPATH=.`, `API_URL=https://<your-api-service>.onrender.com` |

> The UI service only needs `API_URL` — LLM calls happen in the API service, so the Groq key stays only there.

## Project structure

```
app/
  api/          FastAPI routes + schemas
  pipeline/     ingestion, query pipeline, components (extractor, chunker, embedder, retriever, prompt_builder, llm_client)
  storage/      SQLite document store + ChromaDB vector store
  models/       Pydantic schemas
  ui/           Streamlit app
data/           chroma index + documents.db (gitignored, rebuilt at setup)
documents/      the 5 fund pages + reference/ specs
tests/          scripts: fetch_scheme_pages.py, ingest_docs.py, test_chat.py, test_retrieval.py, test_ingestion.py, test_query.py, test_api.py
```

## Sample Q&A

| # | Question | Assistant answer | Source |
|---|---|---|---|
| 1 | What is the expense ratio of HDFC Large Cap Fund? | 1.04% | https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |
| 2 | What is the ELSS lock-in period? | 3 years | https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth |
| 3 | What is the exit load of HDFC Small Cap Fund? | 1% if redeemed within 1 year | https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth |
| 4 | What is the minimum SIP for HDFC Balanced Advantage Fund? | ₹100 | https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth |
| 5 | What is the benchmark of HDFC Equity Fund? | NIFTY 500 Total Return Index | https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth |
| 6 | Who manages HDFC Large Cap Fund? | Rahul Baijal and Dhruv Muchhal | https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |
| 7 | Who manages HDFC Flexi Cap Direct Plan? | Dhruv Muchhal and Amit Ganatra | https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth |
| 8 | Should I buy HDFC Large Cap Fund? | (Refused — facts-only assistant) | https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |

## Disclaimer snippet (used in UI/docs)

> **Facts-only. No investment advice.** Answers are derived solely from the official Groww scheme pages listed above and include one source link. Last updated from sources: October 2026.

## Known limits

- Facts are only as current as the last fetch of the 5 Groww pages; re-run `tests\fetch_scheme_pages.py` + `tests\ingest_docs.py` to refresh.
- The assistant refuses opinionated questions ("should I buy/sell?", portfolio allocation) by design.
- Chunking/retrieval is best for direct fact lookups; long comparison questions across schemes may need follow-ups.
- No PII is collected or stored — the chat history is kept in memory only.
- The free Groq tier may rate-limit heavy usage; responses can also fall back to "I'm having trouble generating a response right now."
