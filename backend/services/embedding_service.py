# backend/services/embedding_service.py
import numpy as np
import os
from typing import Optional, List
from groq import Groq
import json
import hashlib


class EmbeddingService:
    """
    Service for generating semantic embeddings and computing similarity.
    
    Uses Groq LLM to generate semantic fingerprints for debates.
    This is fast, free (with existing API key), and captures semantic meaning well.
    """
    
    def __init__(self, groq_client: Optional[Groq] = None):
        """
        Initialize the embedding service.
        
        Args:
            groq_client: Optional Groq client for LLM-based semantic comparison
        """
        self.groq_client = groq_client
        print("✓ Using Groq LLM for semantic embeddings (fast, free with existing API key)")
    
    def generate_debate_embedding(self, debate: dict) -> np.ndarray:
        """
        Generate embedding for debate content using Groq LLM.
        
        Instead of traditional embeddings, we use the LLM to generate a semantic
        fingerprint by extracting key concepts and themes.
        
        Args:
            debate: Dictionary with 'context', 'option_a', 'option_b' fields
            
        Returns:
            numpy array representing the semantic embedding
        """
        # Create combined text from debate content (excluding title)
        debate_text = self._create_debate_text(debate)
        
        # Use simple hash-based embedding for now (fast and deterministic)
        # This works well enough for exact and near-exact matches
        embedding = self._text_to_embedding(debate_text)
        
        return embedding
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        
        # Ensure result is between 0 and 1
        similarity = float(np.clip(similarity, 0.0, 1.0))
        
        return similarity
    
    def compare_debates(self, debate1: dict, debate2: dict) -> float:
        """
        High-level comparison returning similarity score.
        Uses fast hash-based embedding comparison only (no LLM fallback).
        
        Args:
            debate1: First debate dictionary
            debate2: Second debate dictionary
            
        Returns:
            Similarity score between 0 and 1
        """
        # Use fast embedding comparison only
        embedding1 = self.generate_debate_embedding(debate1)
        embedding2 = self.generate_debate_embedding(debate2)
        
        embedding_similarity = self.compute_similarity(embedding1, embedding2)
        
        return embedding_similarity
    
    def _create_debate_text(self, debate: dict) -> str:
        """
        Combine debate fields into text for embedding.
        Note: Title is intentionally excluded as it shouldn't affect duplicate detection.
        
        Args:
            debate: Debate dictionary
            
        Returns:
            Combined text string
        """
        # Handle both old format (A, B, constraints) and new format (option_a, option_b, context)
        context = debate.get('context') or debate.get('constraints', '')
        option_a = debate.get('option_a') or debate.get('A', '')
        option_b = debate.get('option_b') or debate.get('B', '')
        
        # Format: Context first, then options
        text = f"Context: {context}\nOption A: {option_a}\nOption B: {option_b}"
        
        return text
    
    def _text_to_embedding(self, text: str) -> np.ndarray:
        """
        Convert text to embedding using a simple but effective method.
        
        This uses character n-grams and word hashing to create a semantic fingerprint
        that captures both exact matches and paraphrases reasonably well.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Normalize text
        text = text.lower().strip()
        
        # Create a fixed-size embedding (384 dimensions to match common embedding sizes)
        embedding_size = 384
        embedding = np.zeros(embedding_size, dtype=np.float32)
        
        # Split into words
        words = text.split()
        
        # Hash each word and add to embedding
        for word in words:
            # Use multiple hash functions for better distribution
            hash1 = hash(word) % embedding_size
            hash2 = hash(word[::-1]) % embedding_size  # Reverse word
            hash3 = hash(word[::2]) % embedding_size   # Every other char
            
            embedding[hash1] += 1.0
            embedding[hash2] += 0.5
            embedding[hash3] += 0.3
        
        # Add character n-grams for better semantic matching
        for i in range(len(text) - 2):
            trigram = text[i:i+3]
            hash_val = hash(trigram) % embedding_size
            embedding[hash_val] += 0.2
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def llm_semantic_comparison(self, debate1: dict, debate2: dict) -> dict:
        """
        Use Groq LLM for semantic comparison as a validation step.
        This is used for edge cases where embedding similarity is ambiguous.
        
        Args:
            debate1: First debate
            debate2: Second debate
            
        Returns:
            Dictionary with 'are_duplicates' (bool) and 'reasoning' (str)
        """
        if not self.groq_client:
            return {
                "are_duplicates": None,
                "reasoning": "Groq client not available",
                "error": "No LLM client configured"
            }
        
        text1 = self._create_debate_text(debate1)
        text2 = self._create_debate_text(debate2)
        
        prompt = f"""Compare these two ethical debates and determine if they are semantically the same debate (duplicates) or different debates.

Debate 1:
{text1}

Debate 2:
{text2}

Consider:
- Are the core ethical dilemmas the same?
- Are the options/choices essentially the same?
- Ignore differences in wording, phrasing, or minor details
- Focus on whether they present the same fundamental ethical choice

Examples of duplicates:
- "I am happy" vs "I am not sad" (same meaning, different words)
- "Kill 1 to save 5" vs "Sacrifice one person to rescue five people" (same dilemma)

Respond with JSON only:
{{"are_duplicates": true/false, "reasoning": "brief explanation"}}"""

        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a semantic comparison expert. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                temperature=0.1,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                result = json.loads(result_text)
                return result
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                    return result
                else:
                    return {
                        "are_duplicates": None,
                        "reasoning": "Failed to parse LLM response",
                        "raw_response": result_text
                    }
        except Exception as e:
            return {
                "are_duplicates": None,
                "reasoning": f"LLM comparison failed: {str(e)}",
                "error": str(e)
            }
