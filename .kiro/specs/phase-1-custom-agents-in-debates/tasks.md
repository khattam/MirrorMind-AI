# Implementation Plan: Custom Agents in Debates

## Task Overview

This plan breaks down the integration of custom agents into the debate system into discrete, testable tasks. Each task builds on previous work and can be verified independently.

---

## Backend Tasks

- [ ] 1. Fix duplicate endpoint definition
  - Remove duplicate `/agent/{agent_name}` endpoint at line 358-380
  - Keep the more complete version at line 408-430
  - Verify no other code references the removed endpoint
  - _Requirements: 2.1_

- [ ] 2. Update `/agent/{agent_id}` endpoint
- [ ] 2.1 Change parameter from `agent_name` to `agent_id`
  - Update function signature: `def get_agent_response(agent_id: str, dilemma: Dilemma)`
  - Normalize agent_id to lowercase for consistency
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 2.2 Add usage count increment for custom agents
  - Check if agent_id is not in ['deon', 'conse', 'virtue']
  - Call `agent_service.increment_usage(agent_id)` for custom agents
  - _Requirements: 2.5_

- [ ] 2.3 Improve error handling
  - Return 404 with descriptive message if custom agent not found
  - Return 500 with error details if AI generation fails
  - Log errors for debugging
  - _Requirements: 4.1, 4.2, 4.4_

- [ ] 3. Enhance `/continue` endpoint validation
- [ ] 3.1 Add agent existence validation
  - Extract agent IDs from transcript turns
  - For custom agents, verify they still exist in storage
  - Return 404 error if any agent is missing
  - _Requirements: 4.1, 5.4_

- [ ] 3.2 Improve error messages
  - Include agent name in error messages
  - Suggest user actions (e.g., "start new debate")
  - _Requirements: 4.1_

- [ ]* 4. Add backend tests
  - Test `get_agent_system_prompt()` with default agents
  - Test `get_agent_system_prompt()` with custom agents
  - Test `get_agent_system_prompt()` with non-existent agent
  - Test `/agent/{agent_id}` endpoint with valid default agent
  - Test `/agent/{agent_id}` endpoint with valid custom agent
  - Test `/agent/{agent_id}` endpoint with invalid agent ID
  - Test usage count increment for custom agents
  - _Requirements: 2.1, 2.2, 2.3, 2.5_

---

## Frontend Tasks

- [ ] 5. Update App.jsx - handleStartDebate()
- [ ] 5.1 Store selected agents in transcript
  - Add `selectedAgents` field to transcript state
  - Store the agent IDs array when debate starts
  - _Requirements: 3.2, 5.1_

- [ ] 5.2 Use agent IDs directly in API calls
  - Remove agent name conversion logic
  - Call `/agent/${agentId}` directly with the ID from selection
  - _Requirements: 3.1, 5.1_

- [ ] 5.3 Add error handling for agent responses
  - Catch and display HTTP errors (404, 500)
  - Show user-friendly error messages
  - Allow user to retry or reset
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 5.4 Handle partial failures gracefully
  - Continue with remaining agents if one fails
  - Show warning but don't abort entire debate
  - Log failed agents for debugging
  - _Requirements: 4.5_

- [ ] 6. Update App.jsx - handleContinue()
- [ ] 6.1 Use stored selectedAgents from transcript
  - Read `transcript.selectedAgents` instead of extracting from turns
  - Fallback to default agents if not present (backward compatibility)
  - _Requirements: 3.2, 5.5_

- [ ] 6.2 Add error handling for continue round
  - Handle 404 errors (agent deleted)
  - Handle 500 errors (AI generation failed)
  - Show appropriate error messages
  - _Requirements: 4.1, 4.2_

- [ ] 7. Update DebateView.jsx for dynamic agents
- [ ] 7.1 Enhance getAgentInfo() function
  - Keep default agent info (Deon, Conse, Virtue)
  - Add fallback for custom agents (generic icon, gradient)
  - Handle case-insensitive agent ID matching
  - _Requirements: 3.4_

- [ ] 7.2 Remove hardcoded agent list
  - Extract agent list from transcript turns dynamically
  - Ensure UI adapts to any number/type of agents
  - _Requirements: 3.1, 3.4_

- [ ]* 7.3 Add agent data fetching (optional enhancement)
  - Fetch custom agent details (avatar, description) from API
  - Cache agent data to avoid repeated calls
  - Display custom agent avatars and roles correctly
  - _Requirements: 3.4, 6.3_

- [ ] 8. Update DilemmaForm.jsx validation
- [ ] 8.1 Verify selected agents still exist
  - Before submitting, check if custom agents are still available
  - Show error if any selected agent was deleted
  - Allow user to reselect agents
  - _Requirements: 4.1_

- [ ] 8.2 Improve validation feedback
  - Show which agents are selected in each slot
  - Highlight if an agent is no longer available
  - _Requirements: 4.1_

- [ ]* 9. Add frontend tests
  - Test agent selection state management
  - Test agent ID passing to handleStartDebate()
  - Test error handling for missing agents
  - Test debate flow with default agents
  - Test debate flow with custom agents
  - Test debate flow with mixed agents
  - _Requirements: 3.1, 3.3, 4.1_

---

## Integration & Testing Tasks

- [ ] 10. End-to-end testing
- [ ] 10.1 Test with default agents only
  - Select Deon, Conse, Virtue
  - Complete full debate (opening → continue → judge)
  - Verify all responses display correctly
  - _Requirements: 3.1, 3.3, 3.4_

- [ ] 10.2 Test with custom agents only
  - Create 3 custom agents
  - Select all 3 custom agents
  - Complete full debate
  - Verify usage counts increment
  - _Requirements: 2.5, 3.1, 3.3_

- [ ] 10.3 Test with mixed agents
  - Select 1 default + 2 custom agents
  - Complete full debate
  - Verify all agents work together
  - _Requirements: 3.1, 3.3_

- [ ] 10.4 Test error scenarios
  - Delete a custom agent mid-debate
  - Verify error message displays
  - Verify user can recover (reset/retry)
  - _Requirements: 4.1, 4.2_

- [ ] 10.5 Test performance
  - Measure response time for custom agents
  - Verify it's comparable to default agents (< 100ms overhead)
  - _Requirements: 6.1_

- [ ]* 11. Documentation updates
  - Update README with custom agent debate instructions
  - Add troubleshooting section for common errors
  - Document agent ID format and conventions
  - _Requirements: 4.1_

---

## Deployment Tasks

- [ ] 12. Pre-deployment checks
- [ ] 12.1 Verify backward compatibility
  - Test that existing debates in history still work
  - Verify default agent debates work without changes
  - _Requirements: 5.5_

- [ ] 12.2 Database migration (if needed)
  - Check if any schema changes required
  - Create migration scripts if necessary
  - _Requirements: 5.2, 5.3_

- [ ] 13. Deployment
- [ ] 13.1 Deploy backend changes
  - Deploy to staging environment
  - Run smoke tests
  - Monitor for errors
  - _Requirements: All backend requirements_

- [ ] 13.2 Deploy frontend changes
  - Deploy to staging environment
  - Test with production backend
  - Monitor for errors
  - _Requirements: All frontend requirements_

- [ ] 13.3 Production deployment
  - Deploy backend to production
  - Deploy frontend to production
  - Monitor metrics and error logs
  - _Requirements: All requirements_

- [ ]* 14. Post-deployment monitoring
  - Monitor error rates for 24 hours
  - Check custom agent usage metrics
  - Verify no performance degradation
  - Collect user feedback
  - _Requirements: 6.1, 6.2_

---

## Notes

- Tasks marked with `*` are optional and can be skipped for MVP
- Each task should be completed and tested before moving to the next
- Backend tasks should be completed before frontend tasks for easier testing
- Integration testing should be done after all core tasks are complete
