# backend/services/debate_deduplication_service.py
import json
import os
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import re
from services.embedding_service import EmbeddingService


class DeduplicationResult:
    """Result of debate deduplication check"""
    
    def __init__(self, success: bool, is_duplicate: bool, message: str, 
                 matched_template: Optional[dict] = None, 
                 added_template: Optional[dict] = None):
        self.success = success
        self.is_duplicate = is_duplicate
        self.message = message
        self.matched_template = matched_template
        self.added_template = added_template
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        result = {
            'success': self.success,
            'is_duplicate': self.is_duplicate,
            'message': self.message
        }
        if self.matched_template:
            result['matched_template'] = self.matched_template
        if self.added_template:
            result['added_template'] = self.added_template
        return result


class DebateDeduplicationService:
    """
    Service for managing debate library and detecting duplicates.
    
    Handles:
    - Loading/saving debate templates
    - Generating slugs and IDs
    - Semantic duplicate detection
    - Adding unique debates to library
    """
    
    def __init__(self, templates_path: str = "data/debate_templates.json", 
                 embedding_service: Optional[EmbeddingService] = None,
                 groq_client = None):
        """
        Initialize the deduplication service.
        
        Args:
            templates_path: Path to debate templates JSON file
            embedding_service: Optional embedding service (creates new one if not provided)
            groq_client: Optional Groq client for LLM-based comparison
        """
        self.templates_path = Path(templates_path)
        self.embedding_service = embedding_service or EmbeddingService(groq_client=groq_client)
        
        # Ensure data directory exists
        self.templates_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize templates file if it doesn't exist
        if not self.templates_path.exists():
            self._save_templates([])
    
    def submit_custom_debate(self, debate: dict) -> DeduplicationResult:
        """
        Main entry point for debate submission.
        
        Checks for duplicates and adds to library if unique.
        
        Args:
            debate: Dictionary with 'title', 'context', 'option_a', 'option_b'
            
        Returns:
            DeduplicationResult indicating if added or duplicate found
        """
        try:
            # Validate debate has required fields
            required_fields = ['title', 'context', 'option_a', 'option_b']
            missing_fields = [f for f in required_fields if not debate.get(f)]
            
            if missing_fields:
                return DeduplicationResult(
                    success=False,
                    is_duplicate=False,
                    message=f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            # Check for duplicates
            duplicate = self.find_duplicate(debate)
            
            if duplicate:
                return DeduplicationResult(
                    success=True,
                    is_duplicate=True,
                    message="This debate already exists in the library.",
                    matched_template=duplicate
                )
            
            # Add to library
            added_template = self.add_to_library(debate)
            
            return DeduplicationResult(
                success=True,
                is_duplicate=False,
                message="Debate added to library successfully!",
                added_template=added_template
            )
            
        except Exception as e:
            return DeduplicationResult(
                success=False,
                is_duplicate=False,
                message=f"Failed to process debate: {str(e)}"
            )
    
    def find_duplicate(self, debate: dict) -> Optional[dict]:
        """
        Search for semantic duplicates in existing library.
        Uses LLM to make intelligent duplicate detection decisions.
        
        Args:
            debate: Debate to check
            
        Returns:
            Matching template if found, None otherwise
        """
        templates = self._load_templates()
        
        if not templates:
            return None
        
        # Use LLM-based comparison for accurate semantic matching
        candidate_text = self.embedding_service._create_debate_text(debate)
        
        for template in templates:
            template_text = self.embedding_service._create_debate_text(template)
            
            # Ask LLM if these are duplicates
            is_duplicate = self._llm_duplicate_check(candidate_text, template_text, debate['title'], template.get('title', ''))
            
            if is_duplicate:
                result = template.copy()
                result['similarity_score'] = 1.0  # LLM confirmed duplicate
                return result
        
        return None
    
    def _llm_duplicate_check(self, debate1_text: str, debate2_text: str, title1: str, title2: str) -> bool:
        """
        Use LLM to determine if two debates are duplicates.
        
        Args:
            debate1_text: First debate content (context + options)
            debate2_text: Second debate content (context + options)
            title1: First debate title (for context only)
            title2: Second debate title (for context only)
            
        Returns:
            True if debates are duplicates, False otherwise
        """
        if not self.embedding_service.groq_client:
            # Fallback to simple text comparison if no LLM available
            return debate1_text.lower().strip() == debate2_text.lower().strip()
        
        prompt = f"""You are a semantic duplicate detector for ethical debates. Determine if these two debates are the SAME debate or DIFFERENT debates.

DEBATE 1 (Title: "{title1}"):
{debate1_text}

DEBATE 2 (Title: "{title2}"):
{debate2_text}

RULES FOR DUPLICATE DETECTION:
1. IGNORE titles completely - titles don't matter for duplicate detection
2. Focus ONLY on the content: context and the two options
3. Consider debates DUPLICATES if:
   - The ethical dilemma/scenario is the same (even if worded differently)
   - Both options present the same choices (even if paraphrased)
   - Example: "I am happy" vs "I am not sad" = SAME meaning = DUPLICATE
   - Example: "Kill 1 to save 5" vs "Sacrifice one person to rescue five people" = DUPLICATE

4. Consider debates DIFFERENT if:
   - The context/scenario is different
   - ANY option is different (even if context is same)
   - Example: Same trolley context but "pull lever" vs "push person" = DIFFERENT
   - Example: Same context but different option B = DIFFERENT

Respond with ONLY "DUPLICATE" or "DIFFERENT" - nothing else."""

        try:
            response = self.embedding_service.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a precise semantic comparison expert. Respond with only DUPLICATE or DIFFERENT."},
                    {"role": "user", "content": prompt}
                ],
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                temperature=0.1,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
            return "DUPLICATE" in result
            
        except Exception as e:
            print(f"LLM duplicate check failed: {e}")
            # Fallback to exact text match
            return debate1_text.lower().strip() == debate2_text.lower().strip()
    
    def add_to_library(self, debate: dict) -> dict:
        """
        Add unique debate to templates library.
        
        Args:
            debate: Debate to add
            
        Returns:
            The added template with generated ID and slug
        """
        templates = self._load_templates()
        
        # Generate new ID (max existing ID + 1)
        if templates:
            max_id = max(t.get('id', 0) for t in templates)
            new_id = max_id + 1
        else:
            new_id = 1
        
        # Generate slug from title
        slug = self._generate_slug(debate['title'], templates)
        
        # Create new template
        new_template = {
            'id': new_id,
            'slug': slug,
            'title': debate['title'],
            'context': debate['context'],
            'option_a': debate['option_a'],
            'option_b': debate['option_b'],
            'created_at': datetime.now().isoformat(),
            'is_custom': True
        }
        
        # Add to templates
        templates.append(new_template)
        
        # Save atomically
        self._save_templates(templates)
        
        return new_template
    
    def _load_templates(self) -> List[dict]:
        """Load debate templates from JSON file"""
        try:
            if not self.templates_path.exists():
                return []
            
            with open(self.templates_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            return templates if isinstance(templates, list) else []
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading templates: {e}")
            return []
    
    def _save_templates(self, templates: List[dict]) -> None:
        """
        Persist templates back to JSON file.
        Uses atomic write (write to temp, then rename) for safety.
        """
        # Write to temporary file first
        temp_path = self.templates_path.with_suffix('.tmp')
        
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(templates, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_path.replace(self.templates_path)
            
        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise e
    
    def _generate_slug(self, title: str, existing_templates: List[dict]) -> str:
        """
        Generate URL-friendly slug from title.
        Ensures uniqueness by appending number if needed.
        
        Args:
            title: Debate title
            existing_templates: List of existing templates to check against
            
        Returns:
            Unique slug
        """
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
        slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces/multiple hyphens
        slug = slug.strip('-')                 # Remove leading/trailing hyphens
        
        # Limit length
        slug = slug[:50]
        
        # Check for uniqueness
        existing_slugs = {t.get('slug') for t in existing_templates}
        
        if slug not in existing_slugs:
            return slug
        
        # Append number if slug exists
        counter = 2
        while f"{slug}-{counter}" in existing_slugs:
            counter += 1
        
        return f"{slug}-{counter}"
    
    def _has_significant_field_difference(self, debate1: dict, debate2: dict) -> bool:
        """
        Check if debates have significant differences in individual fields.
        Used for medium-similarity cases (0.75-0.90).
        
        Args:
            debate1: First debate
            debate2: Second debate
            
        Returns:
            True if there's a significant field-level difference
        """
        # Compare each content field individually
        fields = ['context', 'option_a', 'option_b']
        
        for field in fields:
            text1 = debate1.get(field, '')
            text2 = debate2.get(field, '')
            
            # Create simple embeddings for each field
            emb1 = self.embedding_service._text_to_embedding(text1)
            emb2 = self.embedding_service._text_to_embedding(text2)
            
            field_similarity = self.embedding_service.compute_similarity(emb1, emb2)
            
            # If any field is significantly different (< 0.80), debates are unique
            if field_similarity < 0.80:
                return True
        
        # All fields are similar
        return False
