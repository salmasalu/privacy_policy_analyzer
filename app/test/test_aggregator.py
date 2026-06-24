import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from  app.core.aggregator import calculate_risk_score, get_risk_label, summarize_clauses

print("=" * 55)
print("TEST: aggregator.py")
print("=" * 55)


# Test 1: Empty input 
score, avg_conf, num = calculate_risk_score([])
assert score == 0.0, f"Expected 0.0, got {score}"
assert avg_conf == 0.0, f"Expected 0.0, got {avg_conf}"
assert num == 0, f"Expected 0, got {num}"
print("✅ Test 1 passed: empty input returns (0.0, 0.0, 0)")


# Test 2: Single high risk clause
high_risk_clauses = [{
    "clause": "We sell your personal data to advertisers.",
    "risk_type": "selling user data for profit",
    "confidence": 95.0
}]
score, avg_conf, num = calculate_risk_score(high_risk_clauses)
assert score > 5.0, f"Expected score > 5.0 for selling data, got {score}"
assert num == 1
print(f"✅ Test 2 passed: high risk clause scored {score}/10")


# Test 3: Single low risk clause
low_risk_clauses = [{
    "clause": "We use anonymized data to improve our services.",
    "risk_type": "data usage for service improvement",
    "confidence": 75.0
}]
score, avg_conf, num = calculate_risk_score(low_risk_clauses)
assert score < 5.0, f"Expected score < 5.0 for service improvement, got {score}"
print(f"✅ Test 3 passed: low risk clause scored {score}/10")


# Test 4: Score never exceeds 10
many_clauses = [{
    "clause": "We sell your data.",
    "risk_type": "selling user data for profit",
    "confidence": 99.0
}] * 20
score, _, _ = calculate_risk_score(many_clauses)
assert score <= 10.0, f"Score exceeded 10: {score}"
print(f"✅ Test 4 passed: score capped at {score}/10")


# Test 5: Risk labels
assert get_risk_label(1.0) == "LOW RISK"
assert get_risk_label(5.0) == "MEDIUM RISK"
assert get_risk_label(8.0) == "HIGH RISK"
print("✅ Test 5 passed: risk labels correct for all ranges")


# Test 6: Summary with no clauses
summary = summarize_clauses([])
assert "safe" in summary.lower() or "no" in summary.lower(), \
    f"Expected safe message, got: {summary}"
print("✅ Test 6 passed: empty summary is safe message")


# Test 7: Summary with clauses
summary = summarize_clauses(high_risk_clauses)
assert "selling user data for profit".upper() in summary, \
    "Expected risk type in summary"
print("✅ Test 7 passed: summary contains risk type")


print("\n" + "=" * 55)
print("ALL AGGREGATOR TESTS PASSED")
print("=" * 55)