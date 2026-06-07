from transformers import pipeline
import re
import mlflow
from app.core.llm_engine import explain_risk
from app.core.aggregator import calculate_risk_score, get_risk_label

mlflow.set_experiment("privacy-policy-analyzer")

print("Loading DeBERTa model... please wait")

classifier = pipeline(
    "zero-shot-classification",
    model="cross-encoder/nli-deberta-v3-small"
)

print("Model loaded successfully!")

# LABELS

LABELS = [
    "collecting personal data without clear consent",
    "sharing user data with third parties",
    "selling user data for profit",
    "tracking user location or behavior",
    "storing sensitive information indefinitely",
    "data usage for service improvement",
    "normal safe statement"
]

# RISK KEYWORDS 

RISK_KEYWORDS = [
    # Data sharing
    "sell", "selling", "sold",
    "third party", "third-party", "third parties",
    "share", "sharing", "shared", "disclose", "disclosure",
    "transfer", "transmit", "provide to", "give to",
    "partner", "partners", "affiliate", "affiliates",
    # Advertising
    "advertising", "advertisers", "ads", "ad targeting",
    "marketing", "promotional", "commercial",
    # Tracking
    "track", "tracking", "monitor", "monitoring",
    "profile", "profiling", "fingerprint",
    # Location
    "location", "gps", "geolocation", "whereabouts",
    # Data collection
    "collect", "collecting", "gathered", "obtain",
    "cookies", "cookie", "pixel", "beacon",
    "analytics", "telemetry", "usage data",
    # Storage
    "retain", "retention", "store", "storing", "indefinitely",
    "as long as", "until we decide",
    # Consent
    "without consent", "without your permission",
    "automatically", "by using our service"
]

NEGATIVE_PHRASES = [
    "do not share", "don't share",
    "we do not share", "we don't share",
    "we never share", "do not sell",
    "we don't sell", "we do not sell",
    "we do not track", "we don't track",
    "we do not collect", "we don't collect",
    "opt out", "opt-out", "you can disable",
    "you may disable", "you can turn off"
]

# TEXT PROCESSING

def split_into_chunks(text: str) -> list:
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    for s in sentences:
        s = s.strip()
        if len(s.split()) > 6:  # lowered from 8 to catch more
            chunks.append(s)
    return chunks


def is_potentially_risky(chunk: str) -> bool:
    chunk_lower = chunk.lower()
    return any(keyword in chunk_lower for keyword in RISK_KEYWORDS)


def has_negative_phrase(chunk: str) -> bool:
    chunk_lower = chunk.lower()
    return any(phrase in chunk_lower for phrase in NEGATIVE_PHRASES)

# MAIN ANALYSIS

def analyze_clauses(text: str) -> list:
    """
    Runs DeBERTa zero-shot classification on each sentence chunk.

    Changes from v1:
    - Chunk limit increased from 40 to 60 for better coverage
    - Min word count lowered from 12 to 8 to catch shorter clauses
    - Confidence threshold lowered from 0.65 to 0.60
    - Expanded keyword list catches more policy language patterns
    """
    chunks = split_into_chunks(text)
    risky_clauses = []

    for chunk in chunks[:60]:              # increased from 40
        if len(chunk.split()) < 8:         # lowered from 12
            continue
        if not is_potentially_risky(chunk):
            continue
        if has_negative_phrase(chunk):
            continue

        result = classifier(chunk, LABELS)
        top_label = result["labels"][0]
        top_score = result["scores"][0]

        if top_label != "normal safe statement" and top_score > 0.60:   # lowered from 0.65
            try:
                explanation = explain_risk(chunk)
            except Exception:
                explanation = "Explanation unavailable"

            risky_clauses.append({
                "clause": chunk[:300],
                "risk_type": top_label,
                "confidence": round(top_score * 100, 2),
                "explanation": explanation
            })

    return risky_clauses

# MLflow ENTRY POINT

def get_risk_level(text: str) -> tuple:
    with mlflow.start_run():
        clauses = analyze_clauses(text)
        risk_score, avg_conf, num_clauses = calculate_risk_score(clauses)
        risk_label = get_risk_label(risk_score)

        mlflow.log_param("input_length", len(text))
        mlflow.log_param("risk_label", risk_label)
        mlflow.log_metric("risk_score", risk_score)
        mlflow.log_metric("num_risky_clauses", num_clauses)
        mlflow.log_metric("avg_confidence", avg_conf)

        return risk_label, risk_score