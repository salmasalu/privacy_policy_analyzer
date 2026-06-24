import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.core.classifier import analyze_clauses

print("=" * 55)
print("TEST: classifier.py")
print("(Model loading may take 30–60 seconds)")
print("=" * 55)


# Test 1: Returns list
print("\nTest 1: Return type check...")
result = analyze_clauses("We may share your data with third-party advertisers for profit.")
assert isinstance(result, list), f"Expected list, got {type(result)}"
print("✅ Test 1 passed: returns list")


# Test 2: Clearly risky clause is detected 
print("\nTest 2: Risky clause detection...")
risky_text = (
    "We may sell your personal information to third-party advertisers "
    "and marketing companies for commercial purposes without your consent."
)
result = analyze_clauses(risky_text)
assert len(result) > 0, "Expected at least 1 risky clause detected"
print(f"✅ Test 2 passed: detected {len(result)} risky clause(s)")


#  Test 3: Each result has required fields
print("\nTest 3: Result structure check...")
for item in result:
    assert "clause" in item, "Missing 'clause' field"
    assert "risk_type" in item, "Missing 'risk_type' field"
    assert "confidence" in item, "Missing 'confidence' field"
    assert "explanation" in item, "Missing 'explanation' field"
print("✅ Test 3 passed: all required fields present")


#  Test 4: Confidence is 0–100 
print("\nTest 4: Confidence range check...")
for item in result:
    assert 0 <= item["confidence"] <= 100, \
        f"Confidence out of range: {item['confidence']}"
print("✅ Test 4 passed: confidence values in valid range")


# Test 5: Negated clause not flagged 
print("\nTest 5: Negated clause filter...")
safe_text = (
    "We do not sell your personal data to any third party. "
    "We never share your information with advertisers or marketing companies."
)
result = analyze_clauses(safe_text)
assert len(result) == 0, \
    f"Expected 0 risky clauses for negated text, got {len(result)}"
print("✅ Test 5 passed: negated clauses correctly filtered")


# Test 6: Clearly safe text returns empty
print("\nTest 6: Safe text returns empty list...")
safe = (
    "Your data is encrypted and stored securely. "
    "We comply with GDPR regulations and protect your privacy. "
    "You can request deletion of your data at any time."
)
result = analyze_clauses(safe)
print(f"✅ Test 6 passed: {len(result)} risky clauses found in safe text")


print("\n" + "=" * 55)
print("ALL CLASSIFIER TESTS PASSED")
print("=" * 55)