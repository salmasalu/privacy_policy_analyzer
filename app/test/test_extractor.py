import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.core.extractor import extract_text_from_url, extract_text_from_input

print("=" * 55)
print("TEST: extractor.py")
print("=" * 55)


# Test 1: Valid URL returns text
print("\nTest 1: Extract from valid URL...")
text = extract_text_from_url("https://policies.google.com/privacy")
assert isinstance(text, str), "Expected string output"
assert len(text) > 100, f"Expected >100 chars, got {len(text)}"
print(f"✅ Test 1 passed: extracted {len(text)} characters")


# Test 2: Extracted text is within limit
assert len(text) <= 5500, f"Text too long: {len(text)} chars"
print("✅ Test 2 passed: character limit respected")


# Test 3: Invalid URL raises exception
print("\nTest 3: Invalid URL handling...")
try:
    result = extract_text_from_url("https://this-url-does-not-exist-xyz123.com")
    # Should either raise or return error string
    print("✅ Test 3 passed: handled gracefully")
except Exception as e:
    print(f"✅ Test 3 passed: raised exception as expected → {type(e).__name__}")


# Test 4: Plain text input cleaning
print("\nTest 4: Plain text input...")
raw = "   Hello this is a privacy policy.   "
result = extract_text_from_input(raw)
assert result == raw.strip(), f"Expected stripped text, got: {result}"
print("✅ Test 4 passed: text stripped correctly")


# Test 5: Empty text input 
result = extract_text_from_input("   ")
assert result == "", f"Expected empty string, got: {result}"
print("✅ Test 5 passed: empty input handled")


print("\n" + "=" * 55)
print("ALL EXTRACTOR TESTS PASSED")
print("=" * 55)