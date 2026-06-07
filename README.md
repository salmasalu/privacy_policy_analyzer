# Privacy Policy Risk Analyzer

Most people never read privacy policies. They're long, full of legal jargon, and designed to be ignored. This tool changes that — paste a URL or upload a PDF and get a plain-English breakdown of what an app actually does with your data.


## What it does

Give it a privacy policy as a URL, PDF, or pasted text. It runs the text through a DeBERTa classifier to find risky clauses, then passes each one through a 3-step LLM chain that identifies the data practice, explains the risk, and suggests what you can actually do about it.

Every analysis gets saved to PostgreSQL — so the same URL returns instantly from cache on repeat visits. There's a history tab to browse past analyses and a monitoring tab showing usage stats and average latency.


## Stack

- **DeBERTa-v3-small** — zero-shot classification across 7 risk categories
- **Groq (LLaMA 3.1 8B)** — 3-stage reasoning chain per flagged clause
- **FastAPI** — 5 REST endpoints with auto docs at `/docs`
- **PostgreSQL + SQLAlchemy** — analysis history, prediction logs, error tracking
- **MLflow** — experiment tracking with F1, precision, recall metrics
- **Streamlit** — 3-tab frontend (Analyzer, History, Monitoring)
- **Docker + docker-compose** — single command to run everything

## Running locally

**With Docker:**

```bash
git clone https://github.com/salmasalu/privacy_policy_analyzer.git
cd privacy_policy_analyzer
cp .env.example .env
# add your GROQ_API_KEY to .env
docker-compose up
```

- App → http://localhost:8501
- API docs → http://localhost:8000/docs
- MLflow → http://localhost:5000

**Without Docker:**

```bash
pip install -r requirements.txt
# terminal 1
uvicorn main:app --reload
# terminal 2
streamlit run streamlit_app.py
```

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze-url` | analyze a policy from URL |
| POST | `/analyze-text` | analyze pasted text |
| POST | `/analyze-pdf` | analyze an uploaded PDF |
| GET | `/history` | retrieve past analyses |
| GET | `/analytics` | usage stats and metrics |


Built by Ummusalma P T