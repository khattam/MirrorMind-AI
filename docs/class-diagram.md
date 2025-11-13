# MirrorMind AI - Complete Class Diagram

## System Architecture Overview

```mermaid
graph TB
    subgraph Frontend["Frontend Layer (React)"]
        App[App.jsx]
        DilemmaForm[DilemmaForm]
        DebateView[DebateView]
        VerdictView[VerdictView]
        Dashboard[Dashboard]
        AgentBuilder[AgentBuilder]
        AgentSelector[AgentSelector]
        Sidebar[Sidebar]
    end
    
    subgraph Backend["Backend Layer (FastAPI)"]
        MainAPI[main.py - FastAPI App]
        DebateEndpoints[Debate Endpoints]
        AgentEndpoints[Agent Endpoints]
        MetricsEndpoints[Metrics Endpoints]
        HistoryEndpoints[History Endpoints]
    end
    
    subgraph Services["Service Layer"]
        AgentService[AgentService]
        EnhancementService[EnhancementService]
        MetricsService[MetricsService]
        HistoryService[DebateHistoryService]
    end
    
    subgraph Models["Data Models"]
        CustomAgent[CustomAgent]
        AgentRating[AgentRating]
        Dilemma[Dilemma]
        AgentTurn[AgentTurn]
        Transcript[Transcript]
    end
    
    subgraph AI["AI Integration"]
        GroqAPI[Groq API - Llama 3.3 70B]
        OpenAIAPI[OpenAI API - GPT-4o]
    end
    
    subgraph Storage["Data Storage"]
        AgentsJSON[custom_agents.json]
        RatingsJSON[agent_ratings.json]
        MetricsJSON[debate_metrics.json]
        HistoryJSON[debate_history.json]
    end
    
    App --> DilemmaForm
    App --> DebateView
    App --> VerdictView
    App --> Dashboard
    App --> AgentBuilder
    App --> Sidebar
    
    DilemmaForm --> MainAPI
    DebateView --> MainAPI
    AgentBuilder --> MainAPI
    Dashboard --> MainAPI
    
    MainAPI --> DebateEndpoints
    MainAPI --> AgentEndpoints
    MainAPI --> MetricsEndpoints
    MainAPI --> HistoryEndpoints
    
    DebateEndpoints --> GroqAPI
    AgentEndpoints --> AgentService
    AgentEndpoints --> EnhancementService
    MetricsEndpoints --> MetricsService
    HistoryEndpoints --> HistoryService
    
    EnhancementService --> OpenAIAPI
    
    AgentService --> AgentsJSON
    AgentService --> RatingsJSON
    MetricsService --> MetricsJSON
    HistoryService --> HistoryJSON
    
    style Frontend fill:#1a1a2e,stroke:#00d9ff,stroke-width:2px,color:#fff
    style Backend fill:#1a1a2e,stroke:#00ff88,stroke-width:2px,color:#fff
    style Services fill:#1a1a2e,stroke:#ffd700,stroke-width:2px,color:#fff
    style Models fill:#1a1a2e,stroke:#ff6b6b,stroke-width:2px,color:#fff
    style AI fill:#1a1a2e,stroke:#ff6b6b,stroke-width:2px,color:#fff
    style Storage fill:#1a1a2e,stroke:#ffd700,stroke-width:2px,color:#fff
```

---

## Backend Class Diagram

```mermaid
classDiagram
    %% Models
    class CustomAgent {
        +String id
        +String name
        +String avatar
        +String description
        +String enhanced_prompt
        +String system_prompt
        +String created_by
        +DateTime created_at
        +Boolean is_public
        +Integer usage_count
        +Float average_rating
        +Integer rating_count
    }
    
    class AgentRating {
        +String id
        +String agent_id
        +String debate_id
        +String user_id
        +Integer argument_quality
        +Integer consistency
        +Integer engagement
        +Integer overall_satisfaction
        +String comment
        +DateTime created_at
    }
    
    class EnhancementRequest {
        +String original_description
        +String enhanced_prompt
        +List~String~ improvements_made
        +Dict~String,Float~ analysis_scores
        +List~String~ suggestions
    }
    
    class AgentCreationRequest {
        +String name
        +String avatar
        +String description
    }
    
    class AgentUpdateRequest {
        +Optional~String~ name
        +Optional~String~ avatar
        +Optional~String~ description
    }
    
    class Dilemma {
        +String title
        +String A
        +String B
        +String constraints
    }
    
    class AgentTurn {
        +String agent
        +Optional~String~ stance
        +String argument
    }
    
    class Transcript {
        +Dilemma dilemma
        +List~AgentTurn~ turns
    }
    
    %% Services
    class AgentService {
        -Path storage_path
        -Path agents_file
        -Path ratings_file
        +create_agent(request, enhanced_prompt, system_prompt) CustomAgent
        +get_agent(agent_id) Optional~CustomAgent~
        +list_agents(public_only, search, limit) List~CustomAgent~
        +update_agent(agent_id, request, enhanced_prompt, system_prompt) Optional~CustomAgent~
        +delete_agent(agent_id) Boolean
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
    
    class EnhancementService {
        -PromptAnalyzer analyzer
        -PromptEnhancer enhancer
        +enhance_agent_description(description, agent_name) EnhancementRequest
        +analyze_only(description) Dict
        +generate_system_prompt(enhanced_prompt, agent_name) String
        -_preserve_agent_name(enhanced_prompt, original_name) String
    }
    
    class PromptAnalyzer {
        +analyze_description(description) Dict~String,Float~
        +generate_suggestions(description, scores) List~String~
        -_score_clarity(description) Float
        -_score_completeness(description) Float
        -_score_specificity(description) Float
        -_score_consistency(description) Float
    }
    
    class PromptEnhancer {
        +String ENHANCER_SYSTEM_PROMPT
        +enhance_description(description, agent_name) EnhancementRequest
        -_identify_improvements(original, enhanced, agent_name) List~String~
        -_fallback_enhancement(description, agent_name, scores, suggestions) EnhancementRequest
    }
    
    class MetricsService {
        -String storage_path
        +calculate_debate_metrics(transcript, verdict) Dict
        +record_debate(transcript, verdict) Dict
        +get_all_metrics() List~Dict~
        +get_summary_stats() Dict
        -_ensure_storage_exists() None
        -_load_metrics() Dict
        -_save_metrics(data) None
    }
    
    class DebateHistoryService {
        -Path storage_path
        -Path history_file
        +save_debate(transcript, verdict) Dict
        +get_all_debates(limit) List~Dict~
        +get_debate_by_id(debate_id) Optional~Dict~
        +delete_debate(debate_id) Boolean
        +clear_all_history() Boolean
        +get_stats() Dict
        -_load_history() List~Dict~
        -_save_history(history) None
    }
    
    %% Main API
    class FastAPIApp {
        +get_root() Dict
        +get_health() Dict
        +post_openings(dilemma) Dict
        +post_agent_response(agent_name, dilemma) Dict
        +post_continue(transcript) Dict
        +post_judge(transcript) Dict
        +post_create_agent(request) Dict
        +get_list_agents(public_only, search, limit) Dict
        +get_all_agents() Dict
        +get_agent(agent_id) Dict
        +put_update_agent(agent_id, request) Dict
        +delete_agent(agent_id) Dict
        +post_enhance(request) Dict
        +post_regenerate_agent(agent_id) Dict
        +get_metrics() Dict
        +get_metrics_summary() Dict
        +get_debates(limit) Dict
        +get_debate(debate_id) Dict
        +delete_debate(debate_id) Dict
        +get_debate_stats() Dict
    }
    
    %% Relationships
    AgentService --> CustomAgent : manages
    AgentService --> AgentRating : manages
    AgentService --> AgentCreationRequest : uses
    AgentService --> AgentUpdateRequest : uses
    
    EnhancementService --> PromptAnalyzer : uses
    EnhancementService --> PromptEnhancer : uses
    EnhancementService --> EnhancementRequest : creates
    
    PromptEnhancer --> EnhancementRequest : creates
    
    MetricsService --> Transcript : analyzes
    
    DebateHistoryService --> Transcript : stores
    
    FastAPIApp --> AgentService : uses
    FastAPIApp --> EnhancementService : uses
    FastAPIApp --> MetricsService : uses
    FastAPIApp --> DebateHistoryService : uses
    FastAPIApp --> Dilemma : uses
    FastAPIApp --> AgentTurn : uses
    FastAPIApp --> Transcript : uses
    
    CustomAgent --> AgentRating : has many
```

---

## Frontend Component Diagram

```mermaid
classDiagram
    %% Main App
    class App {
        -String currentView
        -Object dilemma
        -Array turns
        -Object verdict
        -Boolean isDebating
        -Boolean showSidebar
        -Array customAgents
        +handleDilemmaSubmit(dilemma)
        +handleContinue()
        +handleJudge()
        +handleReset()
        +loadCustomAgents()
        +render()
    }
    
    %% Components
    class DilemmaForm {
        -Object formData
        -Boolean isSubmitting
        +handleInputChange(field, value)
        +handleSubmit()
        +validateForm()
        +render()
    }
    
    class DebateView {
        +Array turns
        +Boolean isDebating
        +Function onContinue
        +Function onJudge
        +renderTurn(turn)
        +render()
    }
    
    class VerdictView {
        +Object verdict
        +Object dilemma
        +Function onReset
        +renderScores()
        +renderRecommendation()
        +render()
    }
    
    class Dashboard {
        -Array metrics
        -Object summaryStats
        -Array debateHistory
        -Boolean isLoading
        +loadMetrics()
        +loadDebateHistory()
        +renderMetricsChart()
        +renderDebateList()
        +render()
    }
    
    class AgentBuilder {
        -Object formData
        -Object enhancement
        -Boolean isEnhancing
        -Boolean showPreview
        -Array savedAgents
        +handleInputChange(field, value)
        +handleEnhance()
        +handleSave()
        +handleRegenerate()
        +loadSavedAgents()
        +render()
    }
    
    class AgentSelector {
        +Array agents
        +Array selectedAgents
        +Function onSelectionChange
        +renderAgentCard(agent)
        +render()
    }
    
    class AgentCard {
        +Object agent
        +Boolean isSelected
        +Function onClick
        +Function onDelete
        +renderAvatar()
        +renderStats()
        +render()
    }
    
    class AgentDetailsModal {
        +Object agent
        +Boolean isOpen
        +Function onClose
        +renderEnhancedPrompt()
        +renderSystemPrompt()
        +renderRatings()
        +render()
    }
    
    class Sidebar {
        +String currentView
        +Function onViewChange
        +Boolean isOpen
        +renderNavigation()
        +render()
    }
    
    class KeyboardShortcuts {
        +Object shortcuts
        +Boolean isVisible
        +Function onClose
        +renderShortcutList()
        +render()
    }
    
    %% Relationships
    App --> DilemmaForm : contains
    App --> DebateView : contains
    App --> VerdictView : contains
    App --> Dashboard : contains
    App --> AgentBuilder : contains
    App --> Sidebar : contains
    App --> KeyboardShortcuts : contains
    
    AgentBuilder --> AgentSelector : uses
    AgentSelector --> AgentCard : contains
    AgentCard --> AgentDetailsModal : opens
    
    Dashboard --> DebateView : displays history
```

---

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant FastAPI
    participant AgentService
    participant EnhancementService
    participant GroqAPI
    participant OpenAI
    participant Storage
    
    %% Agent Creation Flow
    User->>Frontend: Create Custom Agent
    Frontend->>FastAPI: POST /api/agents/create
    FastAPI->>EnhancementService: enhance_agent_description()
    EnhancementService->>OpenAI: Enhance prompt with GPT-4o
    OpenAI-->>EnhancementService: Enhanced prompt
    EnhancementService->>EnhancementService: generate_system_prompt()
    EnhancementService-->>FastAPI: EnhancementRequest
    FastAPI->>AgentService: create_agent()
    AgentService->>Storage: Save to custom_agents.json
    Storage-->>AgentService: Success
    AgentService-->>FastAPI: CustomAgent
    FastAPI-->>Frontend: Agent + Enhancement
    Frontend-->>User: Display created agent
    
    %% Debate Flow
    User->>Frontend: Submit Dilemma
    Frontend->>FastAPI: POST /openings
    FastAPI->>GroqAPI: Generate opening arguments
    GroqAPI-->>FastAPI: Agent responses
    FastAPI-->>Frontend: Opening turns
    Frontend-->>User: Display debate
    
    User->>Frontend: Continue Debate
    Frontend->>FastAPI: POST /continue
    FastAPI->>GroqAPI: Generate rebuttals
    GroqAPI-->>FastAPI: Agent responses
    FastAPI-->>Frontend: New turns
    Frontend-->>User: Display updated debate
    
    User->>Frontend: Request Judgment
    Frontend->>FastAPI: POST /judge
    FastAPI->>GroqAPI: Evaluate debate
    GroqAPI-->>FastAPI: Verdict
    FastAPI->>MetricsService: record_debate()
    MetricsService->>Storage: Save to debate_metrics.json
    FastAPI->>HistoryService: save_debate()
    HistoryService->>Storage: Save to debate_history.json
    FastAPI-->>Frontend: Verdict
    Frontend-->>User: Display verdict
```

---

## Storage Schema

### custom_agents.json
```json
{
  "agent_id": {
    "id": "uuid",
    "name": "string",
    "avatar": "emoji",
    "description": "string",
    "enhanced_prompt": "string",
    "system_prompt": "string",
    "created_by": "string",
    "created_at": "datetime",
    "is_public": "boolean",
    "usage_count": "integer",
    "average_rating": "float",
    "rating_count": "integer"
  }
}
```

### agent_ratings.json
```json
{
  "rating_id": {
    "id": "uuid",
    "agent_id": "string",
    "debate_id": "string",
    "user_id": "string",
    "argument_quality": "1-5",
    "consistency": "1-5",
    "engagement": "1-5",
    "overall_satisfaction": "1-5",
    "comment": "string",
    "created_at": "datetime"
  }
}
```

### debate_metrics.json
```json
{
  "debates": [
    {
      "debate_id": "string",
      "timestamp": "datetime",
      "dilemma_title": "string",
      "total_turns": "integer",
      "total_words": "integer",
      "num_agents": "integer",
      "agents": ["array"],
      "avg_words_per_turn": "float",
      "avg_words_per_agent": "object",
      "agent_word_counts": "object",
      "agent_turn_counts": "object",
      "stance_changes": "object",
      "most_verbose_agent": "string",
      "intensity_score": "float",
      "final_recommendation": "A|B",
      "confidence": "0-100",
      "ethical_scores": "object"
    }
  ]
}
```

### debate_history.json
```json
[
  {
    "id": "uuid",
    "title": "string",
    "date": "datetime",
    "timestamp": "float",
    "transcript": {
      "dilemma": "object",
      "turns": "array"
    },
    "verdict": "object",
    "recommendation": "A|B",
    "confidence": "0-100"
  }
]
```

---

## API Endpoints Summary

### Debate Endpoints
- `GET /` - Health check
- `GET /health` - Health check with status
- `POST /openings` - Generate opening arguments
- `POST /agent/{agent_name}` - Get single agent response
- `POST /continue` - Continue debate with rebuttals
- `POST /judge` - Get final verdict

### Agent Management Endpoints
- `POST /api/agents/create` - Create custom agent
- `GET /api/agents` - List all agents
- `GET /api/agents/all` - Get all available agents (default + custom)
- `GET /api/agents/{agent_id}` - Get specific agent
- `PUT /api/agents/{agent_id}` - Update agent
- `DELETE /api/agents/{agent_id}` - Delete agent
- `POST /api/agents/{agent_id}/regenerate` - Regenerate agent prompt

### Enhancement Endpoints
- `POST /api/enhance` - Enhance agent description

### Metrics Endpoints
- `GET /api/metrics` - Get all debate metrics
- `GET /api/metrics/summary` - Get aggregate statistics

### History Endpoints
- `GET /api/debates` - Get debate history
- `GET /api/debates/{debate_id}` - Get specific debate
- `DELETE /api/debates/{debate_id}` - Delete debate
- `GET /api/debates/stats` - Get debate statistics

---

## Technology Stack

### Frontend
- **React 18.3+** - UI framework
- **Vite** - Build tool
- **Pure CSS** - Styling (no UI library)
- **Fetch API** - HTTP requests

### Backend
- **FastAPI** - Web framework
- **Python 3.8+** - Programming language
- **Pydantic** - Data validation
- **JSON** - Data storage

### AI Integration
- **Groq API** - Llama 3.3 70B for debates
- **OpenAI API** - GPT-4o for agent enhancement

### Deployment
- **Vercel** - Frontend hosting
- **Render** - Backend hosting
- **GitHub Actions** - CI/CD & uptime monitoring

---

## Key Design Patterns

1. **Service Layer Pattern** - Business logic separated into services
2. **Repository Pattern** - Data access abstracted through services
3. **Factory Pattern** - Agent creation through AgentService
4. **Strategy Pattern** - Different AI providers (Groq/OpenAI)
5. **Observer Pattern** - Metrics and history tracking
6. **Singleton Pattern** - Service instances in FastAPI

---

## Future Enhancements (Phase 2)

- User authentication and authorization
- PostgreSQL database migration
- Custom agents in live debates
- Agent marketplace
- Real-time debate streaming
- Multi-language support
- Advanced analytics dashboard
