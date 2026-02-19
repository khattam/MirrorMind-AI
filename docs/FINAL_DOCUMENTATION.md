# MirrorMind AI - Final Technical Documentation

**Version:** 1.0  
**Date:** February 10, 2026  
**Author:** Medhansh Khattam  
**Project:** Multi-Agent Ethical Debate Platform

---

## Executive Summary

MirrorMind AI is a web-based platform enabling AI agents with distinct ethical frameworks to debate complex moral dilemmas in real-time. Users submit ethical scenarios, watch AI agents argue from philosophical perspectives (deontological, consequentialist, virtue ethics), and receive impartial judgments scored across five ethical dimensions.

**Key Capabilities:**
- Multi-agent debate system with 3 default philosophical agents + custom agent creation
- GPT-4o powered agent enhancement pipeline
- Semantic deduplication for debate library (34+ templates)
- 5-dimensional ethical scoring by impartial AI judge
- Analytics dashboard with debate metrics
- Full debate history with replay functionality
- PDF export for debates

**Technology Stack:**
- **Frontend:** React 18.3, Vite, CSS3
- **Backend:** Python 3.8+, FastAPI
- **AI Models:** Groq (Llama 3.3 70B), OpenAI (GPT-4o)
- **Storage:** JSON files (atomic writes)
- **Deployment:** Vercel (frontend), Render (backend)

**Live Demo:** [mirror-mind-ai.vercel.app](https://mirror-mind-ai.vercel.app)

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture](#2-architecture)
3. [Core Features](#3-core-features)
4. [Technical Implementation](#4-technical-implementation)
5. [AI/ML Components](#5-aiml-components)
6. [API Reference](#6-api-reference)
7. [Data Models](#7-data-models)
8. [Deployment](#8-deployment)
9. [Future Enhancements](#9-future-enhancements)

---

## 1. System Overview

### 1.1 Purpose

MirrorMind AI addresses the challenge of exploring ethical dilemmas from multiple philosophical perspectives simultaneously. Traditional ethical analysis requires understanding various frameworks; MirrorMind automates this by having AI agents embody different ethical philosophies and debate in structured rounds.

### 1.2 Target Users

- **Students & Educators:** Philosophy courses, ethics training, debate practice
- **Researchers:** AI ethics studies, moral reasoning analysis, dataset generation
- **Ethics Professionals:** Corporate training, medical ethics, policy evaluation
- **General Public:** Philosophy enthusiasts, curious individuals, content creators

### 1.3 Key Innovations

1. **Multi-Agent Debate System:** First platform enabling real-time philosophical debates between AI agents with distinct ethical frameworks
2. **GPT-4o Agent Enhancement:** Transforms simple descriptions into sophisticated ethical reasoning frameworks with quality scoring
3. **Semantic Deduplication:** Hash-based embedding system (384-dim) for instant duplicate detection without API calls
4. **5-Dimensional Ethical Scoring:** Comprehensive verdict analysis across autonomy, harm prevention, fairness, transparency, and long-term impact

---

## 2. Architecture

### 2.1 System Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        Browser[Web Browser]
        React[React Application]
    end
    
    subgraph Frontend["Frontend - Vercel"]
        App[App.jsx<br/>State Management]
        Components[Components<br/>DilemmaForm, DebateView, etc.]
        Utils[Utilities<br/>PDF Export, API Client]
    end
    
    subgraph Backend["Backend - Render"]
        FastAPI[FastAPI Server<br/>main.py]
        Services[Services Layer<br/>Agent, Enhancement, etc.]
        Storage[JSON Storage<br/>Atomic Writes]
    end
    
    subgraph AI["AI Providers"]
        Groq[Groq API<br/>Llama 3.3 70B]
        OpenAI[OpenAI API<br/>GPT-4o]
    end
    
    Browser --> React
    React --> App
    App --> Components
    Components --> Utils
    
    Utils -->|HTTPS/REST| FastAPI
    FastAPI --> Services
    Services --> Storage
    
    Services -->|Debate Generation| Groq
    Services -->|Agent Enhancement| OpenAI
```

### 2.2 Technology Stack

**Frontend:**
- React 18.3 with Hooks (useState, useEffect)
- Vite for build tooling
- CSS3 with custom dark theme
- jsPDF for PDF generation
- Fetch API for HTTP requests

**Backend:**
- Python 3.8+ with FastAPI framework
- Pydantic for data validation
- Groq SDK for Llama 3.3 70B access
- OpenAI SDK for GPT-4o access
- JSON file storage with atomic writes

**Deployment:**
- Frontend: Vercel (automatic deployments from main branch)
- Backend: Render (Python 3.8 runtime)
- CORS enabled for cross-origin requests

---

## 3. Core Features

### 3.1 AI Debate Arena

**Purpose:** Enable multi-agent ethical debates with real-time argument generation.

**Workflow:**
1. User submits dilemma (title, context, options A & B)
2. User selects 3 agents (default or custom)
3. System generates opening arguments sequentially
4. Agents engage in rebuttal rounds
5. Judge provides verdict with ethical scores

**Key Components:**
- DilemmaForm: 2-step wizard for input
- AgentSelector: 3-slot team builder
- DebateView: Real-time display with TypewriterText animation
- VerdictView: Final judgment with 5-dimensional scores

**Technical Details:**
- Sequential agent processing (prevents race conditions)
- 4-level JSON parsing fallback (fenced block → full parse → object scan → regex)
- Opponent validation ensures agents address each other
- Temperature: 0.65 for arguments, 0.3 for judge (consistency)
- Max tokens: 150-200 for arguments, 800 for verdict



**Class Diagram:**

```mermaid
classDiagram
    class DilemmaRequest {
        <<Pydantic BaseModel>>
        +str title
        +str A
        +str B
        +str constraints
    }
    
    class AgentTurn {
        <<dict>>
        +str agent
        +str stance
        +str argument
    }
    
    class Transcript {
        <<dict>>
        +dict dilemma
        +List~AgentTurn~ turns
    }
    
    class DebateAPI {
        <<main.py endpoints>>
        +post_openings(dilemma) List~AgentTurn~
        +post_continue(transcript) List~AgentTurn~
        +post_agent_by_name(agent_name, dilemma) AgentTurn
        +call_ollama(sys, user, temp, tokens) str
        +clamp_json(response, fallback) dict
        +get_agent_system_prompt(agent_name) str
        +has_valid_opponent(text, agent, all_agents) bool
    }
    
    class PromptTemplates {
        <<main.py constants>>
        +str DEON_SYS
        +str CONSE_SYS
        +str VIRTUE_SYS
        +str OPENING_INSTRUCT
        +str CONTINUE_INSTRUCT
    }
    
    class AppComponent {
        <<React Component>>
        +state stage
        +state dilemma
        +state transcript
        +state verdict
        +state selectedAgentsInfo
        +state currentThinkingAgent
        +handleStartDebate(formData, agentIds, agentsInfo)
        +handleContinue()
        +handleJudge()
        +checkAndAddToLibrary(dilemmaData)
    }
    
    class DilemmaForm {
        <<React Component>>
        +state step
        +state formData
        +state selectedAgents
        +validateStep1() bool
        +validateStep2() bool
        +handleSubmit()
    }
    
    class DebateView {
        <<React Component>>
        +props transcript
        +props currentThinkingAgent
        +renderDilemma()
        +renderTurns()
        +renderControls()
    }
    
    class TypewriterText {
        <<React Component>>
        +props text
        +props speed
        +state displayedText
        +useEffect() void
    }
    
    DebateAPI --> DilemmaRequest : receives
    DebateAPI --> Transcript : manages
    DebateAPI --> AgentTurn : creates
    DebateAPI --> PromptTemplates : uses
    
    AppComponent --> DilemmaForm : renders
    AppComponent --> DebateView : renders
    AppComponent --> Transcript : manages
    
    DebateView --> TypewriterText : uses
    DebateView --> AgentTurn : displays
```

### 3.1.2 Component Architecture (Frontend)

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

### 3.1.3 System Architecture (Full Stack)

```mermaid
graph LR
    User[User] --> DilemmaForm[DilemmaForm]
    DilemmaForm --> App[App.jsx]
    
    App --> API[Backend API]
    API --> Groq[Groq API<br/>Llama 3.3 70B]
    
    API --> AgentService[AgentService]
    API --> MetricsService[MetricsService]
    API --> HistoryService[HistoryService]
    
    Groq --> App
    App --> DebateView[DebateView]
    DebateView --> User
```

### 3.1.4 Data Flow - Opening Arguments

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

### 3.1.5 Data Flow - Rebuttal Round

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

### 3.1.6 Component Architecture

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

### 3.2 Custom Agent Builder

**Purpose:** Enable users to create personalized AI agents with enhanced ethical frameworks.

**Workflow:**
1. User enters name (1-50 chars), avatar emoji, description (50-1000 chars)
2. Frontend validates uniqueness against default + custom agents
3. User clicks "Enhance with AI"
4. PromptAnalyzer scores description (clarity, completeness, specificity, consistency)
5. GPT-4o expands description into 4-5 detailed sentences
6. System generates debate-ready system prompt
7. AgentService saves with UUID to custom_agents.json
8. Agent immediately available for debates

**Quality Scoring Algorithm:**
- **Clarity (0-10):** Sentence length analysis (optimal 15-20 words)
- **Completeness (0-10):** Checks for values, reasoning, examples, personality, decision-making
- **Specificity (0-10):** Vague terms vs specific terms ratio
- **Consistency (0-10):** Detects contradictions (-2 points each)

**Enhancement Process:**
- Temperature: 0.7 for creativity
- Max tokens: 500 for detailed expansion
- Quality check: retries if <50 words or missing agent name
- Preserves original name by removing JSON fields

**Class Diagram:**

```mermaid
classDiagram
    class CustomAgent {
        +str id
        +str name
        +str avatar
        +str description
        +str enhanced_prompt
        +str system_prompt
        +str created_by
        +datetime created_at
        +bool is_public
        +int usage_count
        +float average_rating
        +int rating_count
    }
    
    class AgentRating {
        +str id
        +str agent_id
        +str debate_id
        +str user_id
        +int argument_quality
        +int consistency
        +int engagement
        +int overall_satisfaction
        +str comment
        +datetime created_at
    }
    
    class EnhancementRequest {
        +str original_description
        +str enhanced_prompt
        +List~str~ improvements_made
        +Dict~str,float~ analysis_scores
        +List~str~ suggestions
    }
    
    class AgentCreationRequest {
        +str name
        +str avatar
        +str description
    }
    
    class AgentUpdateRequest {
        +Optional~str~ name
        +Optional~str~ avatar
        +Optional~str~ description
    }
    
    class AgentService {
        -Path storage_path
        -Path agents_file
        -Path ratings_file
        +__init__(storage_path)
        +create_agent(request, enhanced_prompt, system_prompt) CustomAgent
        +get_agent(agent_id) Optional~CustomAgent~
        +get_agent_by_name(name) Optional~CustomAgent~
        +list_agents(public_only, search, limit) List~CustomAgent~
        +update_agent(agent_id, request) Optional~CustomAgent~
        +delete_agent(agent_id) bool
        +increment_usage(agent_id) None
        +add_rating(rating) None
        +get_agent_ratings(agent_id) List~AgentRating~
        +get_default_agents() List~Dict~
        +get_all_available_agents() List~Dict~
        -_load_agents() Dict
        -_save_agents(agents) None
        -_load_ratings() Dict
        -_save_ratings(ratings) None
        -_check_duplicate_name(name) None
        -_update_agent_rating(agent_id) None
    }
    
    class PromptAnalyzer {
        +analyze_description(description) Dict~str,float~
        -_score_clarity(description) float
        -_score_completeness(description) float
        -_score_specificity(description) float
        -_score_consistency(description) float
        +generate_suggestions(description, scores) List~str~
    }
    
    class PromptEnhancer {
        +str ENHANCER_SYSTEM_PROMPT
        +enhance_description(description, agent_name) EnhancementRequest
        -_identify_improvements(original, enhanced, agent_name) List~str~
        -_fallback_enhancement(description, agent_name, scores, suggestions) EnhancementRequest
    }
    
    class EnhancementService {
        -PromptAnalyzer analyzer
        -PromptEnhancer enhancer
        +__init__()
        +enhance_agent_description(description, agent_name) EnhancementRequest
        +analyze_only(description) Dict
        +generate_system_prompt(enhanced_prompt, agent_name) str
        -_preserve_agent_name(enhanced_prompt, original_name) str
    }
    
    AgentService --> CustomAgent : creates/manages
    AgentService --> AgentRating : stores
    AgentService --> AgentCreationRequest : receives
    AgentService --> AgentUpdateRequest : receives
    
    EnhancementService --> PromptAnalyzer : uses
    EnhancementService --> PromptEnhancer : uses
    EnhancementService --> EnhancementRequest : returns
    
    PromptEnhancer --> EnhancementRequest : creates
    PromptAnalyzer --> EnhancementRequest : contributes to
    
    AgentRating --> CustomAgent : rates
```

### 3.2.2 System Architecture

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

### 3.2.3 Data Flow - Agent Creation

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

### 3.2.4 Quality Scoring Algorithm

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

### 3.3 Debate Library & Deduplication

**Purpose:** Prevent duplicate debates using semantic similarity detection.

**Workflow:**
1. When debate starts, App.jsx calls checkAndAddToLibrary() in background
2. DebateDeduplicationService validates required fields
3. EmbeddingService generates 384-dim vector (hash-based: word + char n-grams)
4. Computes cosine similarity against all existing templates
5. If similarity >= 0.95: duplicate found, returns match
6. If similarity < 0.95: unique debate, generates ID and slug, saves with atomic write
7. Frontend shows toast notification (success or duplicate)

**Embedding Algorithm:**
- For each word: hash(word) % 384, hash(reverse) % 384, hash(every other char) % 384
- For each trigram: hash(trigram) % 384
- Normalizes to unit length for cosine similarity
- Title excluded (only context/options matter)
- Instant results (no API calls)

**Class Diagram:**

```mermaid
classDiagram
    class DebateDeduplicationService {
        -Path templates_path
        -EmbeddingService embedding_service
        +submit_custom_debate(debate) DeduplicationResult
        +find_duplicate(debate) Optional~dict~
        +add_to_library(debate) dict
        -_load_templates() List~dict~
        -_save_templates(templates) None
        -_generate_slug(title, existing) str
        -_has_significant_field_difference(d1, d2) bool
    }
    
    class EmbeddingService {
        -Optional~Groq~ groq_client
        +generate_debate_embedding(debate) ndarray
        +compute_similarity(emb1, emb2) float
        +compare_debates(debate1, debate2) float
        +llm_semantic_comparison(d1, d2) dict
        -_create_debate_text(debate) str
        -_text_to_embedding(text) ndarray
    }
    
    class DeduplicationResult {
        +bool success
        +bool is_duplicate
        +str message
        +Optional~dict~ matched_template
        +Optional~dict~ added_template
        +to_dict() dict
    }
    
    class DebateTemplate {
        <<dict>>
        +int id
        +str slug
        +str title
        +str context
        +str option_a
        +str option_b
        +str created_at
        +bool is_custom
    }
    
    DebateDeduplicationService --> EmbeddingService : uses
    DebateDeduplicationService --> DeduplicationResult : returns
    DebateDeduplicationService --> DebateTemplate : manages
    EmbeddingService --> DebateTemplate : embeds
```

### 3.3.2 Frontend Architecture

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

### 3.3.3 Backend Architecture

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

### 3.4 Judge System

**Purpose:** Provide impartial ethical analysis with 5-dimensional scoring.

**Workflow:**
1. User clicks "Get Verdict"
2. Backend validates transcript, builds judge prompt
3. Calls Groq with JUDGE_SYS prompt (temp 0.3, max_tokens 800)
4. Parses verdict: final_recommendation, confidence, 5 scores, reasoning, key_considerations
5. MetricsService calculates debate stats
6. DebateHistoryService saves with UUID
7. VerdictView displays results

**5-Dimensional Scoring:**
- **Autonomy (0-10):** Respect for individual choice and self-determination
- **Harm Prevention (0-10):** Minimizing negative consequences
- **Fairness (0-10):** Equal treatment and justice
- **Transparency (0-10):** Openness and accountability
- **Long-term Impact (0-10):** Sustainability and future consequences

**Metrics Calculated:**
- Total turns/words, per-agent stats
- Stance changes (how often agents switched positions)
- Most verbose agent
- Intensity score (avg words/turn)

**Class Diagram:**

```mermaid
classDiagram
    class JudgeRequest {
        <<Pydantic BaseModel>>
        +dict transcript
        +validate_transcript() dict
    }
    
    class EthicalScores {
        <<dict>>
        +float autonomy
        +float harm_prevention
        +float fairness
        +float transparency
        +float long_term_impact
    }
    
    class Verdict {
        <<dict>>
        +str final_recommendation
        +float confidence
        +EthicalScores scores
        +str reasoning
        +List~str~ key_considerations
    }
    
    class JudgeSystem {
        <<main.py functions>>
        +str JUDGE_SYS
        +judge_debate(transcript) Verdict
        +call_ollama(system_prompt, user_prompt) str
        +clamp_json(response, fallback) dict
        -_build_judge_prompt(transcript) str
        -_parse_verdict(response) Verdict
    }
    
    JudgeSystem --> JudgeRequest : receives
    JudgeSystem --> Verdict : returns
    Verdict --> EthicalScores : contains
```

### 3.4.2 Data Flow - Verdict Generation

```mermaid
sequenceDiagram
    participant User
    participant DebateView
    participant App
    participant Backend
    participant JudgeSystem
    participant Groq
    participant MetricsService
    participant HistoryService
    
    User->>DebateView: Click "Get Verdict"
    DebateView->>App: handleJudge()
    App->>App: setStage('judging')
    
    App->>Backend: POST /judge {transcript}
    Backend->>Backend: Validate transcript has turns
    
    Backend->>JudgeSystem: Build judge prompt
    Note over JudgeSystem: Summarize dilemma<br/>Extract all arguments<br/>Format for analysis
    
    JudgeSystem->>Groq: call_ollama(JUDGE_SYS, judge_prompt)
    Note over Groq: Temperature: 0.3<br/>Max tokens: 800<br/>Model: Llama 3.3 70B
    
    Groq-->>JudgeSystem: Raw verdict JSON
    JudgeSystem->>JudgeSystem: clamp_json(response)
    
    JudgeSystem->>JudgeSystem: Validate verdict structure
    Note over JudgeSystem: Check: final_recommendation,<br/>confidence, scores (5 dimensions),<br/>reasoning, key_considerations
    
    alt Verdict valid
        JudgeSystem-->>Backend: Verdict object
    else Verdict invalid
        JudgeSystem->>Groq: Retry with stricter prompt
        Groq-->>JudgeSystem: Second attempt
        JudgeSystem->>JudgeSystem: Parse again
    end
    
    Backend->>MetricsService: record_debate(transcript, verdict)
    MetricsService->>MetricsService: Calculate metrics
    MetricsService->>MetricsService: Save to debate_metrics.json
    
    Backend->>HistoryService: save_debate(transcript, verdict)
    HistoryService->>HistoryService: Generate debate ID
    HistoryService->>HistoryService: Save to debate_history.json
    
    Backend-->>App: {verdict, metrics}
    App->>App: setVerdict(verdict)
    App->>App: setStage('verdict')
    App->>DebateView: Update to VerdictView
    DebateView->>User: Display verdict with scores
```

### 3.5 Analytics Dashboard

**Purpose:** Aggregate and visualize debate statistics.

**Metrics Tracked:**
- Total debates conducted
- Total words and turns
- Average debate length
- Most common winner (A vs B)
- Agent usage statistics
- Most used agent

**Data Storage:**
- debate_metrics.json: per-debate statistics
- Atomic writes prevent corruption
- Summary stats aggregated on-demand

**Class Diagram:**

```mermaid
classDiagram
    class MetricsService {
        -str storage_path
        +__init__(storage_path)
        +calculate_debate_metrics(transcript, verdict) Dict
        +record_debate(transcript, verdict) Dict
        +get_all_metrics() List~Dict~
        +get_summary_stats() Dict
        -_load_metrics() Dict
        -_save_metrics(data) None
        -_ensure_storage_exists() None
    }
    
    class DebateMetrics {
        <<dict>>
        +str debate_id
        +str timestamp
        +str dilemma_title
        +int total_turns
        +int total_words
        +int num_agents
        +List~str~ agents
        +float avg_words_per_turn
        +Dict avg_words_per_agent
        +Dict agent_word_counts
        +Dict agent_turn_counts
        +Dict stance_changes
        +str most_verbose_agent
        +float intensity_score
        +str final_recommendation
        +float confidence
        +Dict ethical_scores
    }
    
    class SummaryStats {
        <<dict>>
        +int total_debates
        +int total_words
        +int total_turns
        +float avg_debate_length
        +float avg_words_per_debate
        +str most_common_winner
        +Dict agent_usage
        +str most_used_agent
    }
    
    class Dashboard {
        <<React Component>>
        +state metrics
        +state summaryStats
        +useEffect() void
        +fetchMetrics() Promise
        +renderCharts() JSX
        +renderAgentStats() JSX
        +renderDebateHistory() JSX
    }
    
    MetricsService --> DebateMetrics : creates
    MetricsService --> SummaryStats : aggregates
    Dashboard --> MetricsService : fetches from
```

### 3.6 Debate History & Replay

**Purpose:** Browse and replay past debates without re-running AI.

**Features:**
- Automatic saving after every verdict
- UUID for unique identification
- Stores complete transcript + verdict
- Limits to last 100 debates
- Instant replay (no AI regeneration)
- Delete functionality

**Class Diagram:**

```mermaid
classDiagram
    class DebateHistoryService {
        -Path storage_path
        -Path history_file
        +__init__(storage_path)
        +save_debate(transcript, verdict) dict
        +get_all_debates(limit) List~dict~
        +get_debate_by_id(debate_id) Optional~dict~
        +delete_debate(debate_id) bool
        +clear_all_history() bool
        +get_stats() dict
        -_load_history() List~dict~
        -_save_history(history) None
    }
    
    class DebateEntry {
        <<dict>>
        +str id
        +str title
        +str date
        +float timestamp
        +dict transcript
        +dict verdict
        +str recommendation
        +float confidence
    }
    
    class DebateLibrary {
        <<React Component>>
        +state debates
        +state selectedDebate
        +useEffect() void
        +fetchDebates() Promise
        +handleSelectDebate(id) void
        +handleDeleteDebate(id) void
        +renderDebateList() JSX
        +renderDebatePreview() JSX
    }
    
    DebateHistoryService --> DebateEntry : manages
    DebateLibrary --> DebateHistoryService : fetches from
    DebateLibrary --> DebateEntry : displays
```

### 3.6.2 Data Flow - Replay Debate

```mermaid
sequenceDiagram
    participant User
    participant DebateLibrary
    participant Backend
    participant HistoryService
    participant App
    participant DebateView
    
    User->>DebateLibrary: Browse saved debates
    DebateLibrary->>Backend: GET /api/history
    Backend->>HistoryService: get_all_debates(limit=50)
    HistoryService->>HistoryService: _load_history()
    HistoryService-->>Backend: List of debate entries
    Backend-->>DebateLibrary: debates array
    
    DebateLibrary->>User: Display debate list
    User->>DebateLibrary: Click debate to replay
    
    DebateLibrary->>Backend: GET /api/history/{debate_id}
    Backend->>HistoryService: get_debate_by_id(debate_id)
    HistoryService-->>Backend: Full debate entry
    Backend-->>DebateLibrary: {transcript, verdict}
    
    DebateLibrary->>App: loadDebate(transcript, verdict)
    App->>App: setTranscript(transcript)
    App->>App: setVerdict(verdict)
    App->>App: setStage('verdict')
    
    App->>DebateView: Render with full transcript
    DebateView->>User: Display all turns + verdict
    
    Note over User,DebateView: User can view full debate<br/>without re-running AI
```

### 3.7 PDF Export

**Purpose:** Generate professional debate documents.

**Process:**
1. User clicks "Export to PDF"
2. PDFExporter creates jsPDF instance
3. Adds header, dilemma, rounds, verdict, scores
4. Word-wraps text (max 170mm width)
5. Adds page numbers
6. Triggers browser download

**Sections Included:**
- Header with title, date, agents
- Dilemma context and options
- All debate rounds with arguments
- Final verdict with reasoning
- 5-dimensional ethical scores

**Class Diagram:**

```mermaid
classDiagram
    class PDFExporter {
        <<pdfExport.js>>
        +exportDebateToPDF(transcript, verdict) Promise
        -_createPDFDocument() jsPDF
        -_addHeader(doc, title) void
        -_addDilemma(doc, dilemma) void
        -_addDebateRounds(doc, turns) void
        -_addVerdict(doc, verdict) void
        -_addScores(doc, scores) void
        -_formatText(text, maxWidth) string[]
        -_addPageNumbers(doc) void
    }
    
    class VerdictView {
        <<React Component>>
        +props transcript
        +props verdict
        +handleExportPDF() void
        +renderExportButton() JSX
    }
    
    class jsPDF {
        <<External Library>>
        +text(text, x, y) void
        +setFontSize(size) void
        +setFont(font, style) void
        +addPage() void
        +save(filename) void
        +getNumberOfPages() int
    }
    
    VerdictView --> PDFExporter : uses
    PDFExporter --> jsPDF : uses
```

### 3.7.2 Data Flow - PDF Generation

```mermaid
sequenceDiagram
    participant User
    participant VerdictView
    participant PDFExporter
    participant jsPDF
    participant Browser
    
    User->>VerdictView: Click "Export to PDF"
    VerdictView->>PDFExporter: exportDebateToPDF(transcript, verdict)
    
    PDFExporter->>jsPDF: new jsPDF()
    PDFExporter->>jsPDF: setFont('helvetica')
    
    PDFExporter->>PDFExporter: _addHeader(doc, title)
    Note over PDFExporter: Add title, date, agents
    
    PDFExporter->>PDFExporter: _addDilemma(doc, dilemma)
    Note over PDFExporter: Add context, options A & B
    
    loop For each turn
        PDFExporter->>PDFExporter: _formatText(argument, maxWidth)
        PDFExporter->>jsPDF: text(agent + stance)
        PDFExporter->>jsPDF: text(formatted argument)
        
        alt Page full
            PDFExporter->>jsPDF: addPage()
        end
    end
    
    PDFExporter->>PDFExporter: _addVerdict(doc, verdict)
    Note over PDFExporter: Add recommendation,<br/>confidence, reasoning
    
    PDFExporter->>PDFExporter: _addScores(doc, scores)
    Note over PDFExporter: Add 5-dimensional<br/>ethical scores
    
    PDFExporter->>PDFExporter: _addPageNumbers(doc)
    
    PDFExporter->>jsPDF: save('debate-export.pdf')
    jsPDF->>Browser: Trigger download
    Browser->>User: Download PDF file
```

---

## 4. Technical Implementation

### 4.1 Frontend Architecture

**State Management:**
- App.jsx: Central state (stage, dilemma, transcript, verdict, selectedAgentsInfo)
- Props drilling for component communication
- useState/useEffect hooks for reactivity

**Key Components:**
- **DilemmaForm:** 2-step wizard with validation
- **AgentSelector:** 3-slot team builder with modal picker
- **DebateView:** Real-time display with collapsible rounds
- **TypewriterText:** Animated text rendering (configurable speed)
- **VerdictView:** Final judgment display with score bars
- **Dashboard:** Analytics visualization
- **DebateLibrary:** History browser with replay

**Styling:**
- Custom CSS with dark theme
- Responsive design (mobile-friendly)
- Smooth animations and transitions
- Color-coded elements (agents, stances, scores)

### 4.2 Backend Architecture

**FastAPI Endpoints:**
- POST /openings: Generate opening arguments
- POST /continue: Generate rebuttals
- POST /judge: Get verdict
- POST /agent/{agent_name}: Single agent response
- GET /api/agents: List all agents
- POST /api/agents/create: Create custom agent
- POST /api/debates/submit: Submit debate for deduplication
- GET /api/history: Get debate history

**Service Layer:**
- **AgentService:** CRUD operations for custom agents
- **EnhancementService:** GPT-4o enhancement pipeline
- **DebateDeduplicationService:** Semantic duplicate detection
- **EmbeddingService:** Hash-based embedding generation
- **MetricsService:** Debate statistics calculation
- **DebateHistoryService:** Debate storage and retrieval

**Data Storage:**
- JSON files with atomic writes (temp file → rename)
- custom_agents.json: Custom agent data
- agent_ratings.json: Agent ratings
- debate_templates.json: Debate library
- debate_metrics.json: Debate statistics
- debate_history.json: Debate transcripts

### 4.3 AI Integration

**Groq API (Llama 3.3 70B):**
- Used for: Opening arguments, rebuttals, judge verdicts
- Temperature: 0.65 for arguments, 0.3 for judge
- Max tokens: 150-200 for arguments, 800 for verdict
- Top-p: 0.9 for diversity
- Retry logic with increased temperature on failure

**OpenAI API (GPT-4o):**
- Used for: Agent enhancement
- Temperature: 0.7 for creativity
- Max tokens: 500 for detailed expansion
- Quality check with retry mechanism

**JSON Parsing (4-Level Fallback):**
1. Try ```json...``` fenced block
2. Try parse entire text as JSON
3. Scan for {...} objects
4. Regex extract stance + argument

**Prompt Engineering:**
- System prompts define agent personalities
- User prompts include dilemma context
- OPENING_INSTRUCT: "Pick a side and argue"
- CONTINUE_INSTRUCT: "Respond to opponent by name"
- JUDGE_SYS: "Impartial ethical judge"

---

## 5. AI/ML Components

### 5.1 Large Language Models

**Llama 3.3 70B (via Groq):**
- **Purpose:** Debate generation, verdict analysis
- **Strengths:** Fast inference, strong reasoning, JSON output
- **Configuration:** Temperature 0.3-0.65, top-p 0.9
- **Cost:** Free tier available

**GPT-4o (via OpenAI):**
- **Purpose:** Agent enhancement
- **Strengths:** Creative expansion, quality writing
- **Configuration:** Temperature 0.7, max_tokens 500
- **Cost:** Pay-per-token

### 5.2 Embedding System

**Hash-Based Embeddings:**
- **Dimensions:** 384 (standard embedding size)
- **Algorithm:** Word hashing + character n-grams
- **Speed:** Instant (no API calls)
- **Accuracy:** 95%+ for exact/near-exact matches

**Cosine Similarity:**
- **Threshold:** 0.95 for duplicate detection
- **Formula:** dot(v1, v2) / (norm(v1) * norm(v2))
- **Range:** 0.0 (completely different) to 1.0 (identical)

### 5.3 Quality Scoring

**PromptAnalyzer Metrics:**
- Clarity: Sentence length optimization
- Completeness: Element presence detection
- Specificity: Vague vs specific term ratio
- Consistency: Contradiction detection

**Scoring Range:** 0-10 for each dimension
**Overall Score:** Average of 4 dimensions
**Color Coding:** <60% red, 60-80% yellow, >80% green

---

## 6. API Reference

### 6.1 Debate Endpoints

**POST /openings**
```json
Request:
{
  "title": "Self-Driving Car Dilemma",
  "A": "Swerve left (kill 1 pedestrian)",
  "B": "Stay straight (kill 5 pedestrians)",
  "constraints": "Car cannot brake in time",
  "agent_names": ["deon", "conse", "virtue"]
}

Response:
{
  "turns": [
    {
      "agent": "Deon",
      "stance": "A",
      "argument": "..."
    },
    ...
  ]
}
```

**POST /continue**
```json
Request:
{
  "transcript": {
    "dilemma": {...},
    "turns": [...]
  }
}

Response:
{
  "turns": [...]
}
```

**POST /judge**
```json
Request:
{
  "transcript": {
    "dilemma": {...},
    "turns": [...]
  }
}

Response:
{
  "final_recommendation": "A",
  "confidence": 75,
  "scores": {
    "autonomy": 8.5,
    "harm_prevention": 6.0,
    "fairness": 7.5,
    "transparency": 9.0,
    "long_term_impact": 7.0
  },
  "reasoning": "...",
  "key_considerations": [...]
}
```

### 6.2 Agent Endpoints

**GET /api/agents**
```json
Response:
{
  "agents": [
    {
      "id": "deon",
      "name": "Deon",
      "avatar": "⚖️",
      "description": "...",
      "type": "default"
    },
    {
      "id": "uuid-here",
      "name": "Dr. Maya Chen",
      "avatar": "🌱",
      "description": "...",
      "type": "custom",
      "rating": 4.5,
      "usage_count": 12
    }
  ]
}
```

**POST /api/agents/create**
```json
Request:
{
  "name": "Dr. Maya Chen",
  "avatar": "🌱",
  "description": "A doctor who believes in patient autonomy..."
}

Response:
{
  "agent": {
    "id": "uuid-here",
    "name": "Dr. Maya Chen",
    ...
  },
  "enhancement": {
    "original_description": "...",
    "enhanced_prompt": "...",
    "improvements_made": [...],
    "analysis_scores": {
      "clarity": 8.5,
      "completeness": 7.0,
      "specificity": 9.0,
      "consistency": 8.0
    }
  }
}
```

### 6.3 Library Endpoints

**POST /api/debates/submit**
```json
Request:
{
  "title": "...",
  "context": "...",
  "option_a": "...",
  "option_b": "..."
}

Response:
{
  "success": true,
  "is_duplicate": false,
  "message": "Debate added to library!",
  "added_template": {...}
}
```

**GET /api/history?limit=50**
```json
Response:
{
  "debates": [
    {
      "id": "uuid-here",
      "title": "...",
      "date": "2026-02-10T...",
      "recommendation": "A",
      "confidence": 75
    },
    ...
  ]
}
```

---

## 7. Data Models

### 7.1 Core Models

**CustomAgent:**
```python
class CustomAgent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(min_length=1, max_length=50)
    avatar: str = Field(default="🤖")
    description: str = Field(min_length=50, max_length=1000)
    enhanced_prompt: str
    system_prompt: str
    created_at: datetime = Field(default_factory=datetime.now)
    usage_count: int = Field(default=0)
    average_rating: float = Field(default=0.0)
```

**AgentTurn:**
```python
{
    "agent": str,  # Agent name
    "stance": str,  # "A" or "B"
    "argument": str  # Argument text
}
```

**Transcript:**
```python
{
    "dilemma": {
        "title": str,
        "A": str,
        "B": str,
        "constraints": str
    },
    "turns": List[AgentTurn]
}
```

**Verdict:**
```python
{
    "final_recommendation": str,  # "A" or "B"
    "confidence": float,  # 0-100
    "scores": {
        "autonomy": float,  # 0-10
        "harm_prevention": float,
        "fairness": float,
        "transparency": float,
        "long_term_impact": float
    },
    "reasoning": str,
    "key_considerations": List[str]
}
```

### 7.2 Storage Schema

**custom_agents.json:**
```json
{
  "uuid-1": {
    "id": "uuid-1",
    "name": "Dr. Maya Chen",
    "avatar": "🌱",
    "description": "...",
    "enhanced_prompt": "...",
    "system_prompt": "...",
    "created_at": "2026-02-10T...",
    "usage_count": 12,
    "average_rating": 4.5,
    "rating_count": 3
  }
}
```

**debate_templates.json:**
```json
[
  {
    "id": 1,
    "slug": "trolley-problem",
    "title": "The Trolley Problem",
    "context": "...",
    "option_a": "...",
    "option_b": "...",
    "created_at": "2026-02-10T...",
    "is_custom": false
  }
]
```

**debate_history.json:**
```json
[
  {
    "id": "uuid-here",
    "title": "...",
    "date": "2026-02-10T...",
    "timestamp": 1707523200.0,
    "transcript": {...},
    "verdict": {...},
    "recommendation": "A",
    "confidence": 75
  }
]
```

---

## 8. Deployment

### 8.1 Frontend Deployment (Vercel)

**Configuration:**
- Framework: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Node version: 18.x
- Environment variables: `VITE_API_URL`

**Automatic Deployments:**
- Push to main branch triggers deployment
- Preview deployments for pull requests
- Custom domain: mirror-mind-ai.vercel.app

### 8.2 Backend Deployment (Render)

**Configuration:**
- Runtime: Python 3.8
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment variables: `GROQ_API_KEY`, `OPENAI_API_KEY`

**Features:**
- Auto-deploy from main branch
- Health checks
- Persistent disk for JSON storage
- Custom domain: mirrormind-ai.onrender.com

### 8.3 Environment Variables

**Frontend (.env):**
```
VITE_API_URL=https://mirrormind-ai.onrender.com
```

**Backend (.env):**
```
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
AI_PROVIDER=groq
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## 9. Future Enhancements

### 9.1 Short-Term (3-6 months)

**Database Migration:**
- PostgreSQL for scalability
- Proper indexing for fast queries
- Backup and recovery

**User Authentication:**
- OAuth integration (Google, GitHub)
- Personal agent libraries
- Private debates

**Enhanced Analytics:**
- Debate outcome trends
- Agent performance over time
- Argument pattern analysis

### 9.2 Long-Term (6-12 months)

**Agent Marketplace:**
- Public agent sharing
- Community ratings and reviews
- Featured agents

**Multi-Language Support:**
- Internationalization (i18n)
- Translated UI
- Multi-language debates

**Mobile Applications:**
- React Native apps
- Offline mode
- Push notifications

**LMS Integration:**
- Canvas, Blackboard, Moodle
- Grade synchronization
- Assignment templates

### 9.3 Research Directions

**Agent Learning:**
- Reinforcement learning from debate outcomes
- Agent evolution based on ratings
- Adaptive argumentation strategies

**Advanced AI Models:**
- Claude integration
- Local model support (Ollama)
- Multi-model ensemble

**Ethical Framework Expansion:**
- Care ethics
- Feminist ethics
- Non-Western philosophies

---

## Conclusion

MirrorMind AI successfully demonstrates the potential of multi-agent AI systems for ethical reasoning and philosophical debate. The platform combines cutting-edge AI models (Llama 3.3 70B, GPT-4o) with intuitive user interfaces to make complex ethical analysis accessible to everyone.

**Key Achievements:**
- ✅ Real-time multi-agent debates with distinct philosophical frameworks
- ✅ GPT-4o powered agent enhancement with quality scoring
- ✅ Semantic deduplication with instant results (no API calls)
- ✅ 5-dimensional ethical scoring for comprehensive analysis
- ✅ Full debate history with replay functionality
- ✅ Professional PDF export
- ✅ Production deployment on Vercel and Render

**Technical Highlights:**
- Robust JSON parsing with 4-level fallback
- Atomic file writes prevent data corruption
- Hash-based embeddings for instant similarity detection
- Sequential agent processing prevents race conditions
- Comprehensive error handling and retry logic

**Impact:**
MirrorMind AI democratizes access to philosophical debate and ethical analysis, enabling students, educators, researchers, and the general public to explore complex moral dilemmas from multiple perspectives simultaneously.

---

**Project Repository:** [github.com/khattam/MirrorMind-AI](https://github.com/khattam/MirrorMind-AI)  
**Live Demo:** [mirror-mind-ai.vercel.app](https://mirror-mind-ai.vercel.app)  
**API Endpoint:** [mirrormind-ai.onrender.com](https://mirrormind-ai.onrender.com)

**Contact:** Medhansh Khattam  
**Date:** February 10, 2026
