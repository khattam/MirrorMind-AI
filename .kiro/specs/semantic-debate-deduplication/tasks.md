# Implementation Plan: Semantic Debate Deduplication

- [ ] 1. Set up embedding service infrastructure
  - Create `backend/services/embedding_service.py` with EmbeddingService class
  - Implement embedding generation using Groq embedding models (reuse existing GROQ_API_KEY)
  - Implement cosine similarity computation
  - Add fallback to Groq LLM for semantic comparison if embeddings unavailable
  - _Requirements: 3.1, 3.2, 5.1_

- [ ] 1.1 Write property test for embedding service
  - **Property 7: Similarity Score Bounds**
  - **Validates: Requirements 3.2**

- [ ] 1.2 Write unit tests for embedding service
  - Test embedding generation with mock API responses
  - Test similarity computation with known vectors
  - Test error handling for API failures
  - Test debate text formatting
  - _Requirements: 3.1, 3.2_

- [ ] 2. Implement debate deduplication service core logic
  - Create `backend/services/debate_deduplication_service.py` with DebateDeduplicationService class
  - Implement template loading from `debate_templates.json`
  - Implement template saving with atomic writes
  - Implement slug generation from titles
  - Implement ID assignment for new debates
  - _Requirements: 1.2, 2.1_

- [ ] 2.1 Write property test for library preservation
  - **Property 2: Library Preservation Invariant**
  - **Validates: Requirements 1.4**

- [ ] 2.2 Write unit tests for template management
  - Test loading templates from JSON
  - Test saving templates to JSON
  - Test slug generation from various titles
  - Test ID assignment logic
  - _Requirements: 1.2_

- [ ] 3. Implement semantic comparison and duplicate detection
  - Implement `find_duplicate()` method using embedding service
  - Implement similarity threshold logic (high: 0.90, medium: 0.75)
  - Implement field-level validation for medium similarity cases
  - Add comparison against all existing templates
  - _Requirements: 2.1, 2.2, 2.3, 3.3_

- [ ] 3.1 Write property test for content-based duplicate detection
  - **Property 3: Content-Based Duplicate Detection**
  - **Validates: Requirements 2.3, 3.5**

- [ ] 3.2 Write property test for title independence
  - **Property 4: Title Independence**
  - **Validates: Requirements 2.2, 3.4**

- [ ] 3.3 Write property test for single field difference
  - **Property 5: Single Field Difference Uniqueness**
  - **Validates: Requirements 4.1, 4.2, 4.3**

- [ ] 3.4 Write property test for all fields similar
  - **Property 6: All Fields Similar Implies Duplicate**
  - **Validates: Requirements 4.4**

- [ ] 3.5 Write unit tests for duplicate detection
  - Test duplicate detection with identical content
  - Test unique detection with different content
  - Test threshold boundary cases
  - Test field-level validation logic
  - _Requirements: 2.1, 2.2, 2.3, 3.3_

- [ ] 4. Implement debate submission workflow
  - Implement `submit_custom_debate()` method as main entry point
  - Implement `add_to_library()` method for unique debates
  - Implement DeduplicationResult data structure
  - Add proper error handling for all failure scenarios
  - Add logging for submissions, duplicates, and errors
  - _Requirements: 1.1, 2.4, 2.5_

- [ ] 4.1 Write property test for duplicate prevention
  - **Property 8: Duplicate Prevention**
  - **Validates: Requirements 2.4**

- [ ] 4.2 Write property test for unique addition
  - **Property 9: Unique Addition**
  - **Validates: Requirements 2.5**

- [ ] 4.3 Write property test for error handling
  - **Property 10: Error Handling Graceful Degradation**
  - **Validates: Requirements 5.3, 5.4**

- [ ] 4.4 Write unit tests for submission workflow
  - Test successful unique debate submission
  - Test duplicate debate rejection
  - Test error scenarios (API failure, file errors)
  - Test logging output
  - _Requirements: 1.1, 2.4, 2.5, 5.3, 5.4_

- [ ] 5. Implement embedding cache system
  - Create `backend/data/debate_embeddings_cache.json` structure
  - Implement cache loading on service initialization
  - Implement cache updates when debates are added
  - Implement cache persistence to disk
  - Add cache invalidation logic for model changes
  - _Requirements: 3.1_

- [ ] 5.1 Write unit tests for embedding cache
  - Test cache loading and saving
  - Test cache updates on debate addition
  - Test cache invalidation
  - Test performance improvement with cache
  - _Requirements: 3.1_

- [ ] 6. Create API endpoint for debate submission
  - Add `POST /api/debates/submit` endpoint in `backend/main.py`
  - Implement request validation (required fields, field lengths)
  - Integrate with DebateDeduplicationService
  - Implement response formatting for success, duplicate, and error cases
  - Add proper HTTP status codes (200, 400, 500)
  - _Requirements: 1.1, 6.1, 6.2, 6.3_

- [ ] 6.1 Write property test for response structure
  - **Property 11: Response Structure Completeness**
  - **Validates: Requirements 6.1, 6.2, 6.3**

- [ ] 6.2 Write integration tests for API endpoint
  - Test successful debate submission via API
  - Test duplicate detection via API
  - Test error responses via API
  - Test request validation
  - _Requirements: 1.1, 6.1, 6.2, 6.3_

- [ ] 7. Checkpoint - Ensure all backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Add frontend "Save to Library" functionality
  - Add "Save to Library" button/checkbox to DilemmaForm component
  - Implement API call to `/api/debates/submit` endpoint
  - Handle loading state during submission
  - _Requirements: 1.1_

- [ ] 9. Implement frontend notification system
  - Create notification component for submission feedback
  - Display success message when debate added
  - Display duplicate message with matched template info
  - Display error message with actionable guidance
  - Add auto-dismiss for success notifications
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 9.1 Write unit tests for frontend notifications
  - Test notification display for success case
  - Test notification display for duplicate case
  - Test notification display for error case
  - Test auto-dismiss behavior
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 10. Integrate submission into debate workflow
  - Add submission trigger after debate creation
  - Update DebateLibrary component to refresh after additions
  - Handle submission in debate completion flow
  - Add user preference for auto-save vs manual save
  - _Requirements: 1.1, 1.3_

- [ ] 10.1 Write property test for debate addition round trip
  - **Property 1: Debate Addition Round Trip**
  - **Validates: Requirements 1.2, 1.3**

- [ ] 10.2 Write integration tests for full workflow
  - Test end-to-end debate creation and library addition
  - Test duplicate detection in full workflow
  - Test library refresh after addition
  - Test error handling in full workflow
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 11. Add environment configuration
  - Add embedding service configuration to `.env.example`
  - Document required environment variables (reuse existing GROQ_API_KEY)
  - Add configuration validation on service startup
  - Set default values for thresholds
  - _Requirements: 5.1, 5.2_

- [ ] 12. Write comprehensive edge case tests for semantic similarity
  - Test Case 1: Same content, different title - should be DUPLICATE
  - Test Case 2: Same context and option A, different option B - should be UNIQUE
  - Test Case 3: Same context and option B, different option A - should be UNIQUE
  - Test Case 4: Same options, different context - should be UNIQUE
  - Test Case 5: All same content but paraphrased (e.g., "I am happy" vs "I am not sad") - should be DUPLICATE
  - Test Case 6: Trolley problem with different wording but same meaning - should be DUPLICATE
  - Test Case 7: Two completely different debates - should be UNIQUE
  - Test Case 8: Same debate with minor typos/punctuation differences - should be DUPLICATE
  - Test Case 9: Same ethical dilemma but with different specific examples - should be evaluated based on semantic similarity
  - Test Case 10: Verify title is NOT a factor in duplicate detection
  - _Requirements: 2.2, 2.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4_

- [ ] 13. Create terminal testing script for manual validation
  - Create `backend/test_deduplication_manual.py` script
  - Add sample debates covering all edge cases from Task 12
  - Script should print similarity scores and classification for each test case
  - Include debates that are: identical, slightly different, paraphrased, completely different
  - Add color-coded output (green=correct, red=incorrect classification)
  - Allow running individual test cases or all at once
  - Output detailed comparison results showing why each decision was made
  - _Requirements: 2.1, 2.2, 2.3, 3.3, 4.1, 4.2, 4.3, 4.4_

- [ ] 14. Checkpoint - Manual terminal testing and validation
  - Run the manual testing script with various debate samples
  - Verify all edge cases are handled correctly
  - Tune similarity thresholds if needed based on results
  - Document any issues or unexpected behaviors
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. Add environment configuration
  - Add embedding service configuration to `.env.example`
  - Document required environment variables (reuse existing GROQ_API_KEY)
  - Add configuration validation on service startup
  - Set default values for thresholds
  - _Requirements: 5.1, 5.2_

- [ ] 16. Final checkpoint - Ensure all automated tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Add frontend "Save to Library" functionality
  - Add "Save to Library" button/checkbox to DilemmaForm component
  - Implement API call to `/api/debates/submit` endpoint
  - Handle loading state during submission
  - _Requirements: 1.1_

- [ ] 9. Implement frontend notification system
  - Create notification component for submission feedback
  - Display success message when debate added
  - Display duplicate message with matched template info
  - Display error message with actionable guidance
  - Add auto-dismiss for success notifications
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 9.1 Write unit tests for frontend notifications
  - Test notification display for success case
  - Test notification display for duplicate case
  - Test notification display for error case
  - Test auto-dismiss behavior
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 10. Integrate submission into debate workflow
  - Add submission trigger after debate creation
  - Update DebateLibrary component to refresh after additions
  - Handle submission in debate completion flow
  - Add user preference for auto-save vs manual save
  - _Requirements: 1.1, 1.3_

- [ ] 10.1 Write property test for debate addition round trip
  - **Property 1: Debate Addition Round Trip**
  - **Validates: Requirements 1.2, 1.3**

- [ ] 10.2 Write integration tests for full workflow
  - Test end-to-end debate creation and library addition
  - Test duplicate detection in full workflow
  - Test library refresh after addition
  - Test error handling in full workflow
  - _Requirements: 1.1, 1.2, 1.3_
