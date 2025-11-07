# Requirements Document: Custom Agents in Debates

## Introduction

This feature enables custom agents (created through the Agent Builder) to participate in live ethical debates alongside or instead of the default agents (Deon, Conse, Virtue). Currently, the frontend has agent selection UI, but the selected agents are not properly integrated into the debate flow.

## Glossary

- **Default Agent**: One of the three pre-configured agents (Deon, Conse, Virtue) with hardcoded system prompts
- **Custom Agent**: A user-created agent with AI-enhanced personality and system prompt stored in the database
- **Debate Flow**: The sequence of API calls that orchestrate opening arguments, counter-arguments, and final judgment
- **Agent Selector**: The frontend component that allows users to choose 3 agents for a debate
- **System Prompt**: The AI instruction text that defines an agent's personality and reasoning framework

## Requirements

### Requirement 1: Agent Selection Integration

**User Story:** As a user, I want to select any combination of default and custom agents for a debate, so that I can see how different ethical perspectives interact.

#### Acceptance Criteria

1. WHEN the user completes the dilemma form, THE System SHALL display an agent selection interface with all available agents
2. WHEN the user selects 3 agents (default or custom), THE System SHALL enable the "Start Debate" button
3. WHEN the user clicks "Start Debate", THE System SHALL pass the selected agent IDs to the backend
4. THE System SHALL prevent duplicate agent selection within the same debate
5. THE System SHALL require exactly 3 agents to be selected before allowing debate start

### Requirement 2: Backend Agent Endpoint Consistency

**User Story:** As a developer, I want a single, consistent API endpoint for fetching agent responses, so that the system handles default and custom agents uniformly.

#### Acceptance Criteria

1. THE Backend SHALL provide a single `/agent/{agent_id}` endpoint that handles both default and custom agents
2. WHEN the endpoint receives a default agent ID (deon, conse, virtue), THE Backend SHALL use the hardcoded system prompt
3. WHEN the endpoint receives a custom agent ID, THE Backend SHALL retrieve the agent's system prompt from storage
4. IF a custom agent ID is not found, THE Backend SHALL return a 404 error with a descriptive message
5. THE Backend SHALL increment the usage count for custom agents when they participate in debates

### Requirement 3: Dynamic Debate Orchestration

**User Story:** As a user, I want debates to work seamlessly with any combination of agents, so that I can explore diverse ethical perspectives.

#### Acceptance Criteria

1. WHEN a debate starts with selected agents, THE System SHALL call the `/agent/{agent_id}` endpoint for each selected agent
2. WHEN continuing to the next round, THE System SHALL use the same agents from the initial selection
3. WHEN the judge evaluates arguments, THE System SHALL consider all participating agents regardless of type
4. THE System SHALL maintain agent identity (name, avatar) throughout the debate
5. THE System SHALL display agent responses in the UI with correct names and avatars

### Requirement 4: Error Handling and Fallbacks

**User Story:** As a user, I want clear error messages if something goes wrong with agent selection, so that I can understand and resolve issues.

#### Acceptance Criteria

1. IF a custom agent is deleted while selected for a debate, THE System SHALL display an error message and prevent debate start
2. IF an agent fails to generate a response, THE System SHALL display a user-friendly error message
3. IF the backend is unreachable, THE System SHALL display a connection error and allow retry
4. THE System SHALL log detailed error information for debugging purposes
5. THE System SHALL gracefully handle partial failures (e.g., one agent fails but others succeed)

### Requirement 5: Data Consistency

**User Story:** As a developer, I want agent data to be consistent between frontend and backend, so that the system operates reliably.

#### Acceptance Criteria

1. THE Frontend SHALL use agent IDs (not names) when communicating with the backend
2. THE Backend SHALL return agent responses with consistent field names (agent, stance, argument)
3. WHEN displaying agents in the UI, THE System SHALL fetch the latest agent data from the backend
4. THE System SHALL handle agent name changes without breaking existing debates
5. THE System SHALL maintain backward compatibility with existing debate history

### Requirement 6: Performance and Scalability

**User Story:** As a user, I want debates with custom agents to be as fast as default agents, so that the experience is seamless.

#### Acceptance Criteria

1. THE System SHALL retrieve custom agent system prompts with minimal latency (< 100ms)
2. THE System SHALL cache agent data to avoid redundant database queries
3. WHEN multiple agents respond simultaneously, THE System SHALL handle concurrent requests efficiently
4. THE System SHALL limit the number of custom agents loaded in the selector to prevent UI lag
5. THE System SHALL paginate or lazy-load custom agents if the count exceeds 50

## Out of Scope

- Authentication and user-specific agent ownership (Phase 2)
- Agent performance analytics and ratings during debates
- Real-time collaborative debates with multiple users
- Agent learning or adaptation based on debate outcomes
- Voice or video representation of agents
