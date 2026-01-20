# Design Document: Semantic Debate Deduplication

## Overview

This feature adds intelligent semantic deduplication to the Mirror Minds debate system, automatically adding user-created custom debates to the debate library while preventing duplicate entries. The system uses LLM-based semantic analysis to compare debate content (context, option A, option B) rather than relying on superficial text matching or titles.

The key innovation is recognizing that debates with different titles but identical content are duplicates, while debates with identical titles but different content are unique. This requires semantic understanding beyond simple string comparison or cosine similarity.

## Architecture

### High-Level Flow

```
User Creates Custom Debate
         ↓
Extract Debate Content (context, optionA, optionB)
         ↓
Generate Semantic Embeddings (via Triage Model)
         ↓
Compare Against Existing Library Debates
         ↓
Calculate Similarity Scores
         ↓
Apply Deduplication Logic
         ↓
    [Duplicate?]
    /          \
  Yes           No
   ↓             ↓
Notify User   Add to Library
Show Match    Persist & Notify
```

### Component Architecture

The system consists of three main layers:

1. **API Layer** (`backend/main.py`)
   - New endpoint: `POST /api/debates/submit`
   - Receives custom debate submissions
   - Orchestrates deduplication workflow
   - Returns result to frontend

2. **Service Layer** (`backend/services/debate_deduplication_service.py`)
   - Core deduplication logic
   - Semantic comparison algorithms
   - Template management

3. **LLM Integration Layer** (`backend/services/embedding_service.py`)
   - Triage model integration
   - Embedding generation
   - Similarity computation

## Components and Interfaces

### 1. Debate Deduplication Service

**File**: `backend/services/debate_deduplication_service.py`

**Responsibilities**:
- Load existing debate templates
- Coordinate semantic comparison
- Apply deduplication rules
- Add unique debates to library
- Generate user-facing notifications

**Key Methods**:

```python
class DebateDeduplicationService:
    def __init__(self, templates_path: str, embedding_service: EmbeddingService)
    
    def submit_custom_debate(self, debate: dict) -> DeduplicationResult:
        """
        Main entry point for debate submission.
        Returns result indicating if added or duplicate found.
        """
    
    def find_duplicate(self, debate: dict) -> Optional[dict]:
        """
        Search for semantic duplicates in existing library.
        Returns matching template if found, None otherwise.
        """
    
    def add_to_library(self, debate: dict) -> dict:
        """
        Add unique debate to templates library.
        Generates slug, assigns ID, persists to JSON.
        """
    
    def _load_templates(self) -> List[dict]:
        """Load debate templates from JSON file"""
    
    def _save_templates(self, templates: List[dict]) -> None:
        """Persist templates back to JSON file"""
```

**Data Structures**:

```python
class DeduplicationResult:
    success: bool
    is_duplicate: bool
    message: str
    matched_template: Optional[dict]  # If duplicate
    added_template: Optional[dict]    # If unique
```

### 2. Embedding Service

**File**: `backend/services/embedding_service.py`

**Responsibilities**:
- Interface with triage LLM model
- Generate semantic embeddings
- Compute similarity scores
- Handle API errors gracefully

**Key Methods**:

```python
class EmbeddingService:
    def __init__(self, groq_client=None, model_name: str = "groq-embedding-model")
    
    def generate_debate_embedding(self, debate: dict) -> np.ndarray:
        """
        Generate embedding for debate content.
        Combines context, optionA, optionB into single representation.
        """
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        Returns score between 0 and 1.
        """
    
    def compare_debates(self, debate1: dict, debate2: dict) -> float:
        """
        High-level comparison returning similarity score.
        """
    
    def _create_debate_text(self, debate: dict) -> str:
        """
        Combine debate fields into text for embedding.
        Format: "Context: {context}\nOption A: {optionA}\nOption B: {optionB}"
        """
```

**Model Selection**:
- Primary: Groq embedding models (free with existing API key)
- Models available: Check Groq API documentation for latest embedding models
- Fallback: Use existing Groq LLM for semantic comparison if embeddings unavailable
- Configuration via environment variables (reuse existing GROQ_API_KEY)

### 3. API Endpoint

**Endpoint**: `POST /api/debates/submit`

**Request Body**:
```json
{
  "title": "string",
  "context": "string",
  "option_a": "string",
  "option_b": "string"
}
```

**Response** (Success - Added):
```json
{
  "success": true,
  "is_duplicate": false,
  "message": "Debate added to library successfully!",
  "template": {
    "id": 29,
    "slug": "generated-slug",
    "title": "...",
    "context": "...",
    "option_a": "...",
    "option_b": "..."
  }
}
```

**Response** (Duplicate Found):
```json
{
  "success": true,
  "is_duplicate": true,
  "message": "This debate already exists in the library.",
  "matched_template": {
    "id": 1,
    "slug": "trolley-switch",
    "title": "The Classic Trolley Problem",
    "similarity_score": 0.94
  }
}
```

**Response** (Error):
```json
{
  "success": false,
  "is_duplicate": false,
  "message": "Failed to process debate: {error_details}",
  "error": "string"
}
```

### 4. Frontend Integration

**File**: `frontend/src/components/DilemmaForm.jsx`

**Changes**:
- Add "Save to Library" checkbox/button after debate creation
- Show notification after submission
- Handle duplicate detection gracefully

**User Flow**:
1. User fills out custom debate form
2. User proceeds to agent selection
3. After debate completes (or before starting), option to "Save to Library"
4. System checks for duplicates
5. User receives feedback (added or duplicate found)

## Data Models

### Debate Template Structure

```json
{
  "id": "number (auto-incremented)",
  "slug": "string (kebab-case, generated from title)",
  "title": "string",
  "context": "string (formerly 'constraints')",
  "option_a": "string (formerly 'A')",
  "option_b": "string (formerly 'B')",
  "created_at": "ISO timestamp (optional, for custom debates)",
  "is_custom": "boolean (optional, marks user-created debates)"
}
```

**Note**: The existing templates use `constraints`, `A`, and `B` fields. We'll normalize to `context`, `option_a`, `option_b` internally while maintaining backward compatibility.

### Embedding Cache Structure

To avoid re-computing embeddings for existing templates:

```json
{
  "template_id": 1,
  "embedding": [0.123, -0.456, ...],
  "model": "text-embedding-3-small",
  "generated_at": "ISO timestamp"
}
```

**File**: `backend/data/debate_embeddings_cache.json`

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing all acceptance criteria, several properties were identified as redundant:
- Properties about storage persistence and API availability can be combined into a single round-trip property
- Multiple properties testing "any field difference = unique" can be unified
- Notification properties can be consolidated to focus on response structure rather than message content
- Properties about title vs content comparison overlap and can be merged

The following properties represent the minimal set needed to validate all functional requirements:

### Core Correctness Properties

**Property 1: Debate Addition Round Trip**
*For any* valid debate, if it is submitted and classified as unique, then querying the library API should return a debate with matching content fields (context, option_a, option_b).
**Validates: Requirements 1.2, 1.3**

**Property 2: Library Preservation Invariant**
*For any* existing debate library state, adding a new unique debate should preserve all existing debates (no data loss).
**Validates: Requirements 1.4**

**Property 3: Content-Based Duplicate Detection**
*For any* debate, creating a copy with identical content (context, option_a, option_b) but a different title should be classified as a duplicate.
**Validates: Requirements 2.3, 3.5**

**Property 4: Title Independence**
*For any* debate, modifying only the title while keeping content identical should not affect duplicate classification.
**Validates: Requirements 2.2, 3.4**

**Property 5: Single Field Difference Uniqueness**
*For any* debate, if exactly one content field (context, option_a, or option_b) differs from an existing debate while the other two are identical, the debates should be classified as unique.
**Validates: Requirements 4.1, 4.2, 4.3**

**Property 6: All Fields Similar Implies Duplicate**
*For any* two debates where all three content fields (context, option_a, option_b) have semantic similarity above the threshold, the debates should be classified as duplicates.
**Validates: Requirements 4.4**

**Property 7: Similarity Score Bounds**
*For any* two debates, the computed similarity score should be a value between 0 and 1 inclusive.
**Validates: Requirements 3.2**

**Property 8: Duplicate Prevention**
*For any* debate classified as a duplicate, the library size should remain unchanged after submission.
**Validates: Requirements 2.4**

**Property 9: Unique Addition**
*For any* debate classified as unique, the library size should increase by exactly 1 after submission.
**Validates: Requirements 2.5**

**Property 10: Error Handling Graceful Degradation**
*For any* debate submission where embedding generation fails, the system should return an error response without crashing and without modifying the library.
**Validates: Requirements 5.3, 5.4**

**Property 11: Response Structure Completeness**
*For any* debate submission, the response should contain all required fields: success (boolean), is_duplicate (boolean), and message (string).
**Validates: Requirements 6.1, 6.2, 6.3**

## Semantic Comparison Algorithm

### Deduplication Logic

The system uses a multi-stage comparison approach:

1. **Embedding Generation**
   - Combine content fields: `f"Context: {context}\nOption A: {option_a}\nOption B: {option_b}"`
   - Generate embedding vector using triage model
   - Cache embeddings for existing templates

2. **Similarity Computation**
   - Compute cosine similarity between candidate and each existing template
   - Cosine similarity formula: `similarity = (A · B) / (||A|| × ||B||)`
   - Results in score between 0 (completely different) and 1 (identical)

3. **Threshold Application**
   - **High Similarity Threshold**: 0.90 - Strong duplicate indicator
   - **Medium Similarity Threshold**: 0.75 - Potential duplicate, requires field-level check
   - **Low Similarity**: < 0.75 - Likely unique

4. **Field-Level Validation** (for medium similarity)
   - Compare individual fields if overall similarity is 0.75-0.90
   - Check if any single field differs significantly
   - If one field differs substantially, classify as unique despite high overall similarity

### Why Cosine Similarity Alone Isn't Enough

Pure cosine similarity has limitations:
- May miss paraphrased content
- Sensitive to word choice variations
- Doesn't capture semantic equivalence well

Our approach enhances this by:
- Using high-quality embedding models that capture semantics
- Applying field-level validation for edge cases
- Using appropriate thresholds based on empirical testing

### Threshold Calibration

Initial thresholds are set conservatively:
- **0.90+**: Very likely duplicate (block addition)
- **0.75-0.90**: Possible duplicate (field-level check)
- **< 0.75**: Likely unique (allow addition)

These can be tuned based on:
- False positive rate (unique debates blocked)
- False negative rate (duplicates added)
- User feedback

## Error Handling

### Error Scenarios

1. **Embedding Service Unavailable**
   - Catch API connection errors
   - Return error response with guidance
   - Log error for monitoring
   - Do not modify library

2. **Invalid Debate Format**
   - Validate required fields present
   - Check field lengths (min/max)
   - Return 400 Bad Request with details

3. **File System Errors**
   - Handle JSON read/write failures
   - Implement atomic writes (write to temp, then rename)
   - Backup templates before modification

4. **Embedding Generation Timeout**
   - Set reasonable timeout (30 seconds)
   - Retry once with exponential backoff
   - Fall back to error response if retry fails

### Error Response Format

```json
{
  "success": false,
  "is_duplicate": false,
  "message": "User-friendly error message",
  "error": "Technical error details",
  "retry_possible": true
}
```

## Testing Strategy

### Unit Testing

**Framework**: pytest

**Test Coverage**:

1. **Debate Deduplication Service Tests**
   - Test loading/saving templates
   - Test slug generation from titles
   - Test ID assignment
   - Test duplicate detection with known examples
   - Test unique debate addition

2. **Embedding Service Tests**
   - Test embedding generation with mock API
   - Test similarity computation with known vectors
   - Test error handling for API failures
   - Test debate text formatting

3. **API Endpoint Tests**
   - Test successful debate submission
   - Test duplicate detection response
   - Test error responses
   - Test request validation

### Property-Based Testing

**Framework**: Hypothesis (Python)

**Configuration**: Minimum 100 iterations per property test

**Test Implementation**:

Each property test must:
- Be tagged with format: `# Feature: semantic-debate-deduplication, Property {N}: {description}`
- Reference the design document property number
- Use Hypothesis strategies to generate random debates
- Verify the property holds across all generated inputs

**Example Property Test Structure**:

```python
from hypothesis import given, strategies as st

# Feature: semantic-debate-deduplication, Property 1: Debate Addition Round Trip
@given(st.builds(generate_random_debate))
def test_debate_addition_round_trip(debate):
    """For any valid debate, if added as unique, it should be retrievable"""
    # Submit debate
    result = service.submit_custom_debate(debate)
    
    # If classified as unique
    if not result.is_duplicate:
        # Should be retrievable from library
        templates = service._load_templates()
        assert any(
            t['context'] == debate['context'] and
            t['option_a'] == debate['option_a'] and
            t['option_b'] == debate['option_b']
            for t in templates
        )
```

**Generators**:

```python
def generate_random_debate():
    """Generate random valid debate for testing"""
    return {
        'title': st.text(min_size=10, max_size=100),
        'context': st.text(min_size=50, max_size=500),
        'option_a': st.text(min_size=20, max_size=200),
        'option_b': st.text(min_size=20, max_size=200)
    }
```

### Integration Testing

1. **End-to-End Debate Submission**
   - Create custom debate via API
   - Verify deduplication check runs
   - Verify correct response
   - Verify library state

2. **Duplicate Detection Accuracy**
   - Submit known duplicate debates
   - Verify correct classification
   - Test with paraphrased content
   - Test with title variations

3. **Error Recovery**
   - Simulate embedding service failures
   - Verify graceful error handling
   - Verify library integrity maintained

## Performance Considerations

### Embedding Cache

- Cache embeddings for all existing templates on service initialization
- Update cache when new debates added
- Persist cache to disk for faster startup
- Cache invalidation: regenerate if model changes

### Scalability

Current approach scales linearly with library size:
- O(n) comparisons for n existing templates
- Each comparison is O(1) with cached embeddings

For large libraries (1000+ debates):
- Consider approximate nearest neighbor search (FAISS, Annoy)
- Batch embedding generation
- Implement pagination for library queries

### API Rate Limits

Embedding API considerations:
- OpenAI: 3000 requests/minute (tier 1)
- Implement request queuing if needed
- Cache aggressively to minimize API calls
- Monitor usage and costs

## Configuration

### Environment Variables

```bash
# Embedding Service Configuration (reuse existing Groq setup)
GROQ_API_KEY=<existing-groq-api-key>
GROQ_EMBEDDING_MODEL=groq-embedding-model  # Check Groq docs for available models
EMBEDDING_TIMEOUT=30

# Deduplication Thresholds
DUPLICATE_THRESHOLD_HIGH=0.90
DUPLICATE_THRESHOLD_MEDIUM=0.75

# Feature Flags
ENABLE_DEDUPLICATION=true
ENABLE_EMBEDDING_CACHE=true
```

### File Paths

```
backend/
  data/
    debate_templates.json          # Main library
    debate_embeddings_cache.json   # Embedding cache
  services/
    debate_deduplication_service.py
    embedding_service.py
```

## Migration Plan

### Phase 1: Service Implementation
- Implement EmbeddingService
- Implement DebateDeduplicationService
- Add unit tests

### Phase 2: API Integration
- Add `/api/debates/submit` endpoint
- Integrate with existing debate flow
- Add integration tests

### Phase 3: Frontend Integration
- Add "Save to Library" UI
- Handle submission responses
- Display notifications

### Phase 4: Optimization
- Implement embedding cache
- Tune similarity thresholds
- Monitor performance

## Security Considerations

1. **Input Validation**
   - Sanitize all user input
   - Limit field lengths
   - Prevent injection attacks

2. **Rate Limiting**
   - Limit debate submissions per user/IP
   - Prevent library spam

3. **API Key Security**
   - Store embedding API keys in environment variables
   - Never expose in client code
   - Rotate keys periodically

## Monitoring and Observability

### Metrics to Track

1. **Functional Metrics**
   - Debates submitted per day
   - Duplicate detection rate
   - False positive rate (user reports)
   - Library growth rate

2. **Performance Metrics**
   - Embedding generation latency
   - Similarity computation time
   - End-to-end submission time
   - Cache hit rate

3. **Error Metrics**
   - Embedding API failures
   - File system errors
   - Invalid submissions

### Logging

Log levels:
- **INFO**: Successful submissions, duplicates found
- **WARNING**: Retries, high latency
- **ERROR**: API failures, file system errors
- **DEBUG**: Similarity scores, detailed comparison results

## Future Enhancements

1. **User Feedback Loop**
   - Allow users to report false positives/negatives
   - Use feedback to tune thresholds
   - Implement manual override for edge cases

2. **Advanced Similarity Metrics**
   - Experiment with other distance metrics
   - Combine multiple similarity signals
   - Use LLM-based comparison for edge cases

3. **Batch Processing**
   - Allow bulk debate imports
   - Deduplicate entire libraries
   - Merge duplicate entries

4. **Debate Clustering**
   - Group similar debates by topic
   - Suggest related debates to users
   - Improve library navigation
