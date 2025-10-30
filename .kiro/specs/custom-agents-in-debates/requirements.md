# Requirements Document

## Introduction

This feature enables custom agents created through the Agent Builder to participate in live ethical debates alongside or instead of the default agents (Deon, Conse, Virtue). Users will be able to select any combination of default and custom agents to form their debate team, and the system will handle the debate flow seamlessly regardless of agent type.

## Glossary

- **System**: The MirrorMinds ethical debate platform
- **User**: A person using the platform to create debates
- **Custom Agent**: An AI agent created by users through the Agent Builder with personalized ethical frameworks
- **Default Agent**: One of the three built-in agents (Deon, Conse, Virtue)
- **Debate Team**: A group of exactly 3 agents selected to participate in a debate
- **Agent Selector**: The UI component that allows users to choose agents for their debate team
- **Debate Engine**: The backend service that orchestrates the debate flow and generates agent responses
- **System Prompt**: The AI instruction that defines an agent's personality and behavior

## Requirements

### Requirement 1

**User Story:** As a user, I want to select custom agents for debates, so that I can see how my personalized ethical frameworks perform in real discussions

#### Acceptance Criteria

1. WHEN the User views the Agent Selector, THE System SHALL display all available custom agents alongside default agents
2. WHEN the User selects a custom agent for a debate slot, THE System SHALL validate that the agent exists and is available
3. WHEN the User attempts to select the same agent for multiple slots, THE System SHALL prevent duplicate selection and display a warning
4. WHEN the User completes agent selection with exactly 3 agents, THE System SHALL enable the "Start Debate" button
5. WHEN the User starts a debate with custom agents, THE System SHALL pass the selected agent IDs to the debate engine

### Requirement 2

**User Story:** As a user, I want custom agents to participate in debates using their enhanced prompts, so that they debate according to their defined personalities

#### Acceptance Criteria

1. WHEN the Debate Engine receives a custom agent ID, THE System SHALL retrieve the agent's system prompt from storage
2. WHEN the Debate Engine generates a response for a custom agent, THE System SHALL use the agent's system prompt instead of default prompts
3. WHEN a custom agent responds in a debate, THE System SHALL format the response in the same JSON structure as default agents
4. WHEN a custom agent's response fails to parse, THE System SHALL retry with adjusted parameters before falling back to error handling
5. WHEN a custom agent participates in a debate, THE System SHALL increment the agent's usage count in storage

### Requirement 3

**User Story:** As a user, I want to see custom agents displayed properly in the debate interface, so that I can distinguish them from default agents

#### Acceptance Criteria

1. WHEN the Debate View renders agents, THE System SHALL display custom agent names and avatars from their stored data
2. WHEN a custom agent is thinking, THE System SHALL show the same "Thinking..." animation as default agents
3. WHEN a custom agent speaks, THE System SHALL display their argument in a speech bubble with their avatar
4. WHEN the User views debate history with custom agents, THE System SHALL preserve and display custom agent information correctly
5. WHEN a custom agent no longer exists, THE System SHALL display a placeholder with the agent's last known name

### Requirement 4

**User Story:** As a user, I want to mix default and custom agents in the same debate, so that I can compare different ethical frameworks

#### Acceptance Criteria

1. WHEN the User selects agents for a debate, THE System SHALL allow any combination of default and custom agents
2. WHEN the Debate Engine processes a mixed team, THE System SHALL correctly identify agent types and use appropriate system prompts
3. WHEN agents respond in a mixed debate, THE System SHALL maintain consistent turn order regardless of agent type
4. WHEN the Judge evaluates a mixed debate, THE System SHALL score all agents using the same criteria
5. WHEN the System displays debate results, THE System SHALL show all agents with their correct names and avatars

### Requirement 5

**User Story:** As a user, I want custom agents to address each other by name in debates, so that the conversation feels natural and coherent

#### Acceptance Criteria

1. WHEN a custom agent generates a counter-argument, THE System SHALL provide the names of all participating agents in the prompt
2. WHEN a custom agent responds, THE System SHALL validate that the response mentions an opponent's name
3. WHEN the response validation fails, THE System SHALL retry with more explicit formatting instructions
4. WHEN agents from different types debate, THE System SHALL ensure all agents can reference each other correctly
5. WHEN the System builds the debate context, THE System SHALL include agent names and their latest stances for all participants

### Requirement 6

**User Story:** As a developer, I want the debate system to handle agent failures gracefully, so that one broken agent doesn't crash the entire debate

#### Acceptance Criteria

1. WHEN a custom agent's system prompt fails to generate a response, THE System SHALL log the error and attempt a retry
2. WHEN retries are exhausted, THE System SHALL insert a fallback response indicating the agent encountered an error
3. WHEN an agent is deleted mid-debate, THE System SHALL continue the debate with remaining agents
4. WHEN the System cannot load an agent's data, THE System SHALL display an error message to the User
5. WHEN multiple agents fail in sequence, THE System SHALL offer the User an option to restart with different agents

### Requirement 7

**User Story:** As a user, I want to see which custom agents are most popular, so that I can discover high-quality agents created by the community

#### Acceptance Criteria

1. WHEN the User views the Agent Selector, THE System SHALL display usage count for each custom agent
2. WHEN the User sorts agents, THE System SHALL provide options to sort by usage count, rating, or creation date
3. WHEN a custom agent completes a debate, THE System SHALL increment its usage count immediately
4. WHEN the User views agent details, THE System SHALL show total debates participated and average performance metrics
5. WHEN the System displays popular agents, THE System SHALL highlight agents with high usage and ratings

## Non-Functional Requirements

### Performance

1. Agent selection SHALL load all available agents within 2 seconds
2. Custom agent system prompt retrieval SHALL complete within 500ms
3. Debate initialization with custom agents SHALL not exceed 3 seconds

### Reliability

1. The System SHALL handle up to 100 custom agents without performance degradation
2. Agent data SHALL be persisted reliably with automatic backup
3. Debate flow SHALL continue even if one agent fails to respond

### Usability

1. Agent selection interface SHALL clearly distinguish between default and custom agents
2. Error messages SHALL provide actionable guidance for users
3. Custom agent avatars SHALL be clearly visible in all debate views

### Maintainability

1. Agent type detection logic SHALL be centralized in a single service
2. System prompt retrieval SHALL use a consistent interface for all agent types
3. Debate engine SHALL be extensible to support future agent types
