# backend/test/test_embedding_service_properties.py
"""
Property-based tests for EmbeddingService

Feature: semantic-debate-deduplication
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings, HealthCheck
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


class TestEmbeddingServiceProperties:
    """Property-based tests for embedding service"""
    
    # Feature: semantic-debate-deduplication, Property 7: Similarity Score Bounds
    # Validates: Requirements 3.2
    @given(debate1=debate_strategy(), debate2=debate_strategy())
    @settings(max_examples=100, deadline=None)
    def test_similarity_score_bounds(self, debate1, debate2):
        """
        Property 7: Similarity Score Bounds
        For any two debates, the computed similarity score should be 
        a value between 0 and 1 inclusive.
        """
        embedding_service = EmbeddingService()
        
        # Generate embeddings
        embedding1 = embedding_service.generate_debate_embedding(debate1)
        embedding2 = embedding_service.generate_debate_embedding(debate2)
        
        # Compute similarity
        similarity = embedding_service.compute_similarity(embedding1, embedding2)
        
        # Assert bounds
        assert 0.0 <= similarity <= 1.0, \
            f"Similarity score {similarity} is outside bounds [0, 1]"
        
        # Verify it's a float
        assert isinstance(similarity, float), \
            f"Similarity score should be float, got {type(similarity)}"
    
    @given(debate=debate_strategy())
    @settings(max_examples=100, deadline=None)
    def test_self_similarity_is_one(self, debate):
        """
        Property: Self-similarity should be 1.0
        For any debate, comparing it with itself should yield similarity of 1.0
        """
        embedding_service = EmbeddingService()
        embedding = embedding_service.generate_debate_embedding(debate)
        similarity = embedding_service.compute_similarity(embedding, embedding)
        
        # Self-similarity should be very close to 1.0 (allowing for floating point errors)
        assert 0.99 <= similarity <= 1.0, \
            f"Self-similarity should be ~1.0, got {similarity}"
    
    @given(debate=debate_strategy())
    @settings(max_examples=100)
    def test_embedding_deterministic(self, debate):
        """
        Property: Embeddings should be deterministic
        For any debate, generating the embedding twice should produce the same result
        """
        embedding_service = EmbeddingService()
        embedding1 = embedding_service.generate_debate_embedding(debate)
        embedding2 = embedding_service.generate_debate_embedding(debate)
        
        # Embeddings should be identical
        assert np.allclose(embedding1, embedding2), \
            "Embeddings for same debate should be identical"
    
    @given(debate=debate_strategy())
    @settings(max_examples=100)
    def test_embedding_is_vector(self, debate):
        """
        Property: Embeddings should be numpy arrays
        For any debate, the embedding should be a numpy array with positive length
        """
        embedding_service = EmbeddingService()
        embedding = embedding_service.generate_debate_embedding(debate)
        
        assert isinstance(embedding, np.ndarray), \
            f"Embedding should be numpy array, got {type(embedding)}"
        
        assert len(embedding) > 0, \
            "Embedding should have positive length"
        
        assert embedding.dtype in [np.float32, np.float64], \
            f"Embedding should be float type, got {embedding.dtype}"
    
    @given(debate1=debate_strategy(), debate2=debate_strategy())
    @settings(max_examples=100)
    def test_similarity_symmetric(self, debate1, debate2):
        """
        Property: Similarity should be symmetric
        For any two debates, similarity(A, B) should equal similarity(B, A)
        """
        embedding_service = EmbeddingService()
        embedding1 = embedding_service.generate_debate_embedding(debate1)
        embedding2 = embedding_service.generate_debate_embedding(debate2)
        
        similarity_ab = embedding_service.compute_similarity(embedding1, embedding2)
        similarity_ba = embedding_service.compute_similarity(embedding2, embedding1)
        
        assert np.isclose(similarity_ab, similarity_ba), \
            f"Similarity should be symmetric: {similarity_ab} != {similarity_ba}"
    
    @given(debate=debate_strategy())
    @settings(max_examples=50)
    def test_title_not_in_embedding_text(self, debate):
        """
        Property: Title should not affect embedding
        The debate text used for embedding should not include the title
        """
        embedding_service = EmbeddingService()
        debate_text = embedding_service._create_debate_text(debate)
        
        # The debate text should start with "Context:" not with the title
        assert debate_text.startswith("Context:"), \
            "Debate text should start with 'Context:', not title"
        
        # Context and options should be present
        context = debate.get('context', '')
        option_a = debate.get('option_a', '')
        option_b = debate.get('option_b', '')
        
        if context:
            assert context in debate_text, "Context should be in embedding text"
        if option_a:
            assert option_a in debate_text, "Option A should be in embedding text"
        if option_b:
            assert option_b in debate_text, "Option B should be in embedding text"
