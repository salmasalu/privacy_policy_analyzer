"""
mlops/train.py — Model evaluation and MLflow experiment tracking

Evaluation scope: DeBERTa zero-shot classification stage only.
LLM reasoning stage (explain_risk) produces free-text explanations
evaluated qualitatively. Full pipeline evaluation with LLM-as-judge
scoring is a planned improvement.

Usage:
    python -m app.mlops.train

Design decision:
    Zero-shot classification means we don't retrain DeBERTa weights.
    Instead, we evaluate label accuracy on a curated test set,
    track F1/precision/recall per risk category, and version the
    experiment so model behaviour changes are reproducible.
"""

import mlflow
import time
from sklearn.metrics import (
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    accuracy_score
)
from transformers import pipeline

# LABELLED TEST SET
# 30 clauses with ground truth labels
# Source: manually curated from real privacy policies
# Dataset size: 30 samples, balanced across 7 categories

TEST_DATA = [
    # Selling data
    ("We may sell your personal information to third-party advertisers.", "selling user data for profit"),
    ("Your data may be sold to marketing partners for commercial use.", "selling user data for profit"),
    ("We monetize user data by selling it to data brokers.", "selling user data for profit"),
    ("Personal information may be transferred as part of a business sale.", "selling user data for profit"),

    # Sharing with third parties
    ("We share your data with trusted third-party service providers.", "sharing user data with third parties"),
    ("Your information may be disclosed to our business partners.", "sharing user data with third parties"),
    ("We provide your data to affiliated companies within our group.", "sharing user data with third parties"),
    ("User data is shared with analytics and advertising companies.", "sharing user data with third parties"),

    # Tracking
    ("We track your location continuously to improve recommendations.", "tracking user location or behavior"),
    ("We monitor your browsing behavior across websites using cookies.", "tracking user location or behavior"),
    ("Your GPS location is recorded when the app is running.", "tracking user location or behavior"),
    ("We use tracking pixels to monitor email open rates.", "tracking user location or behavior"),

    # No consent
    ("We collect your email address and phone number automatically.", "collecting personal data without clear consent"),
    ("Personal details are gathered from your device without prompting.", "collecting personal data without clear consent"),
    ("We collect biometric data during app usage.", "collecting personal data without clear consent"),

    # Indefinite storage
    ("We retain your data for as long as necessary for business purposes.", "storing sensitive information indefinitely"),
    ("Your information is kept indefinitely even after account deletion.", "storing sensitive information indefinitely"),
    ("We store all user data without a defined retention period.", "storing sensitive information indefinitely"),

    # Service improvement (low risk)
    ("We use anonymized data to improve our services.", "data usage for service improvement"),
    ("Aggregated statistics help us enhance app performance.", "data usage for service improvement"),
    ("We analyze usage patterns to fix bugs and improve features.", "data usage for service improvement"),

    # Safe statements
    ("We do not sell your personal data to any third party.", "normal safe statement"),
    ("Your data is encrypted and never shared without consent.", "normal safe statement"),
    ("We do not track your location or behavior.", "normal safe statement"),
    ("You can request deletion of your data at any time.", "normal safe statement"),
    ("We only collect information you explicitly provide.", "normal safe statement"),
    ("Data is stored for 30 days and then permanently deleted.", "normal safe statement"),
    ("We never share your information with advertisers.", "normal safe statement"),
    ("Your personal data stays on your device and is not transmitted.", "normal safe statement"),
    ("We comply with GDPR and do not process sensitive data.", "normal safe statement"),
]

LABELS = [
    "collecting personal data without clear consent",
    "sharing user data with third parties",
    "selling user data for profit",
    "tracking user location or behavior",
    "storing sensitive information indefinitely",
    "data usage for service improvement",
    "normal safe statement"
]

# Evaluation

def run_evaluation():
    print("Loading DeBERTa model...")
    clf = pipeline(
        "zero-shot-classification",
        model="cross-encoder/nli-deberta-v3-small"
    )
    print("Model loaded.\n")

    y_true = []
    y_pred = []
    latencies = []

    for clause, true_label in TEST_DATA:
        start = time.time()
        result = clf(clause, LABELS)
        latency = round((time.time() - start) * 1000, 2)

        pred_label = result["labels"][0]
        y_true.append(true_label)
        y_pred.append(pred_label)
        latencies.append(latency)

        status = "✅" if pred_label == true_label else "❌"
        print(f"{status} TRUE: {true_label}")
        print(f"   PRED: {pred_label}")
        print(f"   LATENCY: {latency} ms\n")

    return y_true, y_pred, latencies


# MLflow LOGGING

def log_experiment(y_true, y_pred, latencies):
    mlflow.set_experiment("privacy-policy-analyzer")

    with mlflow.start_run(run_name="deberta-v3-small-evaluation"):

        # ── Parameters ──
        mlflow.log_param("model", "cross-encoder/nli-deberta-v3-small")
        mlflow.log_param("task", "zero-shot-risk-classification")
        mlflow.log_param("dataset_size", len(TEST_DATA))
        mlflow.log_param("dataset_source", "manually curated real privacy policies")
        mlflow.log_param("num_labels", len(LABELS))
        mlflow.log_param("confidence_threshold", 0.65)
        mlflow.log_param("max_chunks_per_doc", 40)
        mlflow.log_param("evaluation_scope", "classification_stage_only")
        mlflow.log_param(
            "llm_evaluation_note",
            "LLM reasoning stage evaluated qualitatively. "
            "LLM-as-judge scoring planned as future improvement."
        )

        # ── Real metrics ──
        acc = accuracy_score(y_true, y_pred)
        f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
        f1_weighted = f1_score(y_true, y_pred, average="weighted", zero_division=0)
        precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
        avg_latency = round(sum(latencies) / len(latencies), 2)
        max_latency = round(max(latencies), 2)

        mlflow.log_metric("accuracy", round(acc, 4))
        mlflow.log_metric("f1_macro", round(f1_macro, 4))
        mlflow.log_metric("f1_weighted", round(f1_weighted, 4))
        mlflow.log_metric("precision_weighted", round(precision, 4))
        mlflow.log_metric("recall_weighted", round(recall, 4))
        mlflow.log_metric("avg_latency_ms", avg_latency)
        mlflow.log_metric("max_latency_ms", max_latency)

        # ── Per-class report as artifact ──
        report = classification_report(
            y_true, y_pred,
            labels=LABELS,
            zero_division=0
        )

        print("\n── Classification Report ──")
        print(report)

        with open("classification_report.txt", "w") as f:
            f.write("Evaluation scope: DeBERTa classification stage only.\n")
            f.write("LLM reasoning stage evaluated qualitatively.\n\n")
            f.write(report)

        mlflow.log_artifact("classification_report.txt")

        # ── Summary ──
        print("── MLflow Run Complete ──")
        print(f"Accuracy:          {acc:.4f}")
        print(f"F1 (macro):        {f1_macro:.4f}")
        print(f"F1 (weighted):     {f1_weighted:.4f}")
        print(f"Precision:         {precision:.4f}")
        print(f"Recall:            {recall:.4f}")
        print(f"Avg latency:       {avg_latency} ms")
        print(f"Max latency:       {max_latency} ms")
        print(f"Dataset size:      {len(TEST_DATA)} samples")

# ENTRY POINT

if __name__ == "__main__":
    y_true, y_pred, latencies = run_evaluation()
    log_experiment(y_true, y_pred, latencies)