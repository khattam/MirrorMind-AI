# MirrorMind AI - Feature Architecture Diagrams

**Complete architecture and data flow diagrams based on actual code implementation**

---

## Table of Contents

1. [AI Debate Arena](#1-ai-debate-arena)
2. [Custom Agent Builder](#2-custom-agent-builder)
3. [Debate Library & Deduplication](#3-debate-library--deduplication)
4. [Judge System](#4-judge-system)
5. [Analytics Dashboard](#5-analytics-dashboard)
6. [Debate History & Replay](#6-debate-history--replay)
7. [PDF Export](#7-pdf-export)

---

## 1. AI Debate Arena

### 1.1 Component Architecture (Frontend)

```mermaid
graph TD
    App[App.jsx<br/>Main State: stage, dilemma, transcript, verdict]
    
    App -->|renders| DilemmaForm[DilemmaForm.jsx<br/>2-Step Wizard]
    App -->|renders| DebateView[DebateView.jsx<br/>Live Debate Display]
    
    DilemmaForm -->|Step 1| Step1[Dilemma Input<br/>title, context, options A & B]
    DilemmaForm -->|Step 2| Step2[Agent Selection<br/>Choose 3 agents]
    
    Step2 -->|uses| AgentSelector[AgentSelector.jsx<br/>3-Slot Team Builder]
    AgentSelector -->|opens| AgentPicker[Agent Picker Modal<br/>Default + Custom agents]
    AgentPicker -->|loads| LoadAgents[GET /api/agents]
    
    Step1 -->|optional| DebateLibrary[DebateLibrary Modal<br/>34+ templates]
    
    DilemmaForm -->|onSubmit| HandleStart[handleStartDebate]
    HandleStart -->|updates| App
    
    DebateView -->|displays| DilemmaCard[Dilemma Card<br/>Title + Options A/B]
    DebateView -->|displays| Rounds[Rounds Container<br/>Collapsible rounds]
    Rounds -->|contains| AgentCards[Agent Cards x3<br/>Avatar, stance, argument]
    AgentCards -->|uses| Typewriter[TypewriterText.jsx<br/>Animated text]
    
    DebateView -->|displays| Controls[Action Buttons]
    Controls -->|onClick| HandleContinue[handleContinue]
    Controls -->|onClick| HandleJudge[handleJudge]
    HandleContinue -->|updates| App
    HandleJudge -->|updates| App
```

**Clean Component Flow:**
- App.jsx manages all state and renders DilemmaForm or DebateView based on stage
- DilemmaForm is a 2-step wizard: dilemma input → agent selection
- AgentSelector loads agents and provides 3-slot team builder
- DebateView displays rounds with agent cards using TypewriterText for animation
- All actions flow back to App.jsx to update state

### 1.2 System Architecture (Full Stack)

```mermaid
graph TB
    subgraph User["User Interface"]
        DilemmaForm[Dilemma Form<br/>Title, Context, Options]
        AgentSelect[Agent Selector<br/>3 agents required]
        DebateDisplay[Debate Display<br/>Real-time updates]
    end
    
    subgraph Frontend["Frontend Logic"]
        StateManager[State Manager<br/>transcript, stage, agents]
        APIClient[API Client<br/>Fetch requests]
        TypewriterEffect[Typewriter Effect<br/>Animated text]
    end
    
    subgraph Backend["Backend API"]
        OpeningsEndpoint[POST /openings<br/>Generate opening args]
        ContinueEndpoint[POST /continue<br/>Generate rebuttals]
        JudgeEndpoint[POST /judge<br/>Get verdict]
    end
    
    subgraph AILayer["AI Processing"]
        GroqAPI[Groq API<br/>Llama 3.3 70B]
        PromptEngine[Prompt Engineering<br/>System + User prompts]
        JSONParser[JSON Parser<br/>3-level fallback]
    end
    
    subgraph Services["Backend Services"]
        AgentService[Agent Service<br/>Get system prompts]
        MetricsService[Metrics Service<br/>Record stats]
        HistoryService[History Service<br/>Save debates]
    end

    
    DilemmaForm --> StateManager
    AgentSelect --> StateManager
    StateManager --> APIClient
    APIClient --> OpeningsEndpoint
    APIClient --> ContinueEndpoint
    APIClient --> JudgeEndpoint
    
    OpeningsEndpoint --> AgentService
    OpeningsEndpoint --> PromptEngine
    ContinueEndpoint --> AgentService
    ContinueEndpoint --> PromptEngine
    JudgeEndpoint --> PromptEngine
    
    PromptEngine --> GroqAPI
    GroqAPI --> JSONParser
    JSONParser --> StateManager
    StateManager --> DebateDisplay
    DebateDisplay --> TypewriterEffect
    
    JudgeEndpoint --> MetricsService
    JudgeEndpoint --> HistoryService
```

### 1.2 Data Flow - Opening Arguments (ACTUAL CODE)

```mermaid
sequenceDiagram
    participant User
    participant DilemmaForm
    participant App
    participant Backend
    participant AgentService
    participant Groq
    participant ClampJSON
    
    User->>DilemmaForm: Fill dilemma + select 3 agents
    DilemmaForm->>DilemmaForm: Validate Step 1 and Step 2
    DilemmaForm->>App: onSubmit(formData, agentIds, agentsInfo)
    
    App->>App: setDilemma, setStage('debate')
    App->>App: checkAndAddToLibrary (background)
    
    Note over App: Convert agent IDs to names:<br/>deon→Deon, conse→Conse, virtue→Virtue<br/>custom agents use ID directly
    
    loop For each agent in agentNames
        App->>App: setCurrentThinkingAgent(agent)
        
        App->>App: Determine agentEndpoint:<br/>Default agents: lowercase<br/>Custom agents: ID
        
        App->>Backend: POST /agent/{agentEndpoint}<br/>{title, A, B, constraints}
        
        Backend->>Backend: get_agent_system_prompt(agent_name)
        
        alt Default agent (deon/conse/virtue)
            Backend->>Backend: Return DEON_SYS/CONSE_SYS/VIRTUE_SYS
        else Custom agent
            Backend->>AgentService: get_agent(agent_id)
            AgentService-->>Backend: agent.system_prompt
            Backend->>AgentService: increment_usage(agent_id)
        end
        
        Backend->>Backend: mk_base(dilemma) + OPENING_INSTRUCT
        Backend->>Groq: call_ollama(sys_prompt, user_prompt)
        Note over Groq: Temperature: 0.65<br/>Max tokens: 150<br/>Top-p: 0.9
        Groq-->>Backend: Raw LLM response
        
        Backend->>ClampJSON: clamp_json(raw, fallback)
        ClampJSON->>ClampJSON: 1. Try ```json...``` fenced block
        ClampJSON->>ClampJSON: 2. Try parse entire text as JSON
        ClampJSON->>ClampJSON: 3. Scan for {...} objects
        ClampJSON->>ClampJSON: 4. Regex extract stance + argument
        ClampJSON-->>Backend: {stance: "A|B", argument: "text"}
        
        alt Parsing failed or argument is "—"
            Backend->>Groq: Retry with temp 0.8, max_tokens 150
            Groq-->>Backend: Second attempt
            Backend->>ClampJSON: Parse again
        end
        
        Backend-->>App: AgentTurn {agent, stance, argument}
        App->>App: turns.push(turn)
        App->>App: setTranscript({dilemma, turns: [...turns]})
        App->>App: Update DebateView (triggers re-render)
    end
    
    App->>App: setCurrentThinkingAgent(null)
    Note over App: DebateView shows "Continue Debate" button
```

**Actual Opening Arguments Flow:**
1. User completes 2-step wizard in DilemmaForm
2. DilemmaForm calls `onSubmit(formData, agentIds, agentsInfo)`
3. App.jsx `handleStartDebate()`:
   - Sets dilemma and stage to 'debate'
   - Calls `checkAndAddToLibrary()` in background
   - Converts agent IDs: default agents to lowercase, custom agents keep ID
4. **Loops through each agent sequentially:**
   - Sets `currentThinkingAgent` (shows spinner)
   - Determines endpoint: `deon`→`/agent/deon`, custom→`/agent/{uuid}`
   - POST to `/agent/{agentEndpoint}` with dilemma
5. Backend `single_agent()`:
   - Calls `get_agent_system_prompt()` (returns default or custom prompt)
   - For custom agents: increments usage count
   - Builds prompt: `mk_base(dilemma) + OPENING_INSTRUCT`
   - Calls Groq via `call_ollama()` (temp 0.65, max_tokens 150)
6. Response parsing via `clamp_json()` (4-level fallback)
7. If parsing fails, retry with temp 0.8
8. Returns `AgentTurn {agent, stance, argument}`
9. App appends to turns array and updates transcript
10. DebateView re-renders with TypewriterText animation
```
            Groq-->>API: Second attempt
            API->>JSONParser: Parse again
        end
        API-->>Frontend: AgentTurn object
        Frontend->>Frontend: Append to transcript
        Frontend->>User: Display with typewriter effect
```

### 1.3 Data Flow - Rebuttal Round

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Groq
    participant Validator
    
    User->>Frontend: Click "Continue Debate"
    Frontend->>API: POST /continue {transcript}
    
    loop For each agent (sequential)
        API->>API: Build opponent summary
        Note over API: Extract latest arguments<br/>from other agents
        API->>API: Create rebuttal prompt
        Note over API: "Respond to [opponent]<br/>Start with their name"
        API->>Groq: Generate rebuttal
        Groq-->>API: Raw response
        API->>Validator: has_valid_opponent(text, agent, all_agents)
        Validator->>Validator: Check opponent name mentioned
        Validator->>Validator: Check length > 30 chars
        alt Invalid - no opponent mentioned
            API->>API: Build stricter retry prompt
            API->>Groq: Retry with explicit opponent
            Groq-->>API: Second attempt
        end
        API->>API: Parse JSON {stance, argument}
        API->>API: Maintain or update stance
        API-->>Frontend: AgentTurn
        Frontend->>Frontend: Append to transcript
        Frontend->>User: Display new turn
    end
    
    Frontend->>User: Show "Get Verdict" button
```

### 1.4 Component Architecture

```mermaid
graph LR
    subgraph DebateView["DebateView.jsx"]
        Props[Props<br/>transcript, roundCount,<br/>currentThinkingAgent]
        DilemmaDisplay[Dilemma Display<br/>Title, context, options]
        TurnsList[Turns List<br/>Map over transcript.turns]
        ThinkingIndicator[Thinking Indicator<br/>Agent avatar + spinner]
        ActionButtons[Action Buttons<br/>Continue, Judge, Reset]
    end
    
    subgraph TurnComponent["Turn Component"]
        AgentInfo[Agent Info<br/>Avatar, name, stance]
        ArgumentText[Argument Text<br/>Typewriter effect]
        StanceBadge[Stance Badge<br/>A or B indicator]
    end
    
    Props --> DilemmaDisplay
    Props --> TurnsList
    Props --> ThinkingIndicator
    Props --> ActionButtons
    
    TurnsList --> TurnComponent
    TurnComponent --> AgentInfo
    TurnComponent --> ArgumentText
    TurnComponent --> StanceBadge
```

---

## 2. Custom Agent Builder

### 2.1 System Architecture

```mermaid
graph TD
    User[User Input<br/>Name, Avatar, Description]
    
    User -->|Step 1-3| AgentBuilder[AgentBuilder Component<br/>3-step form]
    AgentBuilder -->|validates| Validation[Validation<br/>50-1000 chars, unique name]
    Validation -->|Click Enhance| API[POST /api/agents/create]
    
    API -->|calls| EnhancementService[EnhancementService]
    EnhancementService -->|analyzes| Analyzer[PromptAnalyzer<br/>Score 4 dimensions]
    EnhancementService -->|enhances| GPT4o[OpenAI GPT-4o<br/>Expand to 4-5 sentences]
    
    GPT4o -->|returns| Enhanced[Enhanced Framework]
    Enhanced -->|generates| SystemPrompt[System Prompt Generator<br/>Debate-ready format]
    
    SystemPrompt -->|saves| AgentService[AgentService]
    AgentService -->|writes| Storage[custom_agents.json]
    
    Storage -->|returns| Response[Agent + Quality Scores]
    Response -->|displays| AgentBuilder
```

**Clean Flow:**
- User fills 3-step form (name, avatar, description)
- Frontend validates inputs
- Backend calls EnhancementService
- PromptAnalyzer scores quality (4 dimensions)
- GPT-4o expands description to 4-5 sentences
- System prompt generated for debates
- AgentService saves to JSON with atomic write
- Quality scores displayed to user
```

### 2.2 Data Flow - Agent Creation

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant EnhancementService
    participant PromptAnalyzer
    participant GPT4o
    participant AgentService
    participant Storage
    
    User->>Frontend: Enter name, avatar, description
    Frontend->>Frontend: Validate inputs (50-1000 chars)
    User->>Frontend: Click "Enhance with AI"
    Frontend->>API: POST /api/agents/create
    
    API->>EnhancementService: enhance_agent_description(desc, name)
    
    EnhancementService->>PromptAnalyzer: analyze_description(desc)
    PromptAnalyzer->>PromptAnalyzer: _score_clarity()
    PromptAnalyzer->>PromptAnalyzer: _score_completeness()
    PromptAnalyzer->>PromptAnalyzer: _score_specificity()
    PromptAnalyzer->>PromptAnalyzer: _score_consistency()
    PromptAnalyzer-->>EnhancementService: {scores: 0-10 each}
    
    EnhancementService->>EnhancementService: Build enhancement prompt
    Note over EnhancementService: "Agent Name: {name}<br/>Description: {desc}<br/>Expand into 4-5 sentences..."
    
    EnhancementService->>GPT4o: Generate enhancement
    Note over GPT4o: Temperature: 0.7<br/>Max tokens: 500<br/>System: ENHANCER_SYSTEM_PROMPT
    GPT4o-->>EnhancementService: Enhanced 4-5 sentence framework
    
    EnhancementService->>EnhancementService: Quality check
    alt Quality check fails (length < 50 or missing name)
        EnhancementService->>GPT4o: Retry with stricter prompt
        GPT4o-->>EnhancementService: Second attempt
    end
    
    EnhancementService->>EnhancementService: _identify_improvements()
    EnhancementService->>EnhancementService: generate_system_prompt()
    Note over EnhancementService: "You are {name}, {enhanced}.<br/>Respond to opponents by name.<br/>JSON only."
    
    EnhancementService-->>API: EnhancementRequest
    
    API->>AgentService: create_agent(request, enhanced, system_prompt)
    AgentService->>AgentService: _check_duplicate_name()
    AgentService->>AgentService: Generate UUID
    AgentService->>Storage: Atomic write to custom_agents.json
    Storage-->>AgentService: Success
    AgentService-->>API: CustomAgent
    
    API-->>Frontend: {agent, enhancement}
    Frontend->>Frontend: Display quality scores
    Frontend->>Frontend: Show enhanced framework
    Frontend->>User: "Agent created successfully!"
```


### 2.3 Quality Scoring Algorithm

```mermaid
graph TD
    Description[User Description] --> Analyzer[Prompt Analyzer]
    
    Analyzer --> Clarity[Clarity Score 0-10]
    Analyzer --> Completeness[Completeness Score 0-10]
    Analyzer --> Specificity[Specificity Score 0-10]
    Analyzer --> Consistency[Consistency Score 0-10]
    
    Clarity --> ClarityLogic[Sentence length analysis<br/>Optimal: 15-20 words<br/>Penalize too long/short]
    
    Completeness --> CompletenessLogic[Check for elements:<br/>✓ Values/beliefs<br/>✓ Reasoning<br/>✓ Examples<br/>✓ Personality<br/>✓ Decision-making<br/>Score = present/5 * 10]
    
    Specificity --> SpecificityLogic[Count vague terms:<br/>good, bad, very, always<br/>Count specific terms:<br/>exactly, precisely, namely<br/>Penalize vague ratio]
    
    Consistency --> ConsistencyLogic[Detect contradictions:<br/>always vs sometimes<br/>strict vs flexible<br/>emotional vs logical<br/>-2 points per contradiction]
    
    ClarityLogic --> OverallScore[Overall Quality<br/>Average of 4 scores]
    CompletenessLogic --> OverallScore
    SpecificityLogic --> OverallScore
    ConsistencyLogic --> OverallScore
    
    OverallScore --> Display[Display to User<br/>Color-coded:<br/><60% red<br/>60-80% yellow<br/>>80% green]
```

---

## 3. Debate Library & Deduplication

### 3.1 Frontend Architecture

```mermaid
graph TD
    User[User Creates Custom Debate]
    
    User -->|fills form| DilemmaForm[DilemmaForm<br/>title, constraints, A, B]
    DilemmaForm -->|or browses| TemplateLibrary[Template Library Modal<br/>34+ pre-made debates]
    
    DilemmaForm -->|handleStartDebate| App[App.jsx]
    App -->|IMMEDIATELY calls| CheckDuplicate[checkAndAddToLibrary]
    
    CheckDuplicate -->|builds submission| Submission[title, context, option_a, option_b]
    Submission -->|POST fetch| API[API_URL/api/debates/submit]
    
    API -->|returns result| Response{result.success?}
    Response -->|result.added_template| SuccessNotif[setNotification success<br/>✓ Debate added to library!]
    Response -->|result.is_duplicate| DuplicateNotif[setNotification info<br/>ℹ Already exists in library]
    
    SuccessNotif -->|setTimeout 4000ms| ClearNotif[setNotification null]
    DuplicateNotif -->|setTimeout 4000ms| ClearNotif
```

**Actual Frontend Flow:**
1. User fills DilemmaForm (title, constraints, A, B)
2. On submit → `handleStartDebate()` in App.jsx
3. **IMMEDIATELY** calls `checkAndAddToLibrary(dilemmaData)` in background
4. Builds submission object: `{title, context: constraints, option_a: A, option_b: B}`
5. POST to `/api/debates/submit`
6. If `result.success && result.added_template` → success toast
7. If `result.is_duplicate` → info toast
8. Toast auto-clears after 4 seconds

### 3.2 Backend Architecture

```mermaid
graph TD
    API[POST /api/debates/submit]
    
    API -->|calls| Service[DebateDeduplicationService<br/>submit_custom_debate]
    Service -->|validates| Fields{Has title, context,<br/>option_a, option_b?}
    
    Fields -->|No| Error[Return error:<br/>Missing required fields]
    Fields -->|Yes| FindDup[find_duplicate]
    
    FindDup -->|loads| Templates[_load_templates<br/>from JSON]
    Templates -->|empty?| CheckEmpty{templates.length > 0?}
    CheckEmpty -->|No| AddNew[add_to_library]
    
    CheckEmpty -->|Yes| GenEmbed[generate_debate_embedding<br/>candidate]
    GenEmbed -->|creates| CandidateVec[384-dim vector<br/>word + char n-grams]
    
    CandidateVec -->|loop templates| CompareLoop[For each template]
    CompareLoop -->|generate| TemplateEmbed[template embedding]
    CompareLoop -->|compute| Similarity[cosine_similarity]
    
    Similarity -->|track| BestMatch[best_match, best_similarity]
    BestMatch -->|check| Threshold{similarity >= 0.95?}
    
    Threshold -->|Yes| ReturnDup[Return DeduplicationResult<br/>is_duplicate=True]
    Threshold -->|No| AddNew
    
    AddNew -->|generate| NewID[max_id + 1]
    AddNew -->|generate| Slug[_generate_slug from title]
    AddNew -->|create| Template[New template object]
    Template -->|atomic write| Save[_save_templates<br/>temp file + rename]
    
    Save -->|return| ReturnSuccess[Return DeduplicationResult<br/>success=True, added_template]
```

**Actual Backend Flow:**
1. Receives POST with `{title, context, option_a, option_b}`
2. `DebateDeduplicationService.submit_custom_debate()` validates fields
3. Calls `find_duplicate()`:
   - Loads all templates from JSON
   - Generates 384-dim embedding for candidate (hash-based: word + char n-grams)
   - Loops through ALL templates
   - Generates embedding for each template
   - Computes cosine similarity
   - Tracks best match
4. If `best_similarity >= 0.95` → duplicate found, return it
5. If `best_similarity < 0.95` → unique debate:
   - Generate new ID (max existing ID + 1)
   - Generate slug from title
   - Create template object with `is_custom: true`
   - Atomic write (temp file → rename)
6. Return `DeduplicationResult` with success/duplicate status
```


```mermaid
graph TB
    subgraph Frontend["React Frontend"]
        User[User Input]
        DilemmaForm[DilemmaForm<br/>2-step wizard]
        AgentSelector[AgentSelector<br/>3-slot team builder]
        DebateView[DebateView<br/>Real-time display]
        APIClient[Fetch API Client]
    end
    
    subgraph Backend["FastAPI Backend - main.py"]
        OpeningsEndpoint["POST /openings<br/>Generate opening arguments"]
        ContinueEndpoint["POST /continue<br/>Generate rebuttals"]
        SingleAgentEndpoint["POST /agent/{agent_name}<br/>Single agent response"]
        GetAgentPrompt["get_agent_system_prompt()<br/>Retrieve system prompt"]
    end
    
    subgraph AIProcessing["AI Processing Layer"]
        CallOllama["call_ollama()<br/>Groq API wrapper"]
        GroqAPI["Groq API<br/>Llama 3.3 70B"]
        ClampJSON["clamp_json()<br/>3-level JSON parser"]
        ValidateOpponent["has_valid_opponent()<br/>Rebuttal validation"]
    end
    
    subgraph Services["Service Layer"]
        AgentService["AgentService<br/>get_agent(), get_agent_by_name()"]
        AgentsJSON["custom_agents.json<br/>Custom agent storage"]
    end
    
    User --> DilemmaForm
    DilemmaForm --> AgentSelector
    AgentSelector --> APIClient
    APIClient --> OpeningsEndpoint
    
    OpeningsEndpoint --> GetAgentPrompt
    GetAgentPrompt --> AgentService
    AgentService --> AgentsJSON
    
    OpeningsEndpoint --> CallOllama
    CallOllama --> GroqAPI
    GroqAPI --> ClampJSON
    ClampJSON --> DebateView
    
    DebateView --> ContinueEndpoint
    ContinueEndpoint --> GetAgentPrompt
    ContinueEndpoint --> CallOllama
    CallOllama --> ValidateOpponent
    ValidateOpponent --> DebateView
```

### 1.3 Data Flow - Opening Arguments (ACTUAL CODE)

```mermaid
sequenceDiagram
    participant User
    participant DilemmaForm
    participant App
    participant Backend
    participant AgentService
    participant Groq
    participant ClampJSON
    participant DebateView
    
    User->>DilemmaForm: Fill dilemma (Step 1)
    User->>DilemmaForm: Select 3 agents (Step 2)
    DilemmaForm->>DilemmaForm: validateStep1(), validate 3 agents
    DilemmaForm->>DilemmaForm: Build agentsInfo map
    DilemmaForm->>App: onSubmit(formData, agentIds, agentsInfo)
    
    App->>App: setDilemma, setSelectedAgentsInfo
    App->>App: setStage('debate')
    App->>App: checkAndAddToLibrary() [background]
    
    loop For each agent in agentNames
        App->>App: setCurrentThinkingAgent(agent)
        App->>Backend: POST /agent/{agentEndpoint}
        Note over Backend: agentEndpoint = lowercase for default<br/>or ID for custom
        
        Backend->>Backend: get_agent_system_prompt(agent_name)
        alt Default agent (deon/conse/virtue)
            Backend->>Backend: Return DEON_SYS/CONSE_SYS/VIRTUE_SYS
        else Custom agent
            Backend->>AgentService: get_agent(agent_id)
            AgentService->>Backend: agent.system_prompt
            Backend->>AgentService: increment_usage(agent_id)
        end
        
        Backend->>Backend: mk_base(dilemma) + OPENING_INSTRUCT
        Backend->>Groq: call_ollama(sys_prompt, user_prompt)
        Note over Groq: Temperature: 0.65<br/>Max tokens: 150-200<br/>Top-p: 0.9
        Groq-->>Backend: Raw LLM response
        
        Backend->>ClampJSON: clamp_json(raw, fallback)
        ClampJSON->>ClampJSON: 1. Try ```json...``` fenced block
        ClampJSON->>ClampJSON: 2. Try parse entire text as JSON
        ClampJSON->>ClampJSON: 3. Scan for {...} objects
        ClampJSON->>ClampJSON: 4. Regex extract stance + argument
        ClampJSON-->>Backend: {stance: "A|B", argument: "text"}
        
        alt Parsing failed or argument is "—"
            Backend->>Groq: Retry with temp 0.8
            Groq-->>Backend: Second attempt
            Backend->>ClampJSON: Parse again
        end
        
        Backend-->>App: AgentTurn {agent, stance, argument}
        App->>App: turns.push(turn)
        App->>App: setTranscript({dilemma, turns})
        App->>DebateView: Update transcript prop
        DebateView->>DebateView: TypewriterText animation
    end
    
    App->>App: setCurrentThinkingAgent(null)
    DebateView->>User: Show "Continue Debate" button
```
