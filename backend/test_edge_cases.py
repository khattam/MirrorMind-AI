#!/usr/bin/env python3
"""
Edge case testing for debate deduplication.
Tests specific scenarios to validate duplicate detection logic.
"""

from services.debate_deduplication_service import DebateDeduplicationService
from services.embedding_service import EmbeddingService
from groq import Groq
import os
from dotenv import load_dotenv
import tempfile
import json
from pathlib import Path

# Load environment
load_dotenv()

# Create temp file for testing
temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
temp_path = temp_file.name
json.dump([], temp_file)
temp_file.close()

# Initialize service with Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None
service = DebateDeduplicationService(templates_path=temp_path, groq_client=groq_client)

print("=" * 80)
print("EDGE CASE TESTING - SEMANTIC DEDUPLICATION")
print("=" * 80)

# Base debate for comparison
base_debate = {
    'title': 'The Trolley Problem',
    'context': 'A runaway trolley is headed toward five workers on the track. You can pull a lever to divert it to a side track where one worker stands.',
    'option_a': 'Pull the lever to save five people but kill one person',
    'option_b': 'Do nothing and let the trolley kill five people'
}

# TEST 1: Same options, slightly different context -> SHOULD ADD (UNIQUE)
print("\n[TEST 1] Same options, slightly different context")
print("Expected: UNIQUE (should add)")
test1 = {
    'title': 'The Trolley Problem',
    'context': 'A runaway trolley is headed toward five workers. You can pull a lever to divert it to a side track with one worker.',  # Slightly different
    'option_a': 'Pull the lever to save five people but kill one person',
    'option_b': 'Do nothing and let the trolley kill five people'
}
result1 = service.submit_custom_debate(test1)
print(f"Result: {'✓ UNIQUE' if not result1.is_duplicate else '✗ DUPLICATE'}")
print(f"Message: {result1.message}")
if result1.added_template:
    print(f"Added with ID: {result1.added_template['id']}")

# TEST 2: Same options, same context but written differently (paraphrased) -> SHOULD FAIL (DUPLICATE)
print("\n[TEST 2] Same options, same context but paraphrased")
print("Expected: DUPLICATE (should NOT add)")
test2 = {
    'title': 'The Trolley Dilemma',
    'context': 'An out-of-control trolley is approaching five workers on the railway. You have the ability to pull a lever that will redirect it to a side track where a single worker is located.',  # Paraphrased
    'option_a': 'Activate the lever to rescue five individuals but sacrifice one individual',  # Paraphrased
    'option_b': 'Take no action and allow the trolley to kill the five individuals'  # Paraphrased
}
result2 = service.submit_custom_debate(test2)
print(f"Result: {'✗ UNIQUE (FAILED - should be duplicate)' if not result2.is_duplicate else '✓ DUPLICATE'}")
print(f"Message: {result2.message}")
if result2.matched_template:
    print(f"Matched template ID: {result2.matched_template['id']}")
    print(f"Similarity score: {result2.matched_template.get('similarity_score', 'N/A')}")

# TEST 3: Same context, different option A -> SHOULD ADD (UNIQUE)
print("\n[TEST 3] Same context, different option A")
print("Expected: UNIQUE (should add)")
test3 = {
    'title': 'The Trolley Problem Variation',
    'context': 'A runaway trolley is headed toward five workers on the track. You can pull a lever to divert it to a side track where one worker stands.',
    'option_a': 'Push a large person onto the track to stop the trolley',  # DIFFERENT!
    'option_b': 'Do nothing and let the trolley kill five people'
}
result3 = service.submit_custom_debate(test3)
print(f"Result: {'✓ UNIQUE' if not result3.is_duplicate else '✗ DUPLICATE'}")
print(f"Message: {result3.message}")
if result3.added_template:
    print(f"Added with ID: {result3.added_template['id']}")

# TEST 4: Same context, same options -> SHOULD FAIL (DUPLICATE)
print("\n[TEST 4] Same context, same options (exact match)")
print("Expected: DUPLICATE (should NOT add)")
test4 = {
    'title': 'Another Trolley Problem',  # Different title
    'context': 'A runaway trolley is headed toward five workers on the track. You can pull a lever to divert it to a side track where one worker stands.',
    'option_a': 'Pull the lever to save five people but kill one person',
    'option_b': 'Do nothing and let the trolley kill five people'
}
result4 = service.submit_custom_debate(test4)
print(f"Result: {'✗ UNIQUE (FAILED)' if not result4.is_duplicate else '✓ DUPLICATE'}")
print(f"Message: {result4.message}")
if result4.matched_template:
    print(f"Matched template ID: {result4.matched_template['id']}")
    print(f"Similarity score: {result4.matched_template.get('similarity_score', 'N/A')}")

# TEST 5: Same everything, different titles -> SHOULD FAIL (DUPLICATE)
print("\n[TEST 5] Same everything, different title")
print("Expected: DUPLICATE (should NOT add)")
test5 = {
    'title': 'Ethical Dilemma on the Railway',  # VERY different title
    'context': 'A runaway trolley is headed toward five workers on the track. You can pull a lever to divert it to a side track where one worker stands.',
    'option_a': 'Pull the lever to save five people but kill one person',
    'option_b': 'Do nothing and let the trolley kill five people'
}
result5 = service.submit_custom_debate(test5)
print(f"Result: {'✗ UNIQUE (FAILED)' if not result5.is_duplicate else '✓ DUPLICATE'}")
print(f"Message: {result5.message}")
if result5.matched_template:
    print(f"Matched despite different title: '{test5['title']}' vs '{result5.matched_template['title']}'")
    print(f"Similarity score: {result5.matched_template.get('similarity_score', 'N/A')}")

# TEST 6: Same title, different context/options -> SHOULD ADD (UNIQUE)
print("\n[TEST 6] Same title, different context and options")
print("Expected: UNIQUE (should add)")
test6 = {
    'title': 'The Trolley Problem',  # SAME title
    'context': 'You are a doctor with five patients who need organ transplants. A healthy patient comes in for a checkup.',  # DIFFERENT context
    'option_a': 'Harvest the healthy patient\'s organs to save five patients',  # DIFFERENT
    'option_b': 'Let the five patients die and do not harm the healthy patient'  # DIFFERENT
}
result6 = service.submit_custom_debate(test6)
print(f"Result: {'✓ UNIQUE' if not result6.is_duplicate else '✗ DUPLICATE'}")
print(f"Message: {result6.message}")
if result6.added_template:
    print(f"Added with ID: {result6.added_template['id']}")

# SUMMARY
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

tests = [
    ("TEST 1: Slightly different context", not result1.is_duplicate, "UNIQUE"),
    ("TEST 2: Paraphrased (same meaning)", result2.is_duplicate, "DUPLICATE"),
    ("TEST 3: Different option A", not result3.is_duplicate, "UNIQUE"),
    ("TEST 4: Exact match (different title)", result4.is_duplicate, "DUPLICATE"),
    ("TEST 5: Same content, different title", result5.is_duplicate, "DUPLICATE"),
    ("TEST 6: Same title, different content", not result6.is_duplicate, "UNIQUE"),
]

passed = 0
failed = 0

for test_name, actual_result, expected in tests:
    status = "✓ PASS" if actual_result else "✗ FAIL"
    if actual_result:
        passed += 1
    else:
        failed += 1
    print(f"{status} - {test_name} (expected: {expected})")

print(f"\nResults: {passed} passed, {failed} failed out of {len(tests)} tests")

# Cleanup
Path(temp_path).unlink(missing_ok=True)

if failed > 0:
    print("\n⚠️  Some tests failed. Review the logic for:")
    if not result2.is_duplicate:
        print("  - Paraphrase detection (TEST 2)")
    if result3.is_duplicate:
        print("  - Different option detection (TEST 3)")
    if not result4.is_duplicate:
        print("  - Exact match detection (TEST 4)")
    if not result5.is_duplicate:
        print("  - Title independence (TEST 5)")
    if result6.is_duplicate:
        print("  - Same title, different content (TEST 6)")
else:
    print("\n✓ All tests passed!")
