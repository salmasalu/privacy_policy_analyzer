import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from app.core.aggregator import calculate_risk_score, get_risk_label


def test_high_risk_policy():
    clauses = [{
        "clause": "We sell your personal data",
        "risk_type": "selling user data for profit",
        "confidence": 95.0
    }]

    score, _, _ = calculate_risk_score(clauses)

    assert score > 5


def test_empty_input():
    score, avg_conf, num = calculate_risk_score([])

    assert score == 0.0
    assert avg_conf == 0.0
    assert num == 0


def test_risk_labels():
    assert get_risk_label(1.0) == "LOW RISK"
    assert get_risk_label(5.0) == "MEDIUM RISK"
    assert get_risk_label(8.0) == "HIGH RISK"