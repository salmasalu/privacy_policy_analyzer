import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from  app.core.llm_engine import explain_risk

print("=" * 55)
print("TEST: llm_engine.py (Groq API)")
print("=" * 55)


TEST_CLAUSE = (
    "We may share your personal data with third-party partners "
    "for advertising purposes without explicit consent."
)


#  Test 1: Returns string 
print("\nTest 1: Return type check...")
result = explain_risk(TEST_CLAUSE)
assert isinstance(result, str), f"Expected string, got {type(result)}"
print("✅ Test 1 passed: returns string")


# Test 2: Output is not empty
print("\nTest 2: Non-empty output...")
assert len(result.strip()) > 10, f"Output too short: {result}"
print("✅ Test 2 passed: output has content")


# Test 3: All 3 stages present
print("\nTest 3: 3-stage chain output structure...")
assert "Practice:" in result, "Missing Stage 1 'Practice:' label"
assert "Risk:" in result, "Missing Stage 2 'Risk:' label"
assert "Action:" in result, "Missing Stage 3 'Action:' label"
print("✅ Test 3 passed: all 3 stages present in output")


# Test 4: Each stage has content 
print("\nTest 4: Stage content check...")
lines = result.strip().split("\n")
for line in lines:
    if line.startswith("Practice:"):
        assert len(line.replace("Practice:", "").strip()) > 3, "Practice stage empty"
    if line.startswith("Risk:"):
        assert len(line.replace("Risk:", "").strip()) > 3, "Risk stage empty"
    if line.startswith("Action:"):
        assert len(line.replace("Action:", "").strip()) > 3, "Action stage empty"
print("✅ Test 4 passed: all stages have content")


# Test 5: Edge case — very short clause
print("\nTest 5: Short clause handling...")
short_result = explain_risk("We track users.")
assert isinstance(short_result, str), "Expected string for short clause"
print("✅ Test 5 passed: short clause handled gracefully")


# Full output preview 
print("\n── Sample Output ──")
print(result)

print("\n" + "=" * 55)
print("ALL GROQ LLM TESTS PASSED")
print("=" * 55)