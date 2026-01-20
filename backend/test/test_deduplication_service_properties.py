# backend/test/test_deduplication_service_properties.py
"""
Property-based tests for DebateDeduplicationService

Feature: semantic-debate-deduplication
"""

import pytest
import json
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
from services.debate_deduplication_service import DebateDeduplicationService
from services.embedding_service import EmbeddingService


# Strategies for generating test data
@st.composite
def debate_strategy(draw):
    """Generate random debate dictionaries"""
    return {
        'title': draw(st.text(min_size=10, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',)))),
        'context': draw(st.text(min_size=50, max_size=500, alphabet=st.characters(blacklist_categories=('Cs',)))),
        'option_a': draw(st.text(min_size=20, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',)))),
        'option_b': draw(st.text(min_size=20, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',)))),
    }


class TestDebateDeduplicationServiceProperties:
    """Property-based tests for deduplication service"""
    
    # Feature: semantic-debate-deduplication, Property 2: Library Preservation Invariant
    # Validates: Requirements 1.4
    @given(debate=debate_strategy())
    @settings(max_examples=50, deadline=None)
    def test_library_preservation_invariant(self, debate):
        """
        Property 2: Library Preservation Invariant
        For any existing debate library state, adding a new unique debate 
        should preserve all existing debates (no data loss).
        """
        # Create temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            # Create initial library with some debates
            initial_debates = [
                {
                    'id': 1,
                    'slug': 'test-debate-1',
                    'title': 'Test Debate 1',
                    'context': 'Context 1',
                    'option_a': 'Option A1',
                    'option_b': 'Option B1'
                },
                {
                    'id': 2,
                    'slug': 'test-debate-2',
                    'title': 'Test Debate 2',
                    'context': 'Context 2',
                    'option_a': 'Option A2',
                    'option_b': 'Option B2'
                }
            ]
            json.dump(initial_debates, f)
        
        try:
            # Create service with temp file
            service = DebateDeduplicationService(templates_path=temp_path)
            
            # Load initial state
            before_templates = service._load_templates()
            before_count = len(before_templates)
            before_ids = {t['id'] for t in before_templates}
            before_slugs = {t['slug'] for t in before_templates}
            
            # Add new debate (should be unique since it's randomly generated)
            result = service.submit_custom_debate(debate)
            
            # Load after state
            after_templates = service._load_templates()
            after_count = len(after_templates)
            after_ids = {t['id'] for t in after_templates}
            after_slugs = {t['slug'] for t in after_templates}
            
            # Verify preservation: all original IDs and slugs still exist
            assert before_ids.issubset(after_ids), \
                "Original debate IDs should be preserved"
            assert before_slugs.issubset(after_slugs), \
                "Original debate slugs should be preserved"
            
            # Verify all original debates still exist with same content
            for original in before_templates:
                matching = [t for t in after_templates if t['id'] == original['id']]
                assert len(matching) == 1, f"Original debate {original['id']} should still exist"
                assert matching[0]['title'] == original['title'], \
                    "Original debate content should be unchanged"
            
            # If debate was added (not duplicate), count should increase by 1
            if not result.is_duplicate:
                assert after_count == before_count + 1, \
                    "Library should grow by 1 when unique debate added"
            else:
                # If duplicate, count should stay same
                assert after_count == before_count, \
                    "Library size should not change when duplicate detected"
        
        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)
    
    @given(debate=debate_strategy())
    @settings(max_examples=30, deadline=None)
    def test_unique_debate_increases_library_size(self, debate):
        """
        Property: Adding a unique debate increases library size by exactly 1
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            json.dump([], f)  # Start with empty library
        
        try:
            service = DebateDeduplicationService(templates_path=temp_path)
            
            before_count = len(service._load_templates())
            result = service.submit_custom_debate(debate)
            after_count = len(service._load_templates())
            
            if result.success and not result.is_duplicate:
                assert after_count == before_count + 1, \
                    "Unique debate should increase library size by 1"
        
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    @given(debate=debate_strategy())
    @settings(max_examples=30, deadline=None)
    def test_duplicate_debate_preserves_library_size(self, debate):
        """
        Property: Adding a duplicate debate should not change library size
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            json.dump([], f)
        
        try:
            service = DebateDeduplicationService(templates_path=temp_path)
            
            # Add debate first time
            first_result = service.submit_custom_debate(debate)
            count_after_first = len(service._load_templates())
            
            # Try to add same debate again
            second_result = service.submit_custom_debate(debate)
            count_after_second = len(service._load_templates())
            
            # Second addition should be detected as duplicate
            assert second_result.is_duplicate, \
                "Identical debate should be detected as duplicate"
            
            # Library size should not change
            assert count_after_second == count_after_first, \
                "Duplicate should not increase library size"
        
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    @given(title=st.text(min_size=5, max_size=100))
    @settings(max_examples=50, deadline=None)
    def test_slug_generation_is_deterministic(self, title):
        """
        Property: Slug generation should be deterministic for same title
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            json.dump([], f)
        
        try:
            service = DebateDeduplicationService(templates_path=temp_path)
            
            slug1 = service._generate_slug(title, [])
            slug2 = service._generate_slug(title, [])
            
            assert slug1 == slug2, \
                "Slug generation should be deterministic"
            
            # Slug should be URL-friendly (lowercase, hyphens, no special chars)
            assert slug1.islower() or not slug1.isalpha(), \
                "Slug should be lowercase"
            assert ' ' not in slug1, \
                "Slug should not contain spaces"
        
        finally:
            Path(temp_path).unlink(missing_ok=True)
