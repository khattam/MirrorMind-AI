# backend/main.py
import json
import requests
from typing import List, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import re

# -------------------- AI PROVIDER CONFIG --------------------
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq")  # "groq" or "ollama"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_MODEL = "qwen2.5:7b-instruct-q4_K_M"
OLLAMA_API = "http://localhost:11434/api/generate"

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def call_ollama(system_prompt: str, user_prompt: str, num_predict: int = 400, temp: float = 0.7, top_p: float = 0.9, repeat_penalty: float = 1.1) -> str:
    """Unified AI call function - supports both Groq and Ollama"""
    
    if AI_PROVIDER == "groq" and groq_client:
        # Use Groq API
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=GROQ_MODEL,
                temperature=temp,
                max_tokens=num_predict,
                top_p=top_p,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq API error: {e}, falling back to Ollama")
            # Fall back to Ollama if Groq fails
    
    # Use Ollama (local or fallback)
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n",
        "options": {
            "temperature": temp,
            "top_p": top_p,
            "repeat_penalty": repeat_penalty,
            "num_predict": num_predict
        },
        "stream": False,
    }
    
    headers = {"Content-Type": "application/json"}
    if OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"
   
    r = requests.post(OLLAMA_API, json=payload, headers=headers, timeout=240)
    r.raise_for_status()
    return r.json().get("response", "").strip()



import re

def clamp_json(s: str, fallback: dict) -> dict:
    """
    Robust JSON extractor:
    1) prefer ```json ... ``` fenced blocks
    2) else try to parse entire text as JSON
    3) else scan all {...} objects and return the first valid one
    4) else fallback with raw
    """
    try:
        text = s.strip()

        # 1) fenced ```json blocks
        fence = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
        if fence:
            try:
                return json.loads(fence.group(1))
            except json.JSONDecodeError:
                pass

        # 2) Try to parse the entire text as JSON first
        try:
            j = json.loads(text)
            if isinstance(j, dict):
                return j
        except json.JSONDecodeError:
            pass

        # 3) scan for any JSON objects, prefer ones with both keys
        objs = re.findall(r"\{.*?\}", text, re.DOTALL)
        best = None
        for m in objs:
            try:
                j = json.loads(m)
                if isinstance(j, dict):
                    if "stance" in j and "argument" in j:
                        return j
                    if best is None:
                        best = j
            except json.JSONDecodeError:
                continue

        if best is not None:
            return best

        # 3) Try to extract stance and argument separately if JSON parsing fails
        stance_match = re.search(r'"stance"\s*:\s*"([^"]*)"', text, re.IGNORECASE)
        arg_match = re.search(r'"argument"\s*:\s*"([^"]+)"', text, re.DOTALL | re.IGNORECASE)
        
        if stance_match and arg_match:
            raw_stance = stance_match.group(1).strip().upper()
            # Clean stance to only valid values
            if raw_stance in ["A", "B", "SAME"]:
                clean_stance = raw_stance
            elif "A" in raw_stance and "B" not in raw_stance:
                clean_stance = "A"
            elif "B" in raw_stance and "A" not in raw_stance:
                clean_stance = "B"
            else:
                clean_stance = "same"
            
            return {
                "stance": clean_stance,
                "argument": arg_match.group(1)
            }

        return fallback | {"_debug": text[:500]}
    except Exception as e:
        return fallback | {"_debug": f"[clamp_json error] {e}: {s[:200]}"}


# -------------------- ROLE PROMPTS --------------------
DEON_SYS = (
    "You are Deon, a deontologist who believes moral worth comes from following principles, duties, and rights. "
    "You prioritize integrity, consent, fairness, and respect for universal rules. "
    "If breaking a rule leads to good outcomes, you still refuse because morality must be consistent. "
    "You often cite moral laws, rights, or obligations. "
    "When responding to opponents, ALWAYS start with their name followed by a comma. "
    "Respond in compact JSON only."
)

CONSE_SYS = (
    "You are Conse, a consequentialist. You evaluate actions purely by their outcomes: who benefits, who is harmed, and how much overall welfare changes. "
    "Rules are heuristics, not absolutes. If breaking one rule produces greater total well-being or avoids greater suffering, you allow it. "
    "You explicitly weigh short-term versus long-term consequences. "
    "When responding to opponents, ALWAYS start with their name followed by a comma. "
    "Respond in compact JSON only."
)

VIRTUE_SYS = (
    "You are Virtue, a virtue ethicist. You focus on character and human flourishing rather than strict rules or outcomes. "
    "You judge what a virtuous person (honest, compassionate, courageous, wise, just) would do to cultivate good moral character. "
    "You often reference virtues or vices directly. "
    "When responding to opponents, ALWAYS start with their name followed by a comma. "
    "Respond in compact JSON only."
)

JUDGE_SYS = (
    "You are the Judge, a neutral evaluator of ethical reasoning. Given the dilemma and all rounds of debate, "
    "you must evaluate both options and provide a comprehensive verdict.\n\n"
    "Your response MUST be valid JSON with this exact structure:\n"
    "{\n"
    '  "scores": {\n'
    '    "option_a": {"harm_minimization": 0-2, "rule_consistency": 0-2, "autonomy_respect": 0-2, "honesty": 0-2, "fairness": 0-2},\n'
    '    "option_b": {"harm_minimization": 0-2, "rule_consistency": 0-2, "autonomy_respect": 0-2, "honesty": 0-2, "fairness": 0-2}\n'
    '  },\n'
    '  "final_recommendation": "A or B",\n'
    '  "confidence": 0-100,\n'
    '  "verdict": "2-3 sentence explanation of your decision"\n'
    "}\n\n"
    "Return ONLY the JSON object, no other text."
)

# -------------------- MODELS --------------------
class Dilemma(BaseModel):
    title: str
    A: str
    B: str
    constraints: str

class AgentTurn(BaseModel):
    agent: str
    stance: Optional[str] = Field(None, description="A or B if declared")
    argument: str

class Transcript(BaseModel):
    dilemma: Dilemma
    turns: List[AgentTurn]

# Import custom agent models
from models.custom_agent import CustomAgent, AgentCreationRequest, AgentUpdateRequest, AgentRating
from services.agent_service import AgentService
from services.enhancement_service import EnhancementService
from services.metrics_service import MetricsService
from services.debate_history_service import DebateHistoryService

# Import deduplication service
from services.debate_deduplication_service import DebateDeduplicationService

# Initialize services
agent_service = AgentService()
enhancement_service = EnhancementService()
metrics_service = MetricsService()
debate_history_service = DebateHistoryService()
deduplication_service = DebateDeduplicationService(groq_client=groq_client)

# -------------------- APP CONFIG --------------------
app = FastAPI(title="MirrorMinds API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.head("/")
def root():
    return {"message": "MirrorMinds backend is running!"}

@app.get("/health")
@app.head("/health")
def health_check():
    """Health check endpoint for monitoring services"""
    return {"status": "healthy", "service": "MirrorMinds API"}

# -------------------- HELPERS --------------------
def mk_base(d: Dilemma) -> str:
    return (
        f"DILEMMA\nTitle: {d.title}\n"
        f"Option A: {d.A}\nOption B: {d.B}\n"
        f"Constraints: {d.constraints}\n"
    )

OPENING_INSTRUCT = (
    "Opening: Choose A or B, and write a BRIEF response (2-3 sentences max) that:\n"
    "• states your position clearly\n"
    "• gives ONE key reason from your ethical framework\n"
    "Be concise and direct. No lengthy explanations.\n"
    "Respond JSON only: {\"stance\":\"A|B\",\"argument\":\"<brief paragraph>\"}"
)





def summarize_turns(turns: List[AgentTurn]) -> str:
    latest = {t.agent: t for t in turns}
    lines = []
    for a in ["Deon", "Conse", "Virtue"]:
        if a in latest:
            s = latest[a].stance or "?"
            arg = latest[a].argument.replace("\n", " ")
            lines.append(f"{a}({s}): {arg}")
    return "\n".join(lines)


def has_valid_opponent(text: str, role: str, all_agents: List[str] = None) -> bool:
    """Check if text mentions an opponent (not self) and has actual content."""
    text_lower = text.lower()
    role_lower = role.lower()
    
    # Use provided agent list or default to the 3 default agents
    if all_agents:
        names = [a.lower() for a in all_agents]
    else:
        names = ["deon", "conse", "virtue"]
    
    mentioned_opponents = [n for n in names if n in text_lower and n != role_lower]
    
    # Must mention at least one opponent and have reasonable length
    return len(mentioned_opponents) > 0 and len(text.strip()) > 30

def latest_by_agent(turns: List["AgentTurn"]) -> dict:
    out = {}
    for t in turns:
        out[t.agent] = t
    return out

def short_quote(s: str, maxlen: int = 160) -> str:
    s = " ".join(s.split())  # collapse whitespace
    if len(s) <= maxlen:
        return s
    # pick a central slice so it looks like a real quote
    start = max(0, (len(s) // 2) - (maxlen // 2))
    return s[start:start+maxlen].strip()



# -------------------- ENDPOINTS --------------------
@app.post("/openings")
def openings(d: Dilemma):
    base = mk_base(d)

    def gen(role: str, sys: str):
        try:
            raw = call_ollama(sys, base + "\n" + OPENING_INSTRUCT, num_predict=480, temp=0.65)
            print(f"DEBUG {role} raw response: {raw[:200]}...")  # Debug output
            
            j = clamp_json(raw, {"stance": "A", "argument": f"[{role} failed to generate proper response]", "_raw": raw[:200]})
            print(f"DEBUG {role} parsed JSON: {j}")  # Debug output
            
            # If we got the fallback, try once more with different params
            if j.get("argument") == "—" or "[failed to generate]" in j.get("argument", ""):
                print(f"DEBUG {role} retrying...")
                raw2 = call_ollama(sys, base + "\n" + OPENING_INSTRUCT, num_predict=400, temp=0.8)
                j2 = clamp_json(raw2, j)
                if j2.get("argument", "—") not in ["—", "-"]:
                    j = j2
            
            return AgentTurn(agent=role, stance=j.get("stance","A"), argument=j.get("argument","—"))
        except Exception as e:
            print(f"DEBUG {role} exception: {str(e)}")  # Debug output
            return AgentTurn(agent=role, stance="A", argument=f"[{role} error: {str(e)[:100]}]")

    return {"turns": [gen("Deon", DEON_SYS).dict(),
                      gen("Conse", CONSE_SYS).dict(),
                      gen("Virtue", VIRTUE_SYS).dict()]}

# New endpoint for single agent response
@app.post("/agent/{agent_name}")
def single_agent(agent_name: str, d: Dilemma):
    base = mk_base(d)
    
    # Get system prompt for any agent (default or custom)
    sys_prompt = get_agent_system_prompt(agent_name)
    role = get_agent_display_name(agent_name)
    
    try:
        raw = call_ollama(sys_prompt, base + "\n" + OPENING_INSTRUCT, num_predict=150, temp=0.65)
        print(f"DEBUG {role} raw response: {raw[:200]}...")
        
        j = clamp_json(raw, {"stance": "A", "argument": f"[{role} failed to generate proper response]"})
        print(f"DEBUG {role} parsed JSON: {j}")
        
        if j.get("argument") == "—" or "[failed to generate]" in j.get("argument", ""):
            print(f"DEBUG {role} retrying...")
            raw2 = call_ollama(sys_prompt, base + "\n" + OPENING_INSTRUCT, num_predict=150, temp=0.8)
            j2 = clamp_json(raw2, j)
            if j2.get("argument", "—") not in ["—", "-"]:
                j = j2
        
        return AgentTurn(agent=role, stance=j.get("stance","A"), argument=j.get("argument","—")).dict()
    except Exception as e:
        print(f"DEBUG {role} exception: {str(e)}")
        return AgentTurn(agent=role, stance="A", argument=f"[{role} error: {str(e)[:100]}]").dict()

@app.post("/continue")
def continue_round(t: Transcript):
    base = mk_base(t.dilemma)
    latest = latest_by_agent(t.turns)
    
    # Get all agent names from the transcript (supports custom agents)
    all_agent_names = list(set(turn.agent for turn in t.turns))

    def respond(role: str, sys: str = None):
        # Get system prompt if not provided
        if sys is None:
            sys = get_agent_system_prompt(role)
        # Build explicit opponent choices from ALL agents in the debate (not just defaults)
        opponents = [name for name in all_agent_names if name in latest and name != role]
        
        # Build a cleaner summary
        opp_lines = []
        for name in opponents:
            arg_preview = latest[name].argument[:80].replace("\n", " ")
            opp_lines.append(f"{name}: {arg_preview}...")

        summary_for_user = "\n".join(opp_lines) if opp_lines else "No opponents to address."

        # Shorter, more direct prompt
        prompt = (
            f"You are {role}. Opponents said:\n{summary_for_user}\n\n"
            f"Pick ONE opponent ({', '.join(opponents)}) and respond in 2-3 sentences.\n"
            f"Start with their name + comma. Be direct and concise.\n"
            'JSON: {"stance":"A or B","argument":"Name, your brief response..."}'
        )

        # first try
        raw = call_ollama(sys, prompt, num_predict=200, temp=0.65)
        j = clamp_json(raw, {"stance": "same", "argument": "—"})
        arg = j.get("argument", "—").strip()

        # validate: must mention opponent and have content; else retry
        if (arg in ["—", "-", ""]) or (not has_valid_opponent(arg, role, all_agent_names)):
            retry_prompt = (
                f"You are {role}. Respond to {opponents[0] if opponents else 'opponent'}.\n"
                f"Start with: \"{opponents[0] if opponents else 'Opponent'}, \"\n"
                f"Write 2-3 sentences max. Be concise.\n"
                'JSON: {"stance":"A","argument":"Name, your response..."}'
            )
            raw2 = call_ollama(sys, retry_prompt, num_predict=180, temp=0.7)
            j2 = clamp_json(raw2, {"stance": "same", "argument": "—"})
            if j2.get("argument", "—") not in ["—", "-", ""]:
                j = j2
                arg = j.get("argument", "—").strip()

        prev = next((x.stance for x in reversed(t.turns) if x.agent == role and x.stance), None)
        raw_stance = j.get("stance", "same")
        
        # Clean and validate stance - only allow A, B, or same
        stance = str(raw_stance).strip().upper()
        if stance not in ["A", "B", "SAME"]:
            if "A" in stance and "B" not in stance:
                stance = "A"
            elif "B" in stance and "A" not in stance:
                stance = "B"
            else:
                stance = "SAME"
        
        final_stance = prev if stance == "SAME" else stance
        return AgentTurn(agent=role, stance=final_stance, argument=arg)

    # Use all agents from the transcript (works for both default and custom agents)
    return {"turns": [respond(agent_name).dict() for agent_name in all_agent_names]}

@app.post("/judge")
def judge(t: Transcript):
    judge_input = {"dilemma": t.dilemma.dict(), "transcript": [x.dict() for x in t.turns]}
    raw = call_ollama(JUDGE_SYS, json.dumps(judge_input), num_predict=600, temp=0.25)
    print(f"DEBUG Judge raw response: {raw[:500]}...")
    verdict = clamp_json(raw, {"scores":{}, "final_recommendation":"A","confidence":50,"verdict":"—"})
    print(f"DEBUG Judge parsed verdict: {verdict}")
    
    # Record debate metrics in background
    try:
        transcript_dict = {"dilemma": t.dilemma.dict(), "turns": [x.dict() for x in t.turns]}
        metrics_service.record_debate(transcript_dict, verdict)
    except Exception as e:
        print(f"Failed to record metrics: {e}")
        # Don't fail the request if metrics recording fails
    
    # Save debate to history
    try:
        debate_history_service.save_debate(transcript_dict, verdict)
    except Exception as e:
        print(f"Failed to save debate history: {e}")
        # Don't fail the request if history saving fails
    
    return verdict

# -------------------- INDIVIDUAL AGENT ENDPOINTS --------------------

@app.post("/agent/{agent_name}")
def get_agent_response(agent_name: str, dilemma: Dilemma):
    """Get response from any agent (default or custom)"""
    try:
        # Get the appropriate system prompt
        sys_prompt = get_agent_system_prompt(agent_name)
        
        # Get display name for the response
        display_name = get_agent_display_name(agent_name)
        
        # Generate response using the same logic as the opening round
        base = mk_base(dilemma)
        
        raw = call_ollama(sys_prompt, base + "\n" + OPENING_INSTRUCT, num_predict=300, temp=0.65)
        print(f"DEBUG {display_name} raw response: {raw[:300]}...")
        
        j = clamp_json(raw, {"stance": "A", "argument": f"[{display_name} failed to generate proper response]"})
        print(f"DEBUG {display_name} parsed JSON: {j}")
        
        if j.get("argument") == "—" or "[failed to generate]" in j.get("argument", ""):
            print(f"DEBUG {display_name} retrying...")
            raw2 = call_ollama(sys_prompt, base + "\n" + OPENING_INSTRUCT, num_predict=250, temp=0.8)
            j2 = clamp_json(raw2, j)
            if j2.get("argument", "—") not in ["—", "-"]:
                j = j2
        
        return AgentTurn(agent=display_name, stance=j.get("stance","A"), argument=j.get("argument","—")).dict()
        
    except Exception as e:
        print(f"DEBUG {agent_name} exception: {str(e)}")
        return AgentTurn(agent=agent_name, stance="A", argument=f"[{agent_name} error: {str(e)[:100]}]").dict()

# -------------------- CUSTOM AGENT ENDPOINTS --------------------

@app.post("/api/agents/create")
def create_custom_agent(request: AgentCreationRequest):
    """Create a new custom agent with AI enhancement"""
    try:
        # Enhance the description with agent name
        enhancement = enhancement_service.enhance_agent_description(request.description, request.name)
        
        # Generate system prompt
        system_prompt = enhancement_service.generate_system_prompt(
            enhancement.enhanced_prompt, 
            request.name
        )
        
        # Create the agent
        agent = agent_service.create_agent(
            request, 
            enhancement.enhanced_prompt, 
            system_prompt
        )
        
        return {
            "agent": agent.dict(),
            "enhancement": enhancement.dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")

@app.get("/api/agents")
def list_agents(public_only: bool = True, search: Optional[str] = None, limit: int = 50):
    """List all available agents"""
    try:
        agents = agent_service.list_agents(public_only, search, limit)
        return {"agents": [agent.dict() for agent in agents]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")

@app.get("/api/agents/all")
def get_all_available_agents():
    """Get all agents (default + custom) in unified format"""
    try:
        agents = agent_service.get_all_available_agents()
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")

@app.get("/api/agents/{agent_id}")
def get_agent(agent_id: str):
    """Get a specific agent by ID"""
    try:
        agent = agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"agent": agent.dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent: {str(e)}")

@app.put("/api/agents/{agent_id}")
def update_agent(agent_id: str, request: AgentUpdateRequest):
    """Update an existing agent"""
    try:
        enhanced_prompt = None
        system_prompt = None
        
        # Get existing agent to get name if not provided
        existing_agent = agent_service.get_agent(agent_id)
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # If description is being updated, re-enhance it
        if request.description is not None:
            agent_name = request.name if request.name else existing_agent.name
            enhancement = enhancement_service.enhance_agent_description(request.description, agent_name)
            enhanced_prompt = enhancement.enhanced_prompt
            system_prompt = enhancement_service.generate_system_prompt(
                enhanced_prompt, 
                agent_name
            )
        
        agent = agent_service.update_agent(agent_id, request, enhanced_prompt, system_prompt)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {"agent": agent.dict()}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update agent: {str(e)}")

@app.delete("/api/agents/{agent_id}")
def delete_agent(agent_id: str):
    """Delete an agent"""
    try:
        success = agent_service.delete_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"message": "Agent deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete agent: {str(e)}")

@app.post("/api/enhance")
def enhance_description(request: dict):
    """Enhance an agent description"""
    try:
        description = request.get("description", "")
        agent_name = request.get("agent_name", "Agent")
        
        if not description or len(description) < 50:
            raise HTTPException(status_code=400, detail="Description must be at least 50 characters")
        
        if not agent_name or not agent_name.strip():
            agent_name = "Agent"
        
        enhancement = enhancement_service.enhance_agent_description(description, agent_name.strip())
        return enhancement.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enhance description: {str(e)}")

@app.post("/api/agents/{agent_id}/regenerate")
def regenerate_agent_prompt(agent_id: str):
    """Regenerate the enhanced prompt for an existing agent"""
    try:
        agent = agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Re-enhance the original description with agent name
        enhancement = enhancement_service.enhance_agent_description(agent.description, agent.name)
        system_prompt = enhancement_service.generate_system_prompt(
            enhancement.enhanced_prompt, 
            agent.name
        )
        
        # Update the agent
        update_request = AgentUpdateRequest()
        updated_agent = agent_service.update_agent(
            agent_id, 
            update_request, 
            enhancement.enhanced_prompt, 
            system_prompt
        )
        
        return {
            "agent": updated_agent.dict(),
            "enhancement": enhancement.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate agent: {str(e)}")

# -------------------- CUSTOM AGENT DEBATE INTEGRATION --------------------

def get_agent_system_prompt(agent_name: str) -> str:
    """Get system prompt for any agent (default or custom)"""
    # Check if it's a default agent
    if agent_name.lower() == "deon":
        return DEON_SYS
    elif agent_name.lower() == "conse":
        return CONSE_SYS
    elif agent_name.lower() == "virtue":
        return VIRTUE_SYS
    else:
        # Try to find custom agent by ID first
        agent = agent_service.get_agent(agent_name)
        if agent:
            agent_service.increment_usage(agent_name)
            return agent.system_prompt
        
        # Try to find by name (for when display name is passed instead of ID)
        agent = agent_service.get_agent_by_name(agent_name)
        if agent:
            agent_service.increment_usage(agent.id)
            return agent.system_prompt
        
        # Fallback to default if not found
        print(f"WARNING: Agent '{agent_name}' not found, using default Deon prompt")
        return DEON_SYS

def get_agent_display_name(agent_identifier: str) -> str:
    """Get display name for any agent"""
    # Check if it's a default agent
    if agent_identifier.lower() in ["deon", "conse", "virtue"]:
        return agent_identifier.capitalize()
    else:
        # Try to find custom agent by ID
        agent = agent_service.get_agent(agent_identifier)
        if agent:
            return agent.name
        
        # Try to find by name
        agent = agent_service.get_agent_by_name(agent_identifier)
        if agent:
            return agent.name
            
        return agent_identifier

# -------------------- METRICS ENDPOINTS --------------------

@app.get("/api/metrics")
def get_all_debate_metrics():
    """Get all recorded debate metrics"""
    try:
        metrics = metrics_service.get_all_metrics()
        return {"metrics": metrics, "count": len(metrics)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@app.get("/api/metrics/summary")
def get_metrics_summary():
    """Get aggregate statistics across all debates"""
    try:
        summary = metrics_service.get_summary_stats()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

# -------------------- DEBATE HISTORY ENDPOINTS --------------------

@app.get("/api/debates")
def get_debate_history(limit: int = 50):
    """Get all debate history"""
    try:
        debates = debate_history_service.get_all_debates(limit)
        return {"debates": debates, "count": len(debates)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get debate history: {str(e)}")

@app.get("/api/debates/{debate_id}")
def get_debate(debate_id: str):
    """Get a specific debate by ID"""
    try:
        debate = debate_history_service.get_debate_by_id(debate_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
        return {"debate": debate}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get debate: {str(e)}")

@app.delete("/api/debates/{debate_id}")
def delete_debate(debate_id: str):
    """Delete a debate from history"""
    try:
        success = debate_history_service.delete_debate(debate_id)
        if not success:
            raise HTTPException(status_code=404, detail="Debate not found")
        return {"message": "Debate deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete debate: {str(e)}")

@app.get("/api/debates/stats")
def get_debate_stats():
    """Get statistics about debate history"""
    try:
        stats = debate_history_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# -------------------- DEBATE TEMPLATES ENDPOINTS --------------------

# Get the directory where main.py is located
BASE_DIR = Path(__file__).resolve().parent

@app.get("/api/templates")
def get_debate_templates():
    """Get all debate templates from the library"""
    try:
        templates_path = BASE_DIR / "data" / "debate_templates.json"
        if templates_path.exists():
            with open(templates_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            return {"templates": templates, "count": len(templates)}
        return {"templates": [], "count": 0, "debug": str(templates_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load templates: {str(e)}")

@app.get("/api/templates/{slug}")
def get_debate_template(slug: str):
    """Get a specific debate template by slug"""
    try:
        templates_path = BASE_DIR / "data" / "debate_templates.json"
        if templates_path.exists():
            with open(templates_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            for template in templates:
                if template.get("slug") == slug:
                    return {"template": template}
        raise HTTPException(status_code=404, detail="Template not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load template: {str(e)}")


# -------------------- DEBATE SUBMISSION ENDPOINTS --------------------

class DebateSubmission(BaseModel):
    """Model for debate submission"""
    title: str = Field(..., min_length=5, max_length=200)
    context: str = Field(..., min_length=20, max_length=2000)
    option_a: str = Field(..., min_length=10, max_length=500)
    option_b: str = Field(..., min_length=10, max_length=500)

@app.post("/api/debates/submit")
def submit_debate(submission: DebateSubmission):
    """
    Submit a custom debate to the library with semantic deduplication.
    
    This endpoint:
    1. Validates the debate format
    2. Checks for semantic duplicates in the library
    3. Adds unique debates to the library
    4. Returns appropriate response (added or duplicate found)
    """
    try:
        # Convert to dict
        debate = {
            'title': submission.title,
            'context': submission.context,
            'option_a': submission.option_a,
            'option_b': submission.option_b
        }
        
        print(f"DEBUG: Submitting debate: {submission.title}")
        
        # Submit through deduplication service
        result = deduplication_service.submit_custom_debate(debate)
        
        print(f"DEBUG: Result - Success: {result.success}, Duplicate: {result.is_duplicate}, Message: {result.message}")
        
        # Return appropriate status code
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        result_dict = result.to_dict()
        print(f"DEBUG: Returning result: {result_dict}")
        return result_dict
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Exception in submit_debate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit debate: {str(e)}")

# -------------------- DEBATE EXPORT & SHARING ENDPOINTS --------------------

@app.get("/api/debates/{debate_id}/export/markdown")
def export_debate_markdown(debate_id: str):
    """Export a debate as markdown format"""
    try:
        debate = debate_history_service.get_debate_by_id(debate_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
        
        # Build markdown content
        transcript = debate.get('transcript', {})
        verdict = debate.get('verdict', {})
        dilemma = transcript.get('dilemma', {})
        turns = transcript.get('turns', [])
        
        md_content = f"""# {dilemma.get('title', 'Ethical Debate')}

## Dilemma

**Option A:** {dilemma.get('A', 'N/A')}

**Option B:** {dilemma.get('B', 'N/A')}

**Context:** {dilemma.get('constraints', 'N/A')}

---

## Debate Transcript

"""
        
        # Add all turns
        for i, turn in enumerate(turns, 1):
            agent = turn.get('agent', 'Unknown')
            stance = turn.get('stance', '?')
            argument = turn.get('argument', '')
            md_content += f"### {agent} (Position: {stance})\n\n{argument}\n\n"
        
        md_content += "---\n\n## Verdict\n\n"
        
        # Add verdict
        final_rec = verdict.get('final_recommendation', 'N/A')
        confidence = verdict.get('confidence', 0)
        verdict_text = verdict.get('verdict', 'No verdict available')
        
        md_content += f"**Winner:** Option {final_rec}\n\n"
        md_content += f"**Confidence:** {confidence}%\n\n"
        md_content += f"**Reasoning:** {verdict_text}\n\n"
        
        # Add scores
        scores = verdict.get('scores', {})
        if scores:
            md_content += "### Ethical Dimension Scores\n\n"
            for option in ['option_a', 'option_b']:
                option_label = option.replace('_', ' ').title()
                md_content += f"**{option_label}:**\n"
                option_scores = scores.get(option, {})
                for dimension, score in option_scores.items():
                    dim_label = dimension.replace('_', ' ').title()
                    md_content += f"- {dim_label}: {score}/2\n"
                md_content += "\n"
        
        md_content += f"\n---\n\n*Exported from MirrorMind AI on {debate.get('date', 'Unknown date')}*\n"
        
        return {
            "format": "markdown",
            "content": md_content,
            "filename": f"debate_{debate_id}.md"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export debate: {str(e)}")

@app.get("/api/debates/{debate_id}/export/json")
def export_debate_json(debate_id: str):
    """Export a debate as JSON format"""
    try:
        debate = debate_history_service.get_debate_by_id(debate_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
        
        return {
            "format": "json",
            "content": json.dumps(debate, indent=2),
            "filename": f"debate_{debate_id}.json",
            "data": debate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export debate: {str(e)}")

@app.get("/api/debates/{debate_id}/share")
def get_shareable_link(debate_id: str):
    """Get a shareable link for a debate"""
    try:
        debate = debate_history_service.get_debate_by_id(debate_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
        
        # Generate shareable URL (frontend will handle the routing)
        base_url = os.getenv("FRONTEND_URL", "https://mirror-mind-ai.vercel.app")
        share_url = f"{base_url}/debate/{debate_id}"
        
        return {
            "debate_id": debate_id,
            "share_url": share_url,
            "title": debate.get('title', 'Ethical Debate'),
            "date": debate.get('date', '')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate share link: {str(e)}")

@app.get("/api/debates/shared/{debate_id}")
def get_shared_debate(debate_id: str):
    """Get a debate by shareable ID (public endpoint)"""
    try:
        debate = debate_history_service.get_debate_by_id(debate_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
        
        return {"debate": debate}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get shared debate: {str(e)}")
