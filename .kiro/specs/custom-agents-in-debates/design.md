# Design Document

## Overview

This design enables seamless integration of custom agents into the debate system. The solution maintains backward compatibility with existing default agents while extending the architecture to support user-created agents with personalized ethical frameworks. The design focuses on minimal code changes, clear separation of concerns, and robust error handling.

## Architecture

### High-Level Flow

```
User Selects Agents → Agent Selector validates selection → 
Debate starts → Debate Engine identifies agent types → 
Retrieves appropriate system prompts → Generates responses → 
Displays in Debate View → Updates usage metrics
```

### Component Interaction

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ DilemmaForm  │→ │AgentSelector │→ │  DebateView  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                         ↓ POST /openings
                         ↓ POST /continue
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Debate Engine (main.py)                             │  │
│  │  - get_agent_system_prompt(agent_id) → str          │  │
│  │  - get_agent_display_name(agent_id) → str           │  │
│  │  - openings() - handles mixed agent teams           │  │
│  │  - continue_round() - maintains agent context       │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  AgentService                                        │  │
│  │  - get_agent(agent_id) → CustomAgent                │  │
│  │  - increment_usage(agent_id)                        │  │
│  │  - get_all_available_agents() → List[Dict]          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Storage (JSON)                           │
│  - custom_agents.json (agent data + system prompts)        │
│  - agent_ratings.json (usage counts + ratings)             │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Agent Selector (Frontend)

**Current State:**
- Loads default agents from hardcoded array
- Loads custom agents from `/api/agents`
- Displays agents in a modal picker
- Validates 3-agent selection

**Required Changes:**
- ✅ Already loads custom agents correctly
- ✅ Already prevents duplicate selection
- ✅ Already displays agent type badges
- **Minor Enhancement**: Add usage count display
- **Minor Enhancement**: Add sorting options

**Interface:**
```typescript
interface Agent {
  id: string;           // 'deon' | 'conse' | 'virtue' | UUID
  name: string;         // Display name
  avatar: string;       // Emoji
  description: string;  // Short description
  type: 'default' | 'custom';
  usage_count?: number; // For custom agents
  rating?: number;      // For custom agents
}

// Props
selectedAgents: string[];  // Array of 3 agent IDs
onSelectionChange: (agents: string[]) => void;
```

### 2. Dilemma Form (Frontend)

**Current State:**
- Manages 2-step wizard (dilemma → agent selection)
- Passes selected agent IDs to `onSubmit`
- Validates 3-agent selection

**Required Changes:**
- ✅ Already passes agent IDs correctly
- **No changes needed** - works with any agent IDs

**Interface:**
```typescript
onSubmit(dilemmaData: Dilemma, selectedAgentIds: string[]): void
```

### 3. App.jsx - Debate Initialization (Frontend)

**Current State:**
- Converts agent IDs to names ('deon' → 'Deon')
- Calls `/agent/{agentEndpoint}` for each agent
- Uses lowercase for default agents, ID for custom

**Required Changes:**
- ✅ Already handles custom agent IDs
- **Enhancement**: Better error handling for missing agents
- **Enhancement**: Show loading state per agent

**Current Implementation:**
```javascript
const agentNames = selectedAgentIds.map(id => {
  if (id === 'deon') return 'Deon';
  if (id === 'conse') return 'Conse'; 
  if (id === 'virtue') return 'Virtue';
  return id; // Custom agent ID
});

for (const agent of agentNames) {
  const agentEndpoint = ['Deon', 'Conse', 'Virtue'].includes(agent) 
    ? agent.toLowerCase() 
    : agent;
  
  const response = await fetch(`${API_URL}/agent/${agentEndpoint}`, {
    method: 'POST',
    body: JSON.stringify(dilemmaData),
  });
}
```

**Issue Identified**: This logic is fragile. Better approach:

```javascript
// Simplified approach - just pass the ID directly
for (const agentId of selectedAgentIds) {
  const response = await fetch(`${API_URL}/agent/${agentId}`, {
    method: 'POST',
    body: JSON.stringify(dilemmaData),
  });
  const turn = await response.json();
  // turn.agent will have the display name from backend
}
```

### 4. Debate View (Frontend)

**Current State:**
- Hardcoded agent info for Deon, Conse, Virtue
- Uses `getAgentInfo(agent)` to get avatar/gradient
- Displays agent name from turn data

**Required Changes:**
- **Critical**: Make `getAgentInfo()` dynamic
- **Critical**: Fetch agent data for custom agents
- **Enhancement**: Cache agent info to avoid repeated fetches

**Current Implementation:**
```javascript
const getAgentInfo = (agent) => {
  const info = {
    Deon: { name: 'Deon', role: 'Deontologist', icon: '⚖', gradient: '...' },
    Conse: { name: 'Conse', role: 'Consequentialist', icon: '◆', gradient: '...' },
    Virtue: { name: 'Virtue', role: 'Virtue Ethicist', icon: '✦', gradient: '...' },
  };
  return info[agent] || { name: agent, role: 'Agent', icon: '●', gradient: '...' };
};
```

**Proposed Solution:**
```javascript
const [agentInfoCache, setAgentInfoCache] = useState({});

useEffect(() => {
  // Extract unique agent names from transcript
  const agentNames = [...new Set(transcript.turns.map(t => t.agent))];
  
  // Fetch info for any agents not in cache
  agentNames.forEach(async (name) => {
    if (!agentInfoCache[name]) {
      const info = await fetchAgentInfo(name);
      setAgentInfoCache(prev => ({ ...prev, [name]: info }));
    }
  });
}, [transcript.turns]);

const getAgentInfo = (agentName) => {
  return agentInfoCache[agentName] || {
    name: agentName,
    role: 'Custom Agent',
    icon: '●',
    gradient: 'linear-gradient(135deg, #a8a8a8 0%, #6a6a6a 100%)'
  };
};
```

### 5. Backend - Debate Engine (main.py)

**Current State:**
- `get_agent_system_prompt(agent_name)` - ✅ Already implemented!
- `get_agent_display_name(agent_identifier)` - ✅ Already implemented!
- `/agent/{agent_name}` endpoint - ✅ Already exists!
- `/openings` endpoint - Uses hardcoded agents
- `/continue` endpoint - Extracts agents from transcript

**Required Changes:**

#### A. Update `/openings` endpoint

**Current:**
```python
@app.post("/openings")
def openings(d: Dilemma):
    return {"turns": [gen("Deon", DEON_SYS).dict(),
                      gen("Conse", CONSE_SYS).dict(),
                      gen("Virtue", VIRTUE_SYS).dict()]}
```

**Proposed:**
```python
class DebateRequest(BaseModel):
    dilemma: Dilemma
    agent_ids: List[str] = ["deon", "conse", "virtue"]

@app.post("/openings")
def openings(request: DebateRequest):
    turns = []
    for agent_id in request.agent_ids:
        sys_prompt = get_agent_system_prompt(agent_id)
        display_name = get_agent_display_name(agent_id)
        turn = gen(display_name, sys_prompt, request.dilemma)
        turns.append(turn.dict())
    return {"turns": turns}
```

#### B. Update `/continue` endpoint

**Current:**
```python
@app.post("/continue")
def continue_round(t: Transcript):
    # Extracts agents from transcript
    agent_names = list(set(turn.agent for turn in t.turns))
    
    # If default 3, use them
    if len(agent_names) == 3 and all(name in ["Deon", "Conse", "Virtue"] for name in agent_names):
        return {"turns": [respond("Deon").dict(),
                          respond("Conse").dict(),
                          respond("Virtue").dict()]}
    else:
        return {"turns": [respond(agent_name).dict() for agent_name in agent_names]}
```

**Issue**: This works but needs refinement for agent ID tracking

**Proposed Enhancement:**
```python
@app.post("/continue")
def continue_round(t: Transcript):
    # Extract unique agent names from transcript
    agent_names = list(set(turn.agent for turn in t.turns))
    
    turns = []
    for agent_name in agent_names:
        # Get system prompt (works for both default and custom)
        sys_prompt = get_agent_system_prompt(agent_name)
        turn = respond(agent_name, sys_prompt, t)
        turns.append(turn.dict())
    
    return {"turns": turns}
```

#### C. Update `respond()` function signature

**Current:**
```python
def respond(role: str, sys: str = None):
    if sys is None:
        sys = get_agent_system_prompt(role)
    # ... rest of logic
```

**This is already correct!** ✅

### 6. Backend - Agent Service

**Current State:**
- `get_agent(agent_id)` - ✅ Works
- `increment_usage(agent_id)` - ✅ Works
- `get_all_available_agents()` - ✅ Returns unified list

**Required Changes:**
- **Enhancement**: Add method to get agent info by name (not just ID)
- **Enhancement**: Cache frequently accessed agents

**New Method:**
```python
def get_agent_by_name(self, name: str) -> Optional[CustomAgent]:
    """Get agent by display name (for backward compatibility)"""
    agents = self._load_agents()
    for agent_data in agents.values():
        if agent_data.get('name') == name:
            return CustomAgent(**agent_data)
    return None
```

### 7. Backend - Usage Tracking

**Current State:**
- `increment_usage()` exists but not called during debates

**Required Changes:**
- Call `increment_usage()` when custom agent participates
- Track debate outcomes per agent
- Update average ratings based on judge scores

**Implementation:**
```python
# In get_agent_system_prompt()
def get_agent_system_prompt(agent_name: str) -> str:
    if agent_name.lower() in ["deon", "conse", "virtue"]:
        # Default agent
        return get_default_prompt(agent_name)
    else:
        # Custom agent
        agent = agent_service.get_agent(agent_name)
        if agent:
            agent_service.increment_usage(agent_name)  # Track usage
            return agent.system_prompt
        else:
            return fallback_prompt()
```

## Data Models

### Agent Identification Strategy

**Problem**: We need to handle both agent IDs (UUIDs) and agent names (display names)

**Solution**: Use a hybrid approach

1. **Frontend → Backend**: Always send agent IDs
2. **Backend Processing**: Convert IDs to names for display
3. **Backend → Frontend**: Return display names in responses
4. **Frontend Display**: Use names from response data

**Agent ID Mapping:**
```python
# Default agents: ID = lowercase name
'deon' → 'Deon'
'conse' → 'Conse'
'virtue' → 'Virtue'

# Custom agents: ID = UUID
'550e8400-e29b-41d4-a716-446655440000' → 'EcoWarrior'
```

### Transcript Structure

**Current:**
```json
{
  "dilemma": { "title": "...", "A": "...", "B": "...", "constraints": "..." },
  "turns": [
    { "agent": "Deon", "stance": "A", "argument": "..." },
    { "agent": "EcoWarrior", "stance": "B", "argument": "..." },
    { "agent": "Virtue", "stance": "A", "argument": "..." }
  ]
}
```

**Enhancement**: Add agent metadata
```json
{
  "dilemma": { ... },
  "agents": [
    { "id": "deon", "name": "Deon", "avatar": "⚖️", "type": "default" },
    { "id": "uuid-123", "name": "EcoWarrior", "avatar": "🌱", "type": "custom" },
    { "id": "virtue", "name": "Virtue", "avatar": "✦", "type": "default" }
  ],
  "turns": [ ... ]
}
```

**Benefit**: Frontend doesn't need to fetch agent data separately

## Error Handling

### Scenario 1: Custom Agent Deleted Mid-Debate

**Problem**: User views debate history, but agent was deleted

**Solution**:
```javascript
// Frontend
const getAgentInfo = async (agentName) => {
  try {
    const response = await fetch(`/api/agents/by-name/${agentName}`);
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.error('Failed to load agent:', error);
  }
  
  // Fallback for deleted agents
  return {
    name: agentName,
    avatar: '❓',
    role: 'Deleted Agent',
    gradient: 'linear-gradient(135deg, #999 0%, #666 100%)'
  };
};
```

### Scenario 2: Custom Agent Fails to Respond

**Problem**: Agent's system prompt generates invalid JSON

**Solution**: Already handled by `clamp_json()` and retry logic ✅

**Enhancement**: Add agent-specific error messages
```python
try:
    raw = call_ollama(sys_prompt, prompt)
    j = clamp_json(raw, fallback)
except Exception as e:
    return AgentTurn(
        agent=agent_name,
        stance="A",
        argument=f"[{agent_name} encountered an error and could not respond. Error: {str(e)[:100]}]"
    )
```

### Scenario 3: Agent Selector Fails to Load

**Problem**: Backend is down or agents endpoint fails

**Solution**:
```javascript
// AgentSelector.jsx
const loadAgents = async () => {
  try {
    const response = await fetch(`${API_URL}/api/agents`);
    if (response.ok) {
      const data = await response.json();
      setAvailableAgents([...defaultAgents, ...data.agents]);
    } else {
      throw new Error('Failed to load agents');
    }
  } catch (error) {
    console.error('Failed to load agents:', error);
    // Fallback to default agents only
    setAvailableAgents(defaultAgents);
    setError('Could not load custom agents. Showing default agents only.');
  } finally {
    setLoading(false);
  }
};
```

## Testing Strategy

### Unit Tests

1. **Backend - Agent Service**
   - Test `get_agent()` with valid/invalid IDs
   - Test `increment_usage()` updates count correctly
   - Test `get_all_available_agents()` returns both types

2. **Backend - Debate Engine**
   - Test `get_agent_system_prompt()` with default agents
   - Test `get_agent_system_prompt()` with custom agents
   - Test `get_agent_system_prompt()` with invalid IDs
   - Test `get_agent_display_name()` with all agent types

3. **Frontend - Agent Selector**
   - Test agent loading and display
   - Test duplicate prevention
   - Test 3-agent validation

### Integration Tests

1. **Full Debate Flow with Custom Agents**
   - Create custom agent
   - Select for debate
   - Start debate
   - Verify responses use custom system prompt
   - Verify usage count increments

2. **Mixed Agent Debate**
   - Select 2 default + 1 custom
   - Start debate
   - Verify all agents respond correctly
   - Verify turn order maintained

3. **Error Scenarios**
   - Start debate with deleted agent
   - Verify graceful fallback
   - Custom agent fails to respond
   - Verify error message displayed

### Manual Testing Checklist

- [ ] Create custom agent through builder
- [ ] Select custom agent in agent selector
- [ ] Start debate with 3 custom agents
- [ ] Start debate with mixed agents (1 default, 2 custom)
- [ ] Verify custom agent uses enhanced prompt
- [ ] Verify custom agent avatar displays correctly
- [ ] Continue debate for multiple rounds
- [ ] Verify agents address each other by name
- [ ] Get final judgment
- [ ] Verify usage count incremented
- [ ] View debate in history
- [ ] Delete custom agent
- [ ] View old debate with deleted agent
- [ ] Verify graceful degradation

## Performance Considerations

### Caching Strategy

1. **Frontend Agent Info Cache**
   - Cache agent data in component state
   - Refresh on agent creation/deletion
   - TTL: Session-based (cleared on page refresh)

2. **Backend System Prompt Cache**
   - Cache custom agent system prompts in memory
   - Invalidate on agent update
   - TTL: 5 minutes

### Database Queries

- Current: File-based JSON storage
- Performance: Acceptable for <1000 agents
- Future: Consider SQLite or PostgreSQL for >1000 agents

### API Response Times

- Agent list: <500ms (currently ~200ms)
- Agent detail: <100ms (file read)
- Debate initialization: <3s (3 agents × 1s each)

## Security Considerations

1. **Agent Name Validation**
   - Prevent SQL injection (not applicable with JSON)
   - Sanitize agent names for display
   - Limit name length (50 chars)

2. **System Prompt Injection**
   - Validate system prompts don't contain malicious instructions
   - Limit prompt length (currently handled by enhancement service)
   - Monitor for prompt injection attempts

3. **Rate Limiting**
   - Limit debate starts per user (future)
   - Limit agent creation per user (future)
   - Prevent abuse of AI endpoints

## Migration Strategy

### Phase 1: Backend Updates (No Breaking Changes)
1. Update `/openings` to accept agent_ids parameter (optional, defaults to default agents)
2. Ensure `get_agent_system_prompt()` works for all agent types
3. Add usage tracking to debate flow
4. Deploy backend

### Phase 2: Frontend Updates
1. Update `App.jsx` to pass agent IDs to backend
2. Update `DebateView` to handle custom agent display
3. Add agent info caching
4. Deploy frontend

### Phase 3: Testing & Refinement
1. Monitor error rates
2. Gather user feedback
3. Optimize performance
4. Add analytics

### Rollback Plan

If issues arise:
1. Frontend can revert to hardcoded default agents
2. Backend maintains backward compatibility
3. No data loss (agents stored separately)
