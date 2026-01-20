#!/usr/bin/env python3
"""
Manual testing script for debate deduplication.
Run this to test the feature end-to-end.
"""

from services.debate_deduplication_service import DebateDeduplicationService
from services.embedding_service import EmbeddingService
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Initialize services
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None
embedding_service = EmbeddingService(groq_client=groq_client)
dedup_service = DebateDeduplicationService(
    templates_path="data/debate_templates.json",
    embedding_service=embedding_service
)

print("=" * 80)
print("DEBATE DEDUPLICATION TESTING")
print("=" * 80)

# Test Case 1: Add a completely new debate
print("\n[TEST 1] Adding a new unique debate...")
debate1 = {
    'title': 'AI Consciousness Rights',
    'context': 'If AI becomes conscious, should it have legal rights?',
    'option_a': 'Grant AI full legal rights as sentient beings',
    'option_b': 'Keep AI as property without rights'
}

result1 = dedup_service.submit_custom_debate(debate1)
print(f"✓ Result: {result1.message}")
print(f"  Is duplicate: {result1.is_duplicate}")
if result1.added_template:
    print(f"  Added with ID: {result1.added_template['id']}")

# Test Case 2: Try to add the SAME debate again (should be duplicate)
print("\n[TEST 2] Adding the same debate again (should detect duplicate)...")
result2 = dedup_service.submit_custom_debate(debate1)
print(f"✓ Result: {result2.message}")
print(f"  Is duplicate: {result2.is_duplicate}")
if result2.matched_template:
    print(f"  Matched template ID: {result2.matched_template['id']}")
    print(f"  Similarity score: {result2.matched_template.get('similarity_score', 'N/A')}")

# Test Case 3: Same content, different title (should be duplicate)
print("\n[TEST 3] Same content but different title (should detect duplicate)...")
debate3 = {
    'title': 'Rights for Sentient Machines',  # Different title
    'context': 'If AI becomes conscious, should it have legal rights?',  # Same content
    'option_a': 'Grant AI full legal rights as sentient beings',
    'option_b': 'Keep AI as property without rights'
}

result3 = dedup_service.submit_custom_debate(debate3)
print(f"✓ Result: {result3.message}")
print(f"  Is duplicate: {result3.is_duplicate}")
if result3.matched_template:
    print(f"  Matched despite different title!")
    print(f"  Original title: {result3.matched_template['title']}")

# Test Case 4: Different option B (should be unique)
print("\n[TEST 4] Same context but different option B (should be unique)...")
debate4 = {
    'title': 'AI Rights Variation',
    'context': 'If AI becomes conscious, should it have legal rights?',
    'option_a': 'Grant AI full legal rights as sentient beings',
    'option_b': 'Grant limited rights but not full personhood'  # Different!
}

result4 = dedup_service.submit_custom_debate(debate4)
print(f"✓ Result: {result4.message}")
print(f"  Is duplicate: {result4.is_duplicate}")
if result4.added_template:
    print(f"  Added as unique debate with ID: {result4.added_template['id']}")

# Test Case 5: Paraphrased version (semantic duplicate)
print("\n[TEST 5] Paraphrased version (should detect as duplicate)...")
debate5 = {
    'title': 'Machine Consciousness Legal Status',
    'context': 'Should conscious artificial intelligence be granted legal protections?',  # Paraphrased
    'option_a': 'Yes, give AI complete legal rights if sentient',  # Paraphrased
    'option_b': 'No, maintain AI as property without rights'  # Paraphrased
}

result5 = dedup_service.submit_custom_debate(debate5)
print(f"✓ Result: {result5.message}")
print(f"  Is duplicate: {result5.is_duplicate}")
if result5.matched_template:
    print(f"  Detected paraphrase as duplicate!")
    print(f"  Similarity score: {result5.matched_template.get('similarity_score', 'N/A')}")

# Test Case 6: Completely different debate
print("\n[TEST 6] Completely different debate (should be unique)...")
debate6 = {
    'title': 'Climate Engineering Ethics',
    'context': 'Should we use geoengineering to combat climate change?',
    'option_a': 'Deploy solar radiation management to cool the planet',
    'option_b': 'Rely only on emissions reduction and natural solutions'
}

result6 = dedup_service.submit_custom_debate(debate6)
print(f"✓ Result: {result6.message}")
print(f"  Is duplicate: {result6.is_duplicate}")
if result6.added_template:
    print(f"  Added as unique debate with ID: {result6.added_template['id']}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
templates = dedup_service._load_templates()
print(f"Total debates in library: {len(templates)}")
print(f"\nCustom debates added:")
for t in templates:
    if t.get('is_custom'):
        print(f"  - ID {t['id']}: {t['title']}")

print("\n✓ Testing complete!")
