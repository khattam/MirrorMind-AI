# Custom Agents in Debates - Feature Spec

## Overview

This spec defines the integration of custom agents (created through the Agent Builder) into the live debate system. Currently, custom agents can be created but cannot participate in debates. This feature will enable users to select any combination of default and custom agents for their debate teams.

## Status

**Phase**: Planning  
**Priority**: High  
**Estimated Effort**: 3-5 days  
**Dependencies**: Custom Agent Builder (✅ Complete)

## Key Documents

1. **[requirements.md](./requirements.md)** - User stories and acceptance criteria using EARS format
2. **[design.md](./design.md)** - Technical design, architecture, and implementation details
3. **[tasks.md](./tasks.md)** - Step-by-step implementation tasks

## Quick Summary

### What's Being Built

- Custom agents can be selected in the Agent Selector alongside default agents
- Custom agents participate in debates using their enhanced system prompts
- Custom agent avatars and names display correctly in the Debate View
- Usage counts increment when custom agents participate in debates
- Mixed teams (default + custom agents) work seamlessly
- Error handling for deleted agents and failed responses

### Key Technical Changes

**Backend:**
- Update `/openings` endpoint to accept `agent_ids` parameter
- Implement usage tracking in debate flow
- Add `/api/agents/by-name/{name}` endpoint
- Enhance error handling for missing agents

**Frontend:**
- Simplify agent ID passing in `App.jsx`
- Add agent info caching in `DebateView`
- Display usage stats in `AgentSelector`
- Improve error messaging throughout

### What's Already Working

✅ Agent Selector loads custom agents  
✅ Backend has `get_agent_system_prompt()` function  
✅ Backend has `get_agent_display_name()` function  
✅ `/agent/{agent_id}` endpoint exists  
✅ Agent service has all CRUD operations  
✅ Usage count field exists in agent model  

### What Needs Implementation

❌ `/openings` endpoint doesn't accept agent_ids  
❌ Usage tracking not called during debates  
❌ DebateView hardcodes default agent info  
❌ No agent info caching in frontend  
❌ No usage stats displayed in selector  
❌ Limited error handling for missing agents  

## Implementation Approach

### Phase 1: Backend Foundation (Tasks 1-4)
- Update debate endpoints
- Add usage tracking
- Create agent info endpoint
- Enhance error handling

**Estimated Time**: 1-2 days  
**Risk**: Low - mostly extending existing code

### Phase 2: Frontend Integration (Tasks 5-7)
- Update debate initialization
- Make DebateView dynamic
- Add agent metadata handling

**Estimated Time**: 1-2 days  
**Risk**: Medium - requires careful state management

### Phase 3: Polish & Testing (Tasks 8-12)
- Add usage stats display
- Improve error messaging
- Integration testing
- Manual QA
- Documentation

**Estimated Time**: 1-2 days  
**Risk**: Low - refinement and validation

## Success Criteria

- [ ] User can select 3 custom agents and start a debate
- [ ] User can select mixed team (e.g., 1 default + 2 custom)
- [ ] Custom agents respond using their enhanced prompts
- [ ] Custom agent avatars display correctly in debate
- [ ] Usage count increments after each debate
- [ ] Deleted agents show placeholder in history
- [ ] No errors in console during normal operation
- [ ] All integration tests pass

## Known Limitations

1. **Agent Deletion**: Deleting an agent doesn't prevent it from appearing in old debates (by design - shows placeholder)
2. **Performance**: Loading 100+ custom agents may be slow (acceptable for MVP)
3. **Caching**: Agent info cache is session-based (cleared on refresh)
4. **Validation**: No validation that custom agent prompts produce good debate responses

## Future Enhancements

- Agent performance analytics (win rate, average scores)
- Agent recommendations based on dilemma type
- Agent versioning (track prompt changes over time)
- Community ratings and reviews
- Agent tournaments and leaderboards

## Questions & Decisions

### Q: Should we validate custom agent prompts before allowing them in debates?
**A**: No for MVP. Let users experiment. Add validation in future if quality issues arise.

### Q: How do we handle agent name conflicts?
**A**: Already handled - agent service prevents duplicate names during creation.

### Q: Should we cache agent system prompts in backend?
**A**: Yes, but implement in Phase 3 if performance issues arise. Current file-based approach is fast enough.

### Q: What happens if all 3 agents fail to respond?
**A**: Show error message and offer to restart with different agents. Implement in Task 4.

### Q: Should we track which agents debate together most often?
**A**: Good idea for future analytics, but not in this spec. Add to roadmap.

## Related Specs

- [Custom Agent Builder](../custom-agent-builder/) - ✅ Complete
- Agent Performance Analytics - 🔮 Future
- Community Agent Library - 🔮 Future

## Notes

- This spec was created after thorough codebase review
- Many pieces are already in place (good architecture!)
- Main work is connecting existing pieces
- Focus on robust error handling (agents can be deleted)
- Keep backward compatibility (default agents must still work)

---

**Last Updated**: 2025-10-29  
**Author**: AI Assistant  
**Reviewer**: User
