# MirrorMinds: AI-Powered Ethical Debate Platform

<div align="center">

**Where AI Agents Debate Philosophy, Ethics, and Moral Dilemmas**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

*An experimental platform exploring how AI agents reason about complex ethical dilemmas through structured philosophical debate*

[Features](#-features) • [Demo](#-demo) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Roadmap](#-roadmap)

</div>

---

## 🎯 What is MirrorMinds?

MirrorMinds is an interactive web platform where AI agents engage in structured ethical debates, each representing distinct moral philosophies. Users can:

- **Watch AI Debates**: Submit ethical dilemmas and observe agents debate from different philosophical perspectives
- **Create Custom Agents**: Build personalized ethical AI agents with GPT-4o-powered enhancement
- **Analyze Arguments**: See how different ethical frameworks approach the same problem
- **Track Performance**: View analytics on agent performance, debate outcomes, and reasoning patterns

### 🌟 What Makes It Special?

- **🎭 Philosophical Diversity**: Default agents represent Deontology, Consequentialism, and Virtue Ethics
- **✨ AI-Enhanced Agent Builder**: GPT-4o analyzes and improves your agent descriptions with quality scoring
- **🎯 Structured Debate Format**: Opening arguments → Counter-rounds → Final judgment
- **📊 Analytics Dashboard**: Track debate metrics, agent performance, and topic trends
- **🎨 Modern UI**: Sleek dark theme with smooth animations and responsive design

---

## 🚀 Features

### Core Debate System

<table>
<tr>
<td width="50%">

**🤖 Default Philosophical Agents**
- **⚖️ Deon** - Deontologist (Rules & Duties)
- **◆ Conse** - Consequentialist (Outcomes & Utility)
- **✦ Virtue** - Virtue Ethicist (Character & Flourishing)

</td>
<td width="50%">

**🎯 Structured Debate Flow**
- Opening arguments with stance declaration
- Multi-round counter-arguments
- Final judgment with ethical scoring
- Debate history and replay

</td>
</tr>
</table>

### Custom Agent Builder

<table>
<tr>
<td width="50%">

**✨ 4-Step Creation Wizard**
1. **Basic Info** - Name + 32 emoji avatars
2. **Personality** - Natural language description
3. **AI Enhancement** - GPT-4o analysis & improvement
4. **Preview** - Review and create

</td>
<td width="50%">

**📊 Quality Analysis**
- **Clarity** - Sentence structure & readability
- **Completeness** - Presence of key elements
- **Specificity** - Concrete vs vague terms
- **Consistency** - Logical coherence

</td>
</tr>
</table>

### Real Enhancement Example

```
📝 INPUT (User Description):
"This agent is a doctor who believes in patient autonomy above all else."

✨ OUTPUT (GPT-4o Enhanced):
"Dr. Maya Chen champions patient autonomy as the cornerstone of medical ethics. 
She applies a framework rooted in informed consent and bodily autonomy, citing 
landmark cases like Cruzan v. Director to support her positions. When evaluating 
medical dilemmas, she prioritizes the patient's right to make their own healthcare 
decisions, even when those choices conflict with medical recommendations. Her 
approach acknowledges the tension between beneficence and autonomy, but she 
consistently argues that respecting patient agency is fundamental to ethical care."

📈 SCORES: Clarity: 9.2 | Completeness: 8.8 | Specificity: 9.5 | Consistency: 9.0
```

---

## 🎬 Demo

### Debate Interface
```
┌─────────────────────────────────────────────────────────────┐
│ 🎯 Dilemma: Should AI be used for medical diagnosis?       │
│                                                             │
│ Option A: Yes, AI improves accuracy and saves lives        │
│ Option B: No, human doctors should make all decisions      │
└─────────────────────────────────────────────────────────────┘

⚖️ Deon (Stance: B)
"I must emphasize that medical decisions involve human dignity and 
autonomy. While AI may be accurate, delegating life-or-death choices 
to algorithms violates the principle that humans deserve human judgment..."

◆ Conse (Stance: A)
"Deon, I understand your concern for dignity, but we must consider 
outcomes. Studies show AI reduces diagnostic errors by 30%, potentially 
saving thousands of lives annually. The greater good demands we use 
every tool available..."

✦ Virtue (Stance: A)
"Conse, while I agree with your conclusion, I'd frame it differently. 
A virtuous physician demonstrates wisdom by using AI as a tool to enhance 
their judgment, not replace it. The key is cultivating the character to 
use technology responsibly..."
```

### Agent Builder Interface
```
┌──────────────────────────────────────────────────────────────┐
│  Step 3: AI Enhancement Results                              │
│  Our AI analyzed your description and made improvements      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Clarity        Completeness    Specificity    Consistency  │
│    ⭕ 9.2         ⭕ 8.8          ⭕ 9.5          ⭕ 9.0      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 🌱 EcoWarrior                                          │ │
│  │ Enhanced Personality                                   │ │
│  │                                                        │ │
│  │ EcoWarrior champions environmental protection as...   │ │
│  │ [Enhanced description with reasoning framework]        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  [✨ Regenerate]                                             │
└──────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Debate View  │  │ Agent Builder│  │  Dashboard   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↕ REST API
┌─────────────────────────────────────────────────────────────────┐
│                       Backend (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Debate Engine│  │ Enhancement  │  │   Metrics    │         │
│  │   Service    │  │   Service    │  │   Service    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
         ↕                    ↕                    ↕
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Ollama     │    │  OpenAI      │    │     JSON     │
│  (Qwen 2.5)  │    │   GPT-4o     │    │   Storage    │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 18 + Vite | Modern reactive UI with fast HMR |
| **Backend** | FastAPI + Python 3.8+ | High-performance async API |
| **Debate AI** | Ollama + Qwen 2.5 7B | Local AI inference for debates |
| **Enhancement AI** | OpenAI GPT-4o | Cloud-based prompt improvement |
| **Storage** | JSON Files | Lightweight persistent storage |
| **Styling** | Modern CSS + Animations | Dark theme with glass morphism |

### Key Design Patterns

- **Service Layer Architecture**: Clean separation between API, business logic, and data
- **Structured Output**: JSON schema validation ensures reliable AI responses
- **Recursive Enhancement**: Analysis scores guide targeted improvements
- **Modular Components**: Reusable React components with clear responsibilities

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required
- Python 3.8+
- Node.js 16+
- Ollama (for local AI)
- OpenAI API key (for agent enhancement)

# Optional
- Git
```

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/khattam/MirrorMind.git
cd MirrorMind

# 2. Setup Backend
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install fastapi uvicorn requests python-dotenv pydantic openai

# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env

# 3. Setup Frontend
cd ../frontend
npm install

# 4. Start Ollama
ollama serve
ollama pull qwen2.5:7b-instruct-q4_K_M

# 5. Run the Application
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev

# 6. Open Browser
# Navigate to http://localhost:5173
```

### First Debate

1. Enter an ethical dilemma with two clear options
2. Select which agents should participate (default or custom)
3. Watch the structured debate unfold
4. Review the final judgment and ethical scores

### Create Your First Agent

1. Click **"✨ Create Custom Agent"** in the sidebar
2. Name your agent and choose an avatar
3. Describe their personality and values (50-1000 characters)
4. Let GPT-4o enhance your description
5. Review the improvements and create

---

## 📊 Project Structure

```
MirrorMind/
├── backend/
│   ├── main.py                 # FastAPI app & routes
│   ├── models/
│   │   └── custom_agent.py     # Data models
│   ├── services/
│   │   ├── agent_service.py    # Agent CRUD operations
│   │   ├── enhancement_service.py  # AI enhancement logic
│   │   └── metrics_service.py  # Analytics tracking
│   ├── data/
│   │   ├── agents/             # Custom agent storage
│   │   └── metrics/            # Debate metrics
│   └── test/                   # Unit tests
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AgentBuilder/   # 4-step wizard
│   │   │   ├── DebateView.jsx  # Debate interface
│   │   │   ├── Dashboard.jsx   # Analytics dashboard
│   │   │   └── ...
│   │   ├── App.jsx             # Main app component
│   │   └── main.jsx            # Entry point
│   └── package.json
├── docs/
│   └── agent-builder-architecture.md  # Technical docs
└── README.md
```

---

## 🎯 Use Cases

### 🎓 Education
- **Philosophy Classes**: Demonstrate different ethical frameworks
- **Critical Thinking**: Analyze argument structure and logical reasoning
- **Debate Practice**: Learn argumentation techniques from AI examples

### 🔬 Research
- **AI Ethics**: Study how AI systems reason about moral dilemmas
- **Bias Detection**: Compare how different frameworks handle edge cases
- **Argument Analysis**: Examine persuasion strategies and logical patterns

### 💼 Professional Development
- **Ethics Training**: Explore workplace ethical scenarios
- **Decision Making**: See multiple perspectives on complex choices
- **Policy Analysis**: Evaluate ethical implications of decisions

### 🎮 Entertainment
- **Philosophical Exploration**: Engage with deep ethical questions
- **Agent Creation**: Build and test custom ethical personalities
- **Debate Tournaments**: Compare agent performance across scenarios

---

## 🗺️ Roadmap

### ✅ Phase 1: Foundation (Complete)
- [x] Core debate system with 3 default agents
- [x] Structured debate flow (opening → counter → judgment)
- [x] Custom agent builder with AI enhancement
- [x] Quality scoring system (4 dimensions)
- [x] Agent library with CRUD operations
- [x] Analytics dashboard with hardcoded stats

### 🚧 Phase 2: Integration (In Progress)
- [ ] Custom agents participating in live debates
- [ ] Real-time metrics collection and display
- [ ] Agent performance tracking and ratings
- [ ] Export debates as formatted reports (PDF/Markdown)
- [ ] Advanced search and filtering for agents

### 🔮 Phase 3: Social Features
- [ ] Public agent library with discovery
- [ ] Community ratings and reviews
- [ ] Agent tournaments and leaderboards
- [ ] Share debates on social media
- [ ] Collaborative debate mode (multiple users)

### 🎓 Phase 4: Educational Platform
- [ ] LMS integration (Canvas, Blackboard, Moodle)
- [ ] Curriculum-specific ethical scenarios
- [ ] Student progress tracking
- [ ] Assignment templates and grading rubrics
- [ ] Instructor dashboard and analytics

### 🚀 Phase 5: Advanced AI
- [ ] Multi-model support (GPT-4, Claude, Llama)
- [ ] Agent learning from debate outcomes
- [ ] Specialized domain agents (Legal, Medical, Business)
- [ ] Advanced fallacy detection
- [ ] Real-time debate coaching

---

## 🧪 Sample Debates

### Medical Ethics
```
Dilemma: Should experimental treatments be allowed without full FDA approval?
Agents: Dr. Ethics (Custom), Deon, Conse
Winner: Dr. Ethics (89% confidence)
Key Argument: "Patient autonomy must be balanced with evidence-based medicine..."
```

### AI Ethics
```
Dilemma: Should AI systems be allowed to make hiring decisions?
Agents: TechEthicist (Custom), Virtue, Conse
Winner: TechEthicist (76% confidence)
Key Argument: "Algorithmic bias perpetuates systemic discrimination..."
```

### Environmental Policy
```
Dilemma: Should we prioritize economic growth or climate action?
Agents: EcoWarrior (Custom), Deon, Virtue
Winner: EcoWarrior (92% confidence)
Key Argument: "Future generations have rights we must protect today..."
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 Bug Reports
- Use GitHub Issues with detailed reproduction steps
- Include screenshots and error messages
- Specify your environment (OS, browser, versions)

### ✨ Feature Requests
- Describe the feature and its use case
- Explain how it fits with the project vision
- Consider implementation complexity

### 💻 Code Contributions
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📚 Documentation
- Improve README clarity
- Add code comments
- Create tutorials and guides
- Fix typos and formatting

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[Ollama](https://ollama.ai/)** - Excellent local AI model infrastructure
- **[OpenAI](https://openai.com/)** - GPT-4o for intelligent enhancement
- **[FastAPI](https://fastapi.tiangolo.com/)** - Robust Python web framework
- **[React](https://reactjs.org/)** - Modern frontend library
- **[Vite](https://vitejs.dev/)** - Lightning-fast build tool
- **Open Source Community** - For inspiration and foundational tools

---

## 📞 Contact & Links

- **GitHub**: [github.com/khattam/MirrorMind](https://github.com/khattam/MirrorMind)
- **Issues**: [Report bugs or request features](https://github.com/khattam/MirrorMind/issues)
- **Discussions**: [Join the conversation](https://github.com/khattam/MirrorMind/discussions)

---

<div align="center">

**Built with ❤️ for exploring the intersection of AI, ethics, and human reasoning**

⭐ Star this repo if you find it interesting!

</div>
