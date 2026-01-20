# Requirements Document

## Introduction

This feature enables automatic addition of user-created custom debates to the debate library while preventing duplicate entries through semantic analysis. The system will use LLM-based semantic comparison to determine if a newly created debate is substantially similar to existing debates in the library, focusing on the actual content (context, option A, option B) rather than superficial differences like titles.

## Glossary

- **Debate Template**: A structured debate scenario containing a title, context, option A, and option B
- **Custom Debate**: A debate created by a user through the debate creation interface
- **Debate Library**: The collection of available debate templates stored in the system
- **Semantic Deduplication**: The process of identifying duplicate debates based on meaning rather than exact text matching
- **Triage Model**: A lightweight, cost-effective LLM used for semantic comparison tasks
- **Debate Content**: The combination of context, option A, and option B fields that define the substance of a debate
- **Mirror Minds System**: The debate application system that facilitates AI agent debates

## Requirements

### Requirement 1

**User Story:** As a user, I want my custom debates to be automatically added to the debate library, so that I can reuse them and share them with others without manual intervention.

#### Acceptance Criteria

1. WHEN a user completes creating a custom debate THEN the Mirror Minds System SHALL automatically submit the debate for library addition
2. WHEN a custom debate is successfully added to the library THEN the Mirror Minds System SHALL persist the debate to the debate templates storage
3. WHEN a custom debate is added to the library THEN the Mirror Minds System SHALL make it immediately available for selection in the debate library interface
4. WHEN the debate library is updated THEN the Mirror Minds System SHALL maintain all existing debate templates without data loss

### Requirement 2

**User Story:** As a user, I want the system to prevent duplicate debates from cluttering my library, so that I have a clean, organized collection of unique debate scenarios.

#### Acceptance Criteria

1. WHEN a custom debate is submitted for library addition THEN the Mirror Minds System SHALL perform semantic comparison against all existing debate templates
2. WHEN semantic comparison is performed THEN the Mirror Minds System SHALL analyze the debate content fields (context, option A, option B) for similarity
3. WHEN two debates have semantically identical content THEN the Mirror Minds System SHALL classify them as duplicates regardless of title differences
4. WHEN a debate is classified as a duplicate THEN the Mirror Minds System SHALL prevent addition to the library and maintain the existing entry
5. WHEN a debate is classified as unique THEN the Mirror Minds System SHALL proceed with library addition

### Requirement 3

**User Story:** As a system administrator, I want the deduplication system to use semantic analysis rather than simple text matching, so that debates with different wording but same meaning are correctly identified as duplicates.

#### Acceptance Criteria

1. WHEN comparing debate content THEN the Mirror Minds System SHALL use a Triage Model to generate semantic embeddings for each debate
2. WHEN semantic embeddings are generated THEN the Mirror Minds System SHALL compute similarity scores between the candidate debate and existing debates
3. WHEN similarity scores are computed THEN the Mirror Minds System SHALL apply a threshold to determine duplicate classification
4. WHEN debates have identical titles but different content THEN the Mirror Minds System SHALL classify them as unique debates
5. WHEN debates have different titles but identical content THEN the Mirror Minds System SHALL classify them as duplicate debates

### Requirement 4

**User Story:** As a user, I want the system to recognize that debates are different when any core content field differs, so that legitimate variations are preserved in the library.

#### Acceptance Criteria

1. WHEN two debates have identical context and option A but different option B THEN the Mirror Minds System SHALL classify them as unique debates
2. WHEN two debates have identical context and option B but different option A THEN the Mirror Minds System SHALL classify them as unique debates
3. WHEN two debates have identical option A and option B but different context THEN the Mirror Minds System SHALL classify them as unique debates
4. WHEN all three content fields (context, option A, option B) are semantically similar THEN the Mirror Minds System SHALL classify them as duplicate debates

### Requirement 5

**User Story:** As a system administrator, I want the deduplication process to use a cost-effective LLM, so that the feature remains economically viable at scale.

#### Acceptance Criteria

1. WHEN performing semantic comparison THEN the Mirror Minds System SHALL use a lightweight Triage Model for embedding generation
2. WHEN selecting a Triage Model THEN the Mirror Minds System SHALL prioritize models with low cost per token
3. WHEN the Triage Model is unavailable THEN the Mirror Minds System SHALL handle the error gracefully and allow manual review
4. WHEN embedding generation fails THEN the Mirror Minds System SHALL log the error and notify the user of the failure

### Requirement 6

**User Story:** As a user, I want to receive feedback about whether my debate was added or identified as a duplicate, so that I understand what happened to my submission.

#### Acceptance Criteria

1. WHEN a debate is successfully added to the library THEN the Mirror Minds System SHALL display a success notification to the user
2. WHEN a debate is identified as a duplicate THEN the Mirror Minds System SHALL display a notification indicating which existing debate it matches
3. WHEN deduplication processing fails THEN the Mirror Minds System SHALL display an error message with actionable guidance
4. WHEN a notification is displayed THEN the Mirror Minds System SHALL provide clear, non-technical language describing the outcome
