# Implementation Plan

- [ ] 1. Backend - Update debate endpoints to support custom agents
  - Update `/openings` endpoint to accept agent_ids parameter with default value
  - Modify opening generation to use `get_agent_system_prompt()` for all agents
  - Ensure `get_agent_display_name()` is called for response formatting
  - Add error handling for invalid agent IDs
  - _Requirements: 1.2, 2.1, 2.2_

- [ ] 2. Backend - Implement usage tracking in debate flow
  - Call `agent_service.increment_usage()` when custom agent participates in debate
  - Add usage tracking to both `/openings` and `/continue` endpoints
  - Ensure usage count persists correctly to JSON storage
  - _Requirements: 2.5, 7.3_

- [ ] 3. Backend - Add agent info endpoint for frontend
  - Create `/api/agents/by-name/{name}` endpoint to get agent by display name
  - Return agent data including avatar, description, and type
  - Handle case where agent doesn't exist (return 404 with helpful message)
  - _Requirements: 3.5_

- [ ] 4. Backend - Enhance error handling for missing agents
  - Add try-catch blocks around agent retrieval in debate endpoints
  - Return meaningful error messages when agent not found
  - Implement fallback behavior for deleted agents in history
  - Log agent-related errors for debugging
  - _Requirements: 6.1, 6.2, 6.4_

- [ ] 5. Frontend - Update App.jsx debate initialization
  - Simplify agent ID passing logic (remove name conversion)
  - Pass agent IDs directly to backend in debate request
  - Add per-agent loading states during debate initialization
  - Improve error handling when agent fails to respond
  - _Requirements: 1.5, 6.4_

- [ ] 6. Frontend - Make DebateView support custom agents
  - Create `agentInfoCache` state to store agent metadata
  - Implement `fetchAgentInfo()` function to get agent data from backend
  - Update `getAgentInfo()` to use cache and fetch missing agents
  - Add useEffect to preload agent info when transcript changes
  - Handle deleted agents with placeholder info
  - _Requirements: 3.1, 3.2, 3.3, 3.5_

- [ ] 7. Frontend - Add agent metadata to debate requests
  - Update debate request payload to include agent metadata
  - Modify backend to return agent info in debate responses
  - Store agent metadata in transcript for history replay
  - _Requirements: 3.4, 4.5_

- [ ] 8. Frontend - Enhance AgentSelector with usage stats
  - Display usage count badge on custom agents
  - Add sorting options (usage, rating, name, date)
  - Show "Popular" badge for highly-used agents
  - Add tooltip showing agent stats on hover
  - _Requirements: 7.1, 7.2, 7.4_

- [ ] 9. Frontend - Improve error messaging
  - Add error state to AgentSelector for failed agent loads
  - Show user-friendly message when custom agent fails in debate
  - Add retry button for failed agent responses
  - Display warning when selecting recently created agents
  - _Requirements: 6.4_

- [ ] 10. Testing - Create integration tests
  - Test debate with 3 custom agents
  - Test debate with mixed agents (1 default, 2 custom)
  - Test debate with deleted agent (history view)
  - Test agent usage count increments correctly
  - Test error handling when agent fails to respond
  - _Requirements: All_

- [ ] 11. Testing - Manual QA checklist
  - Create custom agent and verify it appears in selector
  - Start debate with custom agents and verify correct prompts used
  - Verify custom agent avatars display in debate view
  - Continue debate for multiple rounds with custom agents
  - Verify agents address each other by name correctly
  - Check usage count increments after debate
  - Delete agent and verify old debates still viewable
  - Test with slow network to verify loading states
  - _Requirements: All_

- [ ] 12. Documentation - Update README and docs
  - Add section on using custom agents in debates
  - Update architecture diagrams to show custom agent flow
  - Document agent ID vs name conventions
  - Add troubleshooting guide for common issues
  - _Requirements: N/A_
