# backend/main.py
import json
import requests
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import re

# -------------------- OLLAMA CONFIG --------------------
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use cloud API for cloud models, local for local models  
MODEL = "qwen2.5:7b-instruct-q4_K_M"  # Back to local model for stability
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

# Determine API endpoint based on model
if MODEL.endswith("-cloud"):
    OLLAMA_API = "https://ollama.com/api/generate"
else:
    OLLAMA_API = "http://localhost:11434/api/generate"

def call_ollama(system_prompt: str, user_prompt: str, num_predict: int = 400, temp: float = 0.7, top_p: float = 0.9, repeat_penalty: float = 1.1) -> str:
    payload = {
        "model": MODEL,
        "prompt": f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n",
        "options": {
            "temperature": temp,
            "top_p": top_p,
            "repeat_penalty": repeat_penalty,
            "num_predict": num_predict
        },
        "stream": False,
    }
    
    # Add authentication headers for cloud models
    headers = {
        "Content-Type": "application/json"
    }
    
    # Only add auth for cloud models
    if MODEL.endswith("-cloud") and OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"
   
    r = requests.post(OLLAMA_API, json=payload, headers=headers, timeout=240)
    r.raise_for_status()
    return r.json().get("response", "").strip()



import re

def clamp_json(s: str, fallback: dict) -> dict:
    """
    Robust JSON extractor:
    1) prefer ```json ... ``` fenced blocks
    2) else scan all {...} objects and return the first that has 'stance' and 'argument'
    3) else return the first valid {...}
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
            if isinstance(j, dict) and "stance" in j and "argument" in j:
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
    "assign each agent scores from 0–2 for harm_minimization, rule_consistency, autonomy_respect, honesty, and fairness. "
    "Then choose which option (A or B) best aligns with the overall ethical balance. "
    "Return a JSON object: {\"scores\":{...},\"final_recommendation\":\"A|B\",\"confidence\":0-100,\"verdict\":\"...\"}"
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

# Initialize services
agent_service = AgentService()
enhancement_service = EnhancementService()
metrics_service = MetricsService()

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
def root():
    return {"message": "MirrorMinds backend is running!"}

# -------------------- HELPERS --------------------
def mk_base(d: Dilemma) -> str:
    return (
        f"DILEMMA\nTitle: {d.title}\n"
        f"Option A: {d.A}\nOption B: {d.B}\n"
        f"Constraints: {d.constraints}\n"
    )

OPENING_INSTRUCT = (
    "Opening: Choose A or B, and write a clear paragraph (5–8 sentences) that:\n"
    "• names your core ethical concept (rule, outcome, or virtue)\n"
    "• gives one concrete example or consequence\n"
    "• stays consistent with your moral framework\n"
    "Respond JSON only: {\"stance\":\"A|B\",\"argument\":\"<paragraph>\"}"
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


def has_valid_opponent(text: str, role: str) -> bool:
    """Check if text mentions an opponent (not self) and has actual content."""
    text_lower = text.lower()
    
    # Check for opponent names (case insensitive)
    names = ["deon", "conse", "virtue"]
    role_lower = role.lower()
    
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
        raw = call_ollama(sys_prompt, base + "\n" + OPENING_INSTRUCT, num_predict=300, temp=0.65)
        print(f"DEBUG {role} raw response: {raw[:300]}...")  # Debug output
        
        j = clamp_json(raw, {"stance": "A", "argument": f"[{role} failed to generate proper response]"})
        print(f"DEBUG {role} parsed JSON: {j}")  # Debug output
        
        if j.get("argument") == "—" or "[failed to generate]" in j.get("argument", ""):
            print(f"DEBUG {role} retrying...")
            raw2 = call_ollama(sys_prompt, base + "\n" + OPENING_INSTRUCT, num_predict=250, temp=0.8)
            j2 = clamp_json(raw2, j)
            if j2.get("argument", "—") not in ["—", "-"]:
                j = j2
        
        return AgentTurn(agent=role, stance=j.get("stance","A"), argument=j.get("argument","—")).dict()
    except Exception as e:
        print(f"DEBUG {role} exception: {str(e)}")  # Debug output
        return AgentTurn(agent=role, stance="A", argument=f"[{role} error: {str(e)[:100]}]").dict()

@app.post("/continue")
def continue_round(t: Transcript):
    base = mk_base(t.dilemma)
    latest = latest_by_agent(t.turns)

    def respond(role: str, sys: str = None):
        # Get system prompt if not provided
        if sys is None:
            sys = get_agent_system_prompt(role)
        # Build explicit opponent choices (cannot be self)
        opponents = [name for name in ["Deon", "Conse", "Virtue"] if name in latest and name != role]
        
        # Build a cleaner summary
        opp_lines = []
        for name in opponents:
            arg_preview = latest[name].argument[:100].replace("\n", " ")
            opp_lines.append(f"{name}: {arg_preview}...")

        summary_for_user = "\n".join(opp_lines) if opp_lines else "No opponents to address."

        # Very explicit prompt with clear example
        prompt = (
            f"You are {role}. Here are your opponents' latest arguments:\n\n"
            + summary_for_user + "\n\n"
            f"TASK: Pick ONE opponent (choose from: {', '.join(opponents)}) and respond to them.\n\n"
            f"CRITICAL: Your argument MUST start with the opponent's name followed by a comma.\n"
            f"Example format: 'Virtue, I disagree with your point because...'\n\n"
            f"Write 4-6 sentences explaining your position from your ethical framework.\n\n"
            'Return JSON: {"stance":"A","argument":"OpponentName, your response here..."}'
        )

        # first try
        raw = call_ollama(sys, prompt, num_predict=400, temp=0.65)
        j = clamp_json(raw, {"stance": "same", "argument": "—"})
        arg = j.get("argument", "—").strip()

        # validate: must mention opponent and have content; else retry with VERY explicit format
        if (arg in ["—", "-", ""]) or (not has_valid_opponent(arg, role)):
            # Force the format by being extremely explicit
            retry_prompt = (
                f"You are {role}. Respond to ONE of these opponents:\n"
                + "\n".join([f"- {name}" for name in opponents]) + "\n\n"
                f"Your response MUST begin with one of these exact phrases:\n"
                + "\n".join([f'- "{name}, "' for name in opponents]) + "\n\n"
                f"Then continue with your argument (4-6 sentences).\n\n"
                f'Example: "Virtue, I believe your focus on character overlooks the practical consequences..."\n\n'
                'JSON format: {"stance":"A","argument":"OpponentName, your full response..."}'
            )
            raw2 = call_ollama(sys, retry_prompt, num_predict=350, temp=0.7)
            j2 = clamp_json(raw2, {"stance": "same", "argument": "—"})
            if j2.get("argument", "—") not in ["—", "-", ""]:
                j = j2
                arg = j.get("argument", "—").strip()

        prev = next((x.stance for x in reversed(t.turns) if x.agent == role and x.stance), None)
        raw_stance = j.get("stance", "same")
        
        # Clean and validate stance - only allow A, B, or same
        stance = str(raw_stance).strip().upper()
        if stance not in ["A", "B", "SAME"]:
            # Try to extract A or B from the stance string
            if "A" in stance and "B" not in stance:
                stance = "A"
            elif "B" in stance and "A" not in stance:
                stance = "B"
            else:
                stance = "SAME"
        
        final_stance = prev if stance == "SAME" else stance
        return AgentTurn(agent=role, stance=final_stance, argument=arg)

    # Get unique agent names from the transcript
    agent_names = list(set(turn.agent for turn in t.turns))
    
    # If we have the default 3 agents, use them
    if len(agent_names) == 3 and all(name in ["Deon", "Conse", "Virtue"] for name in agent_names):
        return {"turns": [respond("Deon").dict(),
                          respond("Conse").dict(),
                          respond("Virtue").dict()]}
    else:
        # Use the agents from the transcript
        return {"turns": [respond(agent_name).dict() for agent_name in agent_names]}

@app.post("/judge")
def judge(t: Transcript):
    judge_input = {"dilemma": t.dilemma.dict(), "transcript": [x.dict() for x in t.turns]}
    raw = call_ollama(JUDGE_SYS, json.dumps(judge_input), num_predict=280, temp=0.25)
    verdict = clamp_json(raw, {"scores":{}, "final_recommendation":"A","confidence":50,"verdict":"—"})
    
    # Record debate metrics in background
    try:
        transcript_dict = {"dilemma": t.dilemma.dict(), "turns": [x.dict() for x in t.turns]}
        metrics_service.record_debate(transcript_dict, verdict)
    except Exception as e:
        print(f"Failed to record metrics: {e}")
        # Don't fail the request if metrics recording fails
    
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
        # Enhance the description
        enhancement = enhancement_service.enhance_agent_description(request.description)
        
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
        
        # If description is being updated, re-enhance it
        if request.description is not None:
            enhancement = enhancement_service.enhance_agent_description(request.description)
            enhanced_prompt = enhancement.enhanced_prompt
            system_prompt = enhancement_service.generate_system_prompt(
                enhanced_prompt, 
                request.name or "Agent"
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
        if not description or len(description) < 50:
            raise HTTPException(status_code=400, detail="Description must be at least 50 characters")
        
        enhancement = enhancement_service.enhance_agent_description(description)
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
        
        # Re-enhance the original description
        enhancement = enhancement_service.enhance_agent_description(agent.description)
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
        # Try to find custom agent
        agent = agent_service.get_agent(agent_name)
        if agent:
            # Increment usage count
            agent_service.increment_usage(agent_name)
            return agent.system_prompt
        else:
            # Fallback to default if not found
            return DEON_SYS

def get_agent_display_name(agent_identifier: str) -> str:
    """Get display name for any agent"""
    # Check if it's a default agent
    if agent_identifier.lower() in ["deon", "conse", "virtue"]:
        return agent_identifier.capitalize()
    else:
        # Try to find custom agent
        agent = agent_service.get_agent(agent_identifier)
        return agent.name if agent else agent_identifier

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
