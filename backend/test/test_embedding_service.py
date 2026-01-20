# backend/test/test_embedding_service.py
"""
Unit tests for EmbeddingService
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from services.embedding_service import EmbeddingService


class TestEmbeddingService:
    """Unit tests for embedding service"""
    
    def test_initialization(self):
        """Test service initializes correctly"""
        service = EmbeddingService()
        assert service is not None
        assert service.groq_client is None
    
    def test_initialization_with_groq_client(self):
        """Test service initializes with Groq client"""
        mock_client = Mock()
        service = EmbeddingService(groq_client=mock_client)
        assert service.groq_client == mock_client
    
    def test_create_debate_text_new_format(self):
        """Test debate text creation with new format (context, option_a, option_b)"""
        service = EmbeddingService()
        debate = {
            'title': 'Test Title',
            'context': 'Test context',
            'option_a': 'Option A text',
            'option_b': 'Option B text'
        }
        
        text = service._create_debate_text(debate)
        
        assert 'Test context' in text
        assert 'Option A text' in text
        assert 'Option B text' in text
        assert 'Test Title' not in text  # Title should not be included
        assert text.startswith('Context:')
    
    def test_create_debate_text_old_format(self):
        """Test debate text creation with old format (constraints, A, B)"""
        service = EmbeddingService()
        debate = {
            'title': 'Test Title',
            'constraints': 'Test constraints',
            'A': 'Option A text',
            'B': 'Option B text'
        }
        
        text = service._create_debate_text(debate)
        
        assert 'Test constraints' in text
        assert 'Option A text' in text
        assert 'Option B text' in text
        assert 'Test Title' not in text
    
    def test_generate_embedding_returns_numpy_array(self):
        """Test that embedding generation returns numpy array"""
        service = EmbeddingService()
        debate = {
            'context': 'Test context',
            'option_a': 'Option A',
            'option_b': 'Option B'
        }
        
        embedding = service.generate_debate_embedding(debate)
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 384  # Expected embedding size
        assert embedding.dtype in [np.float32, np.float64]
    
    def test_embedding_is_normalized(self):
        """Test that embeddings are normalized (unit length)"""
        service = EmbeddingService()
        debate = {
            'context': 'Test context',
            'option_a': 'Option A',
            'option_b': 'Option B'
        }
        
        embedding = service.generate_debate_embedding(debate)
        norm = np.linalg.norm(embedding)
        
        # Should be normalized (close to 1.0)
        assert 0.99 <= norm <= 1.01
    
    def test_identical_debates_have_identical_embeddings(self):
        """Test that identical debates produce identical embeddings"""
        service = EmbeddingService()
        debate1 = {
            'context': 'Test context',
            'option_a': 'Option A',
            'option_b': 'Option B'
        }
        debate2 = {
            'context': 'Test context',
            'option_a': 'Option A',
            'option_b': 'Option B'
        }
        
        emb1 = service.generate_debate_embedding(debate1)
        emb2 = service.generate_debate_embedding(debate2)
        
        assert np.allclose(emb1, emb2)
    
    def test_different_debates_have_different_embeddings(self):
        """Test that different debates produce different embeddings"""
        service = EmbeddingService()
        debate1 = {
            'context': 'Context about trolley problem',
            'option_a': 'Pull the lever',
            'option_b': 'Do nothing'
        }
        debate2 = {
            'context': 'Context about privacy',
            'option_a': 'Allow surveillance',
            'option_b': 'Protect privacy'
        }
        
        emb1 = service.generate_debate_embedding(debate1)
        emb2 = service.generate_debate_embedding(debate2)
        
        assert not np.allclose(emb1, emb2)
    
    def test_compute_similarity_range(self):
        """Test that similarity scores are in valid range [0, 1]"""
        service = EmbeddingService()
        
        # Create two random embeddings
        emb1 = np.random.rand(384).astype(np.float32)
        emb2 = np.random.rand(384).astype(np.float32)
        
        similarity = service.compute_similarity(emb1, emb2)
        
        assert 0.0 <= similarity <= 1.0
        assert isinstance(similarity, float)
    
    def test_compute_similarity_identical_vectors(self):
        """Test that identical vectors have similarity of 1.0"""
        service = EmbeddingService()
        
        emb = np.random.rand(384).astype(np.float32)
        similarity = service.compute_similarity(emb, emb)
        
        assert 0.99 <= similarity <= 1.0
    
    def test_compute_similarity_zero_vectors(self):
        """Test handling of zero vectors"""
        service = EmbeddingService()
        
        emb1 = np.zeros(384, dtype=np.float32)
        emb2 = np.random.rand(384).astype(np.float32)
        
        similarity = service.compute_similarity(emb1, emb2)
        
        assert similarity == 0.0
    
    def test_compute_similarity_symmetric(self):
        """Test that similarity is symmetric"""
        service = EmbeddingService()
        
        emb1 = np.random.rand(384).astype(np.float32)
        emb2 = np.random.rand(384).astype(np.float32)
        
        sim_ab = service.compute_similarity(emb1, emb2)
        sim_ba = service.compute_similarity(emb2, emb1)
        
        assert np.isclose(sim_ab, sim_ba)
    
    def test_compare_debates_returns_float(self):
        """Test that compare_debates returns a float score"""
        service = EmbeddingService()
        debate1 = {
            'context': 'Context 1',
            'option_a': 'Option A1',
            'option_b': 'Option B1'
        }
        debate2 = {
            'context': 'Context 2',
            'option_a': 'Option A2',
            'option_b': 'Option B2'
        }
        
        score = service.compare_debates(debate1, debate2)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    def test_title_does_not_affect_embedding(self):
        """Test that different titles don't affect embeddings"""
        service = EmbeddingService()
        debate1 = {
            'title': 'Title 1',
            'context': 'Same context',
            'option_a': 'Same option A',
            'option_b': 'Same option B'
        }
        debate2 = {
            'title': 'Completely Different Title',
            'context': 'Same context',
            'option_a': 'Same option A',
            'option_b': 'Same option B'
        }
        
        emb1 = service.generate_debate_embedding(debate1)
        emb2 = service.generate_debate_embedding(debate2)
        
        # Embeddings should be identical despite different titles
        assert np.allclose(emb1, emb2)
    
    @patch('services.embedding_service.Groq')
    def test_llm_semantic_comparison_no_client(self, mock_groq):
        """Test LLM comparison when no client is available"""
        service = EmbeddingService(groq_client=None)
        debate1 = {'context': 'c1', 'option_a': 'a1', 'option_b': 'b1'}
        debate2 = {'context': 'c2', 'option_a': 'a2', 'option_b': 'b2'}
        
        result = service.llm_semantic_comparison(debate1, debate2)
        
        assert result['are_duplicates'] is None
        assert 'error' in result
    
    def test_llm_semantic_comparison_with_mock_client(self):
        """Test LLM comparison with mocked Groq client"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"are_duplicates": true, "reasoning": "Same debate"}'
        mock_client.chat.completions.create.return_value = mock_response
        
        service = EmbeddingService(groq_client=mock_client)
        debate1 = {'context': 'c1', 'option_a': 'a1', 'option_b': 'b1'}
        debate2 = {'context': 'c2', 'option_a': 'a2', 'option_b': 'b2'}
        
        result = service.llm_semantic_comparison(debate1, debate2)
        
        assert result['are_duplicates'] is True
        assert 'reasoning' in result
        assert mock_client.chat.completions.create.called
    
    def test_llm_semantic_comparison_handles_json_in_markdown(self):
        """Test LLM comparison handles JSON wrapped in markdown code blocks"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '```json\n{"are_duplicates": false, "reasoning": "Different"}\n```'
        mock_client.chat.completions.create.return_value = mock_response
        
        service = EmbeddingService(groq_client=mock_client)
        debate1 = {'context': 'c1', 'option_a': 'a1', 'option_b': 'b1'}
        debate2 = {'context': 'c2', 'option_a': 'a2', 'option_b': 'b2'}
        
        result = service.llm_semantic_comparison(debate1, debate2)
        
        assert result['are_duplicates'] is False
        assert 'reasoning' in result
    
    def test_llm_semantic_comparison_handles_api_error(self):
        """Test LLM comparison handles API errors gracefully"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        service = EmbeddingService(groq_client=mock_client)
        debate1 = {'context': 'c1', 'option_a': 'a1', 'option_b': 'b1'}
        debate2 = {'context': 'c2', 'option_a': 'a2', 'option_b': 'b2'}
        
        result = service.llm_semantic_comparison(debate1, debate2)
        
        assert result['are_duplicates'] is None
        assert 'error' in result
