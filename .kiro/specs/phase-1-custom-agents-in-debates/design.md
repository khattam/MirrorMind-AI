# Design Document: Custom Agents in Debates

## Overview

This design integrates custom agents into the existing debate system by fixing the disconnect between frontend agent selection and backend debate orchestration. The solution leverages existing infrastructure (agent storage, system prompts, API endpoints) and requires minimal changes to achieve full integration.

## Current State Analysis

### What Works
- ✅ Frontend has complete agent selection UI (AgentSelector component)
- ✅ Backend has agent storage and retrieval (AgentService)
- ✅ Backend has `/agent/{agent_id}` endpoint for individual agent responses
- ✅ Backend has helper functions (`get_agent_system_prompt`, `get_agent_display_name`)
- ✅ Frontend passes selected agents to `handleStartDebate()`

### What's Broken
- ❌ Backend has duplicate `/agent/{agent_name}` endpoint definitions (lines 358 and 408)
- ❌ Frontend calls `/agent/{agentEndpoint}` but endpoint expects agent_name not agent_id
- ❌ `/continue` endpoint works but frontend doesn't properly track selected agents
- ❌ No error handling for missing/deleted custom agents
- ❌ Agent usage count not incremented during debates

## Architecture

### Component Interaction Flow

```
┌─────────────────┐
│  DilemmaForm    │
│  - Step 1: Form │
│  - Step 2: Team │
└────────┬────────┘
         │ onSubmit(dilemma, [agent_ids])
         ↓
┌─────────────────┐
│    App.jsx      │
│ handleStartDebate│
└────────┬────────┘
         │ For each agent_id
         ↓
┌─────────────────┐
│  POST /agent/   │
│   {agent_id}    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ get_agent_      │
│ system_prompt() │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  call_ollama()  │
│  or call_groq() │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Return AgentTurn│
│ {agent, stance, │
│  argument}      │
└─────────────────┘
```

## Components and Interfaces

### Backend Changes

#### 1. Fix Duplicate Endpoint

**Problem:** `/agent/{agent_name}` is defined twice (lines 358 and 408)

**Solution:** Remove the first definition (line 358-380), keep the second one (line 408-430) which is more complete

#### 2. Update `/agent/{agent_id}` Endpoint

**Current:**
```python
@app.post("/agent/{agent_name}")
def get_agent_response(agent_name: str, dilemma: Dilemma):
    # Uses agent_name directly
```

**Updated:**
```python
@app.post("/agent/{agent_id}")
def get_agent_response(agent_id: str, dilemma: Dilemma):
    """Get response from any agent (default or custom) by ID"""
    # Normalize agent_id to lowercase for default agents
    agent_id_lower = agent_id.lower()
    
    # Get system prompt (handles both default and custom)
    sys_prompt = get_agent_system_prompt(agent_id_lower)
    
    # Get display name for response
    display_name = get_agent_display_name(agent_id_lower)
    
    # Increment usage for custom agents
    if agent_id_lower not in ['deon', 'conse', 'virtue']:
        agent_service.increment_usage(agent_id_lower)
    
    # Generate response...
```

#### 3. Update Helper Functions

**`get_agent_system_prompt(agent_id: str)`:**
- Already works correctly
- Handles default agents by name
- Fetches custom agents from storage
- Returns fallback if not found

**`get_agent_display_name(agent_id: str)`:**
- Already works correctly
- Returns capitalized name for default agents
- Returns custom agent name from storage

#### 4. Update `/continue` Endpoint

**Current:** Extracts agent names from transcript
**Keep:** This approach works well

**Enhancement:** Add validation to ensure agents still exist

```python
@app.post("/continue")
def continue_round(t: Transcript):
    # Get unique agent IDs from transcript
    agent_ids = list(set(turn.agent for turn in t.turns))
    
    # Validate agents still exist
    for agent_id in agent_ids:
        if agent_id.lower() not in ['deon', 'conse', 'virtue']:
            agent = agent_service.get_agent(agent_id)
            if not agent:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Agent '{agent_id}' not found. It may have been deleted."
                )
    
    # Continue with existing logic...
```

### Frontend Changes

#### 1. Update App.jsx - `handleStartDebate()`

**Current Issue:** Tries to convert agent IDs to names, causing confusion

**Solution:** Use agent IDs directly

```javascript
const handleStartDebate = async (dilemmaData, selectedAgentIds = ['deon', 'conse', 'virtue']) => {
  setDilemma(dilemmaData);
  setTranscript({
    dilemma: dilemmaData,
    turns: [],
    selectedAgents: selectedAgentIds // Store for later rounds
  });
  setRoundCount(0);
  setStage('debate');

  const turns = [];

  for (const agentId of selectedAgentIds) {
    setCurrentThinkingAgent(agentId);
    
    try {
      // Use agent ID directly in the endpoint
      const response = await fetch(`${API_URL}/agent/${agentId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dilemmaData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get agent response');
      }

      const turn = await response.json();
      turns.push(turn);
      
      setTranscript(prev => ({
        ...prev,
        turns: [...turns],
      }));
    } catch (error) {
      console.error(`Error fetching ${agentId}:`, error);
      alert(`Failed to get response from agent: ${error.message}`);
      // Continue with other agents or abort?
    }
  }

  setCurrentThinkingAgent(null);
};
```

#### 2. Update App.jsx - `handleContinue()`

**Current:** Extracts agents from transcript turns
**Issue:** Works but could be more explicit

**Solution:** Use stored selectedAgents from transcript

```javascript
const handleContinue = async () => {
  setRoundCount(roundCount + 1);
  
  // Use the originally selected agents
  const agentIds = transcript.selectedAgents || ['deon', 'conse', 'virtue'];
  const currentTurns = [...transcript.turns];

  for (const agentId of agentIds) {
    setCurrentThinkingAgent(agentId);
    
    try {
      const response = await fetch(`${API_URL}/continue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...transcript,
          turns: currentTurns,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to continue debate');
      }

      const data = await response.json();
      const agentTurn = data.turns.find(t => t.agent === agentId);
      
      if (agentTurn) {
        currentTurns.push(agentTurn);
        setTranscript(prev => ({
          ...prev,
          turns: [...currentTurns],
        }));
      }
    } catch (error) {
      console.error(`Error fetching ${agentId}:`, error);
      alert(`Failed to get response from agent: ${error.message}`);
    }
  }

  setCurrentThinkingAgent(null);
};
```

#### 3. Update DebateView.jsx - Dynamic Agent Info

**Current:** Hardcoded agent info for Deon, Conse, Virtue

**Solution:** Fetch agent info dynamically or pass as props

**Option A: Pass agent data from App.jsx**
```javascript
// In App.jsx
const [selectedAgentData, setSelectedAgentData] = useState([]);

// Fetch agent data when agents are selected
const fetchAgentData = async (agentIds) => {
  const agentData = await Promise.all(
    agentIds.map(async (id) => {
      if (['deon', 'conse', 'virtue'].includes(id.toLowerCase())) {
        return getDefaultAgentInfo(id);
      } else {
        const response = await fetch(`${API_URL}/api/agents/${id}`);
        const data = await response.json();
        return data.agent;
      }
    })
  );
  setSelectedAgentData(agentData);
};

// Pass to DebateView
<DebateView
  transcript={transcript}
  agentData={selectedAgentData}
  // ... other props
/>
```

**Option B: Fetch in DebateView (simpler)**
```javascript
// In DebateView.jsx
const getAgentInfo = (agentId) => {
  // Check if it's a default agent
  const defaultInfo = {
    deon: { name: 'Deon', role: 'Deontologist', icon: '⚖', gradient: '...' },
    conse: { name: 'Conse', role: 'Consequentialist', icon: '◆', gradient: '...' },
    virtue: { name: 'Virtue', role: 'Virtue Ethicist', icon: '✦', gradient: '...' },
  };
  
  if (defaultInfo[agentId.toLowerCase()]) {
    return defaultInfo[agentId.toLowerCase()];
  }
  
  // For custom agents, use data from transcript or fetch
  // (Could be optimized with caching)
  return {
    name: agentId,
    role: 'Custom Agent',
    icon: '🤖',
    gradient: 'linear-gradient(135deg, #a8a8a8 0%, #6a6a6a 100%)'
  };
};
```

## Data Models

### Transcript Model (Enhanced)

```typescript
interface Transcript {
  dilemma: Dilemma;
  turns: AgentTurn[];
  selectedAgents: string[]; // NEW: Store selected agent IDs
}
```

### AgentTurn Model (Unchanged)

```typescript
interface AgentTurn {
  agent: string;      // Agent display name
  stance: string;     // "A" or "B"
  argument: string;   // The argument text
}
```

## Error Handling

### Backend Errors

1. **Agent Not Found (404)**
   ```python
   if not agent:
       raise HTTPException(
           status_code=404,
           detail=f"Agent '{agent_id}' not found"
       )
   ```

2. **AI Generation Failure (500)**
   ```python
   try:
       raw = call_ollama(...)
   except Exception as e:
       raise HTTPException(
           status_code=500,
           detail=f"Failed to generate response: {str(e)}"
       )
   ```

### Frontend Error Handling

1. **Network Errors**
   ```javascript
   catch (error) {
     console.error('Network error:', error);
     alert('Failed to connect to server. Please check your connection.');
   }
   ```

2. **Agent Deleted Mid-Debate**
   ```javascript
   if (response.status === 404) {
     alert('One of the selected agents has been deleted. Please start a new debate.');
     handleReset();
   }
   ```

3. **Partial Failures**
   ```javascript
   // Continue with remaining agents if one fails
   // Show warning but don't abort entire debate
   ```

## Testing Strategy

### Unit Tests

1. **Backend:**
   - Test `get_agent_system_prompt()` with default and custom agents
   - Test `get_agent_display_name()` with various inputs
   - Test `/agent/{agent_id}` endpoint with valid/invalid IDs
   - Test usage count increment for custom agents

2. **Frontend:**
   - Test agent selection state management
   - Test agent ID passing to backend
   - Test error handling for missing agents

### Integration Tests

1. **Full Debate Flow:**
   - Start debate with 3 default agents
   - Start debate with 3 custom agents
   - Start debate with mixed agents (1 default, 2 custom)
   - Continue debate for multiple rounds
   - Complete debate with judgment

2. **Error Scenarios:**
   - Delete custom agent mid-debate
   - Network failure during agent response
   - Invalid agent ID in selection

### Manual Testing Checklist

- [ ] Select 3 default agents → debate works
- [ ] Select 3 custom agents → debate works
- [ ] Select mixed agents → debate works
- [ ] Agent avatars display correctly
- [ ] Agent names display correctly
- [ ] Continue button works with custom agents
- [ ] Judge evaluates custom agent arguments
- [ ] Usage count increments for custom agents
- [ ] Error message shows if agent deleted
- [ ] Debate history saves with custom agents

## Performance Considerations

1. **Agent Data Caching:**
   - Cache custom agent data in frontend to avoid repeated API calls
   - Invalidate cache when agents are updated

2. **Concurrent Requests:**
   - Backend already handles concurrent agent responses
   - Frontend could parallelize agent calls (currently sequential)

3. **Database Queries:**
   - Agent retrieval is already optimized (single file read)
   - Consider in-memory cache for frequently used agents

## Migration and Rollback

### Migration Steps

1. Deploy backend changes first (backward compatible)
2. Test backend with existing frontend
3. Deploy frontend changes
4. Monitor for errors in production

### Rollback Plan

1. Backend changes are backward compatible
2. If issues arise, revert frontend to previous version
3. Backend will continue to work with old frontend

## Open Questions

1. **Should we allow duplicate agents in a debate?**
   - Current: No, prevented by UI
   - Consideration: Could be interesting for testing

2. **How to handle agent name changes?**
   - Current: Use agent ID throughout
   - Impact: Minimal, display name fetched dynamically

3. **Should we cache agent data in frontend?**
   - Pro: Faster UI, fewer API calls
   - Con: Stale data if agent updated
   - Decision: Implement simple cache with manual refresh

4. **What if all 3 agents fail to respond?**
   - Current: Debate continues with partial data
   - Better: Show error and allow retry or reset
