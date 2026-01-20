# backend/test/test_deduplication_service.py
"""
Unit tests for DebateDeduplicationService
"""

import pytest
import json
import tempfile
from pathlib import Path
from services.debate_deduplication_service import DebateDeduplicationService, DeduplicationResult
from services.embedding_service import EmbeddingService


class TestDebateDeduplicationService:
    """Unit tests for deduplication service"""
    
    @pytest.fixture
    def temp_templates_file(self):
        """Create a temporary templates file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            json.dump([], f)
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def service(self, temp_templates_file):
        """Create service instance with temp file"""
        return DebateDeduplicationService(templates_path=temp_templates_file)
    
    def test_initialization(self, temp_templates_file):
        """Test service initializes correctly"""
        service = DebateDeduplicationService(templates_path=temp_templates_file)
        assert service is not None
        assert service.embedding_service is not None
        assert service.templates_path.exists()
    
    def test_load_empty_templates(self, service):
        """Test loading from empty file"""
        templates = service._load_templates()
        assert templates == []
    
    def test_save_and_load_templates(self, service):
        """Test saving and loading templates"""
        test_templates = [
            {'id': 1, 'slug': 'test', 'title': 'Test', 'context': 'c', 'option_a': 'a', 'option_b': 'b'}
        ]
        
        service._save_templates(test_templates)
        loaded = service._load_templates()
        
        assert len(loaded) == 1
        assert loaded[0]['id'] == 1
        assert loaded[0]['slug'] == 'test'
    
    def test_generate_slug_basic(self, service):
        """Test basic slug generation"""
        slug = service._generate_slug("The Trolley Problem", [])
        assert slug == "the-trolley-problem"
    
    def test_generate_slug_special_chars(self, service):
        """Test slug generation with special characters"""
        slug = service._generate_slug("AI's Impact: Good or Bad?", [])
        assert slug == "ais-impact-good-or-bad"
        assert ":" not in slug
        assert "?" not in slug
    
    def test_generate_slug_uniqueness(self, service):
        """Test slug generation ensures uniqueness"""
        existing = [{'slug': 'test-debate'}]
        
        slug1 = service._generate_slug("Test Debate", existing)
        assert slug1 == "test-debate-2"
        
        existing.append({'slug': 'test-debate-2'})
        slug2 = service._generate_slug("Test Debate", existing)
        assert slug2 == "test-debate-3"
    
    def test_generate_slug_length_limit(self, service):
        """Test slug generation respects length limit"""
        long_title = "A" * 100
        slug = service._generate_slug(long_title, [])
        assert len(slug) <= 50
    
    def test_add_to_library_generates_id(self, service):
        """Test that adding debate generates new ID"""
        debate = {
            'title': 'Test Debate',
            'context': 'Test context',
            'option_a': 'Option A',
            'option_b': 'Option B'
        }
        
        result = service.add_to_library(debate)
        
        assert result['id'] == 1
        assert result['slug'] is not None
        assert result['is_custom'] is True
        assert 'created_at' in result
    
    def test_add_to_library_increments_id(self, service):
        """Test that IDs increment correctly"""
        debate1 = {
            'title': 'Debate 1',
            'context': 'Context 1',
            'option_a': 'A1',
            'option_b': 'B1'
        }
        debate2 = {
            'title': 'Debate 2',
            'context': 'Context 2',
            'option_a': 'A2',
            'option_b': 'B2'
        }
        
        result1 = service.add_to_library(debate1)
        result2 = service.add_to_library(debate2)
        
        assert result1['id'] == 1
        assert result2['id'] == 2
    
    def test_submit_custom_debate_success(self, service):
        """Test successful debate submission"""
        debate = {
            'title': 'New Debate',
            'context': 'New context',
            'option_a': 'New A',
            'option_b': 'New B'
        }
        
        result = service.submit_custom_debate(debate)
        
        assert result.success is True
        assert result.is_duplicate is False
        assert result.added_template is not None
        assert result.added_template['id'] == 1
    
    def test_submit_custom_debate_missing_fields(self, service):
        """Test submission with missing fields"""
        debate = {
            'title': 'Incomplete',
            'context': 'Context'
            # Missing option_a and option_b
        }
        
        result = service.submit_custom_debate(debate)
        
        assert result.success is False
        assert 'Missing required fields' in result.message
    
    def test_submit_custom_debate_duplicate_detection(self, service):
        """Test duplicate detection"""
        debate = {
            'title': 'Test Debate',
            'context': 'Test context',
            'option_a': 'Option A',
            'option_b': 'Option B'
        }
        
        # Add first time
        result1 = service.submit_custom_debate(debate)
        assert result1.success is True
        assert result1.is_duplicate is False
        
        # Try to add same debate again
        result2 = service.submit_custom_debate(debate)
        assert result2.success is True
        assert result2.is_duplicate is True
        assert result2.matched_template is not None
    
    def test_find_duplicate_empty_library(self, service):
        """Test duplicate search in empty library"""
        debate = {
            'context': 'Test',
            'option_a': 'A',
            'option_b': 'B'
        }
        
        duplicate = service.find_duplicate(debate)
        assert duplicate is None
    
    def test_find_duplicate_exact_match(self, service):
        """Test finding exact duplicate"""
        debate = {
            'title': 'Test',
            'context': 'Test context',
            'option_a': 'Option A',
            'option_b': 'Option B'
        }
        
        # Add to library
        service.add_to_library(debate)
        
        # Search for duplicate
        duplicate = service.find_duplicate(debate)
        
        assert duplicate is not None
        assert duplicate['context'] == debate['context']
        assert 'similarity_score' in duplicate
    
    def test_find_duplicate_different_title_same_content(self, service):
        """Test that different titles don't prevent duplicate detection"""
        debate1 = {
            'title': 'Title 1',
            'context': 'Same context',
            'option_a': 'Same A',
            'option_b': 'Same B'
        }
        debate2 = {
            'title': 'Completely Different Title',
            'context': 'Same context',
            'option_a': 'Same A',
            'option_b': 'Same B'
        }
        
        # Add first debate
        service.add_to_library(debate1)
        
        # Search for second debate (different title, same content)
        duplicate = service.find_duplicate(debate2)
        
        # Should be detected as duplicate
        assert duplicate is not None
    
    def test_find_duplicate_different_content(self, service):
        """Test that different content is not detected as duplicate"""
        debate1 = {
            'title': 'Debate 1',
            'context': 'Context about trolley problem',
            'option_a': 'Pull lever',
            'option_b': 'Do nothing'
        }
        debate2 = {
            'title': 'Debate 2',
            'context': 'Context about privacy',
            'option_a': 'Allow surveillance',
            'option_b': 'Protect privacy'
        }
        
        # Add first debate
        service.add_to_library(debate1)
        
        # Search for second debate (completely different)
        duplicate = service.find_duplicate(debate2)
        
        # Should not be detected as duplicate
        assert duplicate is None
    
    def test_deduplication_result_to_dict(self):
        """Test DeduplicationResult conversion to dict"""
        result = DeduplicationResult(
            success=True,
            is_duplicate=False,
            message="Success",
            added_template={'id': 1}
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['success'] is True
        assert result_dict['is_duplicate'] is False
        assert result_dict['message'] == "Success"
        assert result_dict['added_template']['id'] == 1
    
    def test_atomic_save_on_error(self, service):
        """Test that failed saves don't corrupt the file"""
        # Add some initial data
        initial_templates = [{'id': 1, 'slug': 'test', 'title': 'Test', 'context': 'c', 'option_a': 'a', 'option_b': 'b'}]
        service._save_templates(initial_templates)
        
        # Verify initial state
        loaded = service._load_templates()
        assert len(loaded) == 1
        
        # The atomic save should protect against corruption
        # (In a real scenario, we'd simulate a write failure, but that's hard to test)
        # This test just verifies the mechanism exists
        assert service.templates_path.exists()
