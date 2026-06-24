# Privacy Policy Risk Analyzer

Most people never read privacy policies. They're long, full of legal jargon, and often hide important details about how personal data is collected, shared, and stored. This project simplifies privacy policies by automatically identifying risky clauses, explaining them in plain English, and assigning a risk score.

Users can analyze a privacy policy from a URL, uploaded PDF, or pasted text and receive an AI-generated breakdown of potential privacy concerns.

---

## Features

### Privacy Risk Detection

* Extracts privacy policy text from URLs, PDFs, or pasted content
* Detects potentially risky clauses using a DeBERTa-based classifier
* Categorizes risks across multiple privacy-related categories
* Calculates an overall privacy risk score

### AI-Powered Explanations

For every flagged clause, a multi-stage LLM pipeline:

1. Identifies the underlying data practice
2. Explains why it may be risky
3. Suggests practical actions users can take

### Data Persistence & Analytics

* Stores analysis results in PostgreSQL
* Returns cached results for previously analyzed URLs
* Maintains analysis history
* Tracks usage statistics and system performance

### Monitoring & Experiment Tracking

* MLflow integration for model evaluation
* Tracks Precision, Recall, and F1 Score
* Monitors model performance over time

### Automated Testing & CI/CD

* Unit tests implemented using PyTest
* GitHub Actions pipeline automatically runs tests on every push and pull request
* Continuous Integration ensures code quality and reliability

---

## Tech Stack

### Machine Learning & AI

* DeBERTa-v3-small
* Hugging Face Transformers
* Groq (LLaMA 3.1 8B)
* LangChain

### Backend

* FastAPI
* SQLAlchemy
* PostgreSQL

### Frontend

* Streamlit

### MLOps & DevOps

* MLflow
* Docker
* Docker Compose
* GitHub Actions
* PyTest

---

## System Architecture

1. User submits a URL, PDF, or text.
2. Text extraction and preprocessing.
3. DeBERTa classifier identifies risky clauses.
4. LLM reasoning pipeline generates explanations.
5. Risk score is calculated.
6. Results are stored in PostgreSQL.
7. Analysis is displayed through Streamlit.
8. Metrics are tracked using MLflow.

---

## Running Locally

### Option 1: Docker

```bash
git clone https://github.com/salmasalu/privacy_policy_analyzer.git
cd privacy_policy_analyzer

cp .env.example .env

# Add your GROQ_API_KEY inside .env

docker-compose up
```

Services:

* Streamlit UI: http://localhost:8501
* FastAPI Docs: http://localhost:8000/docs
* MLflow Dashboard: http://localhost:5000

---

### Option 2: Local Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn main:app --reload
```

Start Streamlit:

```bash
streamlit run streamlit_app.py
```

---

## API Endpoints

| Method | Endpoint      | Description                       |
| ------ | ------------- | --------------------------------- |
| POST   | /analyze-url  | Analyze a privacy policy from URL |
| POST   | /analyze-text | Analyze pasted text               |
| POST   | /analyze-pdf  | Analyze uploaded PDF              |
| GET    | /history      | Retrieve analysis history         |
| GET    | /analytics    | Retrieve usage statistics         |

---

## Testing

Run unit tests:

```bash
pytest tests/test_pipeline.py -v
```

Example output:

```bash
================ test session starts ================
collected 3 items

test_high_risk_policy PASSED
test_empty_input PASSED
test_risk_labels PASSED

================ 3 passed ===========================
```

---

## CI/CD Pipeline

GitHub Actions automatically:

* Installs dependencies
* Executes PyTest test suite
* Validates code before integration
* Runs on every push and pull request

Workflow file:

```text
.github/workflows/ci.yml
```

---

## Project Highlights

* End-to-end AI application
* FastAPI REST APIs
* PostgreSQL data persistence
* Transformer-based risk classification
* LLM-powered reasoning pipeline
* MLflow experiment tracking
* Dockerized deployment
* Automated testing with PyTest
* Continuous Integration using GitHub Actions

---

## Author

**Ummusalma P T**

