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
graph TB
    subgraph App["App.jsx - Main State"]
        AppState[State:<br/>stage, dilemma, transcript,<br/>verdict, selectedAgentsInfo]
        handleStartDebate[handleStartDebate<br/>dilemma, agentIds, agentsInfo]
        handleContinue[handleContinue]
        handleJudge[handleJudge]
    end
    
    subgraph DilemmaForm["DilemmaForm.jsx - 2-Step Wizard"]
        Step1[Step 1: Dilemma<br/>title, A, B, constraints]
        Step2[Step 2: Agent Selection<br/>3 agents required]
        FormState[State: formData,<br/>selectedAgents, availableAgentsMap]
        DebateLibrary[DebateLibrary Modal<br/>34+ templates]
    end
    
    subgraph AgentSelector["AgentSelector.jsx"]
        TeamBuilder[3-Slot Team Builder<br/>Agent 1, 2, 3]
        AgentPicker[Agent Picker Modal<br/>Default + Custom agents]
        LoadAgents[loadAgents<br/>GET /api/agents]
    end
    
    subgraph DebateView["DebateView.jsx"]
        DilemmaDisplay[Dilemma Display<br/>Title + Options A/B]
        RoundsContainer[Rounds Container<br/>Collapsible rounds]
        AgentsPanel[Agents Panel<br/>3 agent cards]
        TypewriterEffect[TypewriterText Component<br/>Animated arguments]
        StageControls[Stage Controls<br/>Continue, Judge, Reset]
    end
    
    App --> DilemmaForm
    DilemmaForm --> Step1
    Step1 --> Step2
    Step2 --> AgentSelector
    AgentSelector --> TeamBuilder
    TeamBuilder --> AgentPicker
    AgentPicker --> LoadAgents
    
    DilemmaForm --> handleStartDebate
    handleStartDebate --> DebateView
    DebateView --> DilemmaDisplay
    DebateView --> RoundsContainer
    RoundsContainer --> AgentsPanel
    AgentsPanel --> TypewriterEffect
    DebateView --> StageControls
    StageControls --> handleContinue
    StageControls --> handleJudge
    
    Step1 --> DebateLibrary
```

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
    
    style User fill:#1a1a2e,stroke:#00d9ff,stroke-width:2px,color:#fff
    style Frontend fill:#1a1a2e,stroke:#00ff88,stroke-width:2px,color:#fff
    style Backend fill:#1a1a2e,stroke:#ffd700,stroke-width:2px,color:#fff
    style AILayer fill:#1a1a2e,stroke:#ff6b6b,stroke-width:2px,color:#fff
    style Services fill:#1a1a2e,stroke:#00d9ff,stroke-width:2px,color:#fff
```

### 1.2 Data Flow - Opening Arguments

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant AgentService
    participant Groq
    participant JSONParser
    
    User->>Frontend: Submit dilemma + select 3 agents
    Frontend->>Frontend: Validate inputs
    Frontend->>API: POST /openings {dilemma, agents}
    
    loop For each agent
        API->>AgentService: get_agent_system_prompt(agent_id)
        AgentService-->>API: System prompt
        API->>API: Build prompt: system + dilemma + instructions
        API->>Groq: Generate opening argument
        Note over Groq: Temperature: 0.65<br/>Max tokens: 150-200
        Groq-->>API: Raw LLM response
        API->>JSONParser: clamp_json(response)
        JSONParser->>JSONParser: Try fenced JSON block
        JSONParser->>JSONParser: Try parse entire text
        JSONParser->>JSONParser: Scan for {...} objects
        JSONParser->>JSONParser: Regex extract stance/argument
        JSONParser-->>API: {stance: "A|B", argument: "text"}
        API->>API: Validate stance and argument
        alt Invalid response
            API->>Groq: Retry with temp 0.8
            Groq-->>API: Second attempt
            API->>JSONParser: Parse again
        end
        API-->>Frontend: AgentTurn object
        Frontend->>Frontend: Append to transcript
        Frontend->>User: Display with typewriter effect
    end
    
    Frontend->>User: Show "Continue Debate" button
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
    
    style DebateView fill:#1a1a2e,stroke:#00d9ff,stroke-width:2px,color:#fff
    style TurnComponent fill:#1a1a2e,stroke:#00ff88,stroke-width:2px,color:#fff
```

---

## 2. Custom Agent Builder

### 2.1 System Architecture

```mermaid
graph TB
    subgraph UI["User Interface"]
        Step1[Step 1: Name<br/>3-50 chars, unique]
        Step2[Step 2: Avatar<br/>32 emoji options]
        Step3[Step 3: Description<br/>50-1000 chars]
        EnhanceBtn[Enhance Button<br/>Trigger GPT-4o]
        QualityDisplay[Quality Display<br/>4 dimension scores]
        PreviewPanel[Preview Panel<br/>Enhanced framework]
    end
    
    subgraph Frontend["Frontend Logic"]
        FormState[Form State<br/>name, avatar, description]
        ValidationLogic[Validation Logic<br/>Character counts, uniqueness]
        APIClient[API Client<br/>POST /api/agents/create]
    end
    
    subgraph Backend["Backend API"]
        CreateEndpoint[POST /api/agents/create]
        EnhanceEndpoint[POST /api/enhance]
        RegenerateEndpoint[POST /api/agents/{id}/regenerate]
    end
    
    subgraph EnhancementPipeline["Enhancement Pipeline"]
        EnhancementService[Enhancement Service]
        PromptAnalyzer[Prompt Analyzer<br/>Score 4 dimensions]
        PromptEnhancer[Prompt Enhancer<br/>GPT-4o expansion]
        SystemPromptGen[System Prompt Generator<br/>Debate-ready format]
    end
    
    subgraph AI["AI Integration"]
        GPT4o[OpenAI GPT-4o<br/>Temperature: 0.7<br/>Max tokens: 500]
    end
    
    subgraph Storage["Data Storage"]
        AgentService[Agent Service]
        AgentsJSON[custom_agents.json<br/>Atomic writes]
    end
    
    Step1 --> FormState
    Step2 --> FormState
    Step3 --> FormState
    FormState --> ValidationLogic
    ValidationLogic --> EnhanceBtn
    EnhanceBtn --> APIClient
    APIClient --> CreateEndpoint
    
    CreateEndpoint --> EnhancementService
    EnhancementService --> PromptAnalyzer
    EnhancementService --> PromptEnhancer
    PromptEnhancer --> GPT4o
    GPT4o --> PromptEnhancer
    PromptEnhancer --> SystemPromptGen
    SystemPromptGen --> AgentService
    AgentService --> AgentsJSON
    
    AgentService --> QualityDisplay
    AgentService --> PreviewPanel
    
    style UI fill:#1a1a2e,stroke:#00d9ff,stroke-width:2px,color:#fff
    style Frontend fill:#1a1a2e,stroke:#00ff88,stroke-width:2px,color:#fff
    style Backend fill:#1a1a2e,stroke:#ffd700,stroke-width:2px,color:#fff
    style EnhancementPipeline fill:#1a1a2e,stroke:#ff6b6b,stroke-width:2px,color:#fff
    style AI fill:#1a1a2e,stroke:#ff6b6b,stroke-width:2px,color:#fff
    style Storage fill:#1a1a2e,stroke:#ffd700,stroke-width:2px,color:#fff
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
    
    style Description fill:#1a1a2e,stroke:#00d9ff,stroke-width:2px,color:#fff
    style Analyzer fill:#1a1a2e,stroke:#00ff88,stroke-width:2px,color:#fff
    style OverallScore fill:#1a1a2e,stroke:#ffd700,stroke-width:2px,color:#fff
    style Display fill:#1a1a2e,stroke:#ff6b6b,stroke-width:2px,color:#fff
```

---

## 3. Debate Library & Deduplication

### 3.1 System Architecture

```mermaid
graph TB
    subgraph UI["User Interface"]
        TemplateLibrary[Template Library<br/>34+ pre-made debates]
        CustomDebateForm[Custom Debate Form<br/>Title, context, options]
        ToastNotification[Toast Notification<br/>Added or duplicate]
    end
    
    subgraph Frontend["Frontend Logic"]
        DebateSubmission[Debate Submission<br/>On debate start]
        NotificationState[Notification State<br/>4 second timeout]
    end
    
    subgraph Backend["Backend API"]
        SubmitEndpoint[POST /api/debates/submit]
        TemplatesEndpoint[GET /api/templates]
    end
    
    subgraph DeduplicationService["Deduplication Service"]
        SubmitDebate[submit_custom_debate]
        FindDuplicate[find_duplicate<br/>Similarity check]
        AddToLibrary[add_to_library<br/>Generate ID & slug]
    end
    
    subgraph EmbeddingService["Embedding Service"]
        GenerateEmbedding[generate_debate_embedding<br/>Hash-based 384-dim vectors]
        ComputeSimilarity[compute_similarity<br/>Cosine similarity]
        TextToEmbedding[_text_to_embedding<br/>Word + char n-grams]
    end
    
    subgraph Storage["Data Storage"]
        TemplatesJSON[debate_templates.json<br/>Atomic writes]
    end
    
    TemplateLibrary --> CustomDebateForm
    CustomDebateForm --> DebateSubmission
    DebateSubmission --> SubmitEndpoint
    
    SubmitEndpoint --> SubmitDebate
    SubmitDebate --> FindDuplicate
    FindDuplicate --> GenerateEmbedding
    GenerateEmbedding --> TextToEmbedding
    TextToEmbedding --> ComputeSimilarity
    
    ComputeSimilarity --> FindDuplicate
    FindDuplicate --> AddToLibrary
    AddToLibrary --> TemplatesJSON
    
    TemplatesJSON --> ToastNotification
    ToastNotification --> NotificationState
    
    TemplatesEndpoint --> TemplatesJSON
    
    style UI fill:#1a1a2e,stroke:#00d9ff,stroke-width:2px,color:#fff
    style Frontend fill:#1a1a2e,stroke:#00ff88,stroke-width:2px,color:#fff
    style Backend fill:#1a1a2e,stroke:#ffd700,stroke-width:2px,color:#fff
    style DeduplicationService fill:#1a1a2e,stroke:#ff6b6b,stroke-width:2px,color:#fff
    style EmbeddingService fill:#1a1a2e,stroke:#ff6b6b,stroke-width:2px,color:#fff
    style Storage fill:#1a1a2e,stroke:#ffd700,stroke-width:2px,color:#fff
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
