"""
Debate Metrics Service
Tracks and exports debate statistics to JSON file
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


class MetricsService:
    def __init__(self, storage_path: str = "data/debate_metrics.json"):
        self.storage_path = storage_path
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Create storage directory and file if they don't exist"""
        Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({"debates": []}, f)
    
    def _load_metrics(self) -> Dict:
        """Load metrics from file"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"debates": []}
    
    def _save_metrics(self, data: Dict):
        """Save metrics to file"""
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_debate_metrics(self, transcript: Dict, verdict: Dict) -> Dict[str, Any]:
        """
        Calculate comprehensive metrics for a debate
        
        Args:
            transcript: Debate transcript with dilemma and turns
            verdict: Judge's verdict with scores
        
        Returns:
            Dictionary with all calculated metrics
        """
        turns = transcript.get("turns", [])
        dilemma = transcript.get("dilemma", {})
        
        # Basic counts
        total_turns = len(turns)
        agents = list(set(turn.get("agent") for turn in turns))
        num_agents = len(agents)
        
        # Word count analysis
        total_words = 0
        agent_word_counts = {}
        agent_turn_counts = {}
        
        for turn in turns:
            agent = turn.get("agent")
            argument = turn.get("argument", "")
            word_count = len(argument.split())
            
            total_words += word_count
            agent_word_counts[agent] = agent_word_counts.get(agent, 0) + word_count
            agent_turn_counts[agent] = agent_turn_counts.get(agent, 0) + 1
        
        # Calculate averages
        avg_words_per_turn = total_words / total_turns if total_turns > 0 else 0
        avg_words_per_agent = {
            agent: agent_word_counts[agent] / agent_turn_counts[agent]
            for agent in agents
        }
        
        # Stance analysis
        stance_changes = {}
        for agent in agents:
            agent_turns = [t for t in turns if t.get("agent") == agent]
            stances = [t.get("stance") for t in agent_turns if t.get("stance")]
            stance_changes[agent] = len(set(stances)) - 1 if len(stances) > 1 else 0
        
        # Verdict analysis
        final_recommendation = verdict.get("final_recommendation", "Unknown")
        confidence = verdict.get("confidence", 0)
        scores = verdict.get("scores", {})
        
        # Calculate debate "intensity" (total words / number of turns)
        intensity = avg_words_per_turn
        
        # Determine most verbose agent
        most_verbose_agent = max(agent_word_counts.items(), key=lambda x: x[1])[0] if agent_word_counts else None
        
        return {
            "debate_id": f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "dilemma_title": dilemma.get("title", "Untitled"),
            "total_turns": total_turns,
            "total_words": total_words,
            "num_agents": num_agents,
            "agents": agents,
            "avg_words_per_turn": round(avg_words_per_turn, 2),
            "avg_words_per_agent": {k: round(v, 2) for k, v in avg_words_per_agent.items()},
            "agent_word_counts": agent_word_counts,
            "agent_turn_counts": agent_turn_counts,
            "stance_changes": stance_changes,
            "most_verbose_agent": most_verbose_agent,
            "intensity_score": round(intensity, 2),
            "final_recommendation": final_recommendation,
            "confidence": confidence,
            "ethical_scores": scores,
        }
    
    def record_debate(self, transcript: Dict, verdict: Dict) -> Dict[str, Any]:
        """
        Record a completed debate with all metrics
        
        Args:
            transcript: Full debate transcript
            verdict: Judge's verdict
        
        Returns:
            Calculated metrics for the debate
        """
        metrics = self.calculate_debate_metrics(transcript, verdict)
        
        # Load existing data
        data = self._load_metrics()
        
        # Add new debate
        data["debates"].append(metrics)
        
        # Save updated data
        self._save_metrics(data)
        
        return metrics
    
    def get_all_metrics(self) -> List[Dict]:
        """Get all recorded debate metrics"""
        data = self._load_metrics()
        return data.get("debates", [])
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get aggregate statistics across all debates
        
        Returns:
            Summary statistics
        """
        debates = self.get_all_metrics()
        
        if not debates:
            return {
                "total_debates": 0,
                "total_words": 0,
                "avg_debate_length": 0,
                "most_common_winner": None,
                "agent_usage": {}
            }
        
        total_debates = len(debates)
        total_words = sum(d.get("total_words", 0) for d in debates)
        total_turns = sum(d.get("total_turns", 0) for d in debates)
        
        # Count recommendations
        recommendations = [d.get("final_recommendation") for d in debates]
        most_common_winner = max(set(recommendations), key=recommendations.count) if recommendations else None
        
        # Agent usage statistics
        agent_usage = {}
        for debate in debates:
            for agent in debate.get("agents", []):
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
        
        return {
            "total_debates": total_debates,
            "total_words": total_words,
            "total_turns": total_turns,
            "avg_debate_length": round(total_turns / total_debates, 2),
            "avg_words_per_debate": round(total_words / total_debates, 2),
            "most_common_winner": most_common_winner,
            "agent_usage": agent_usage,
            "most_used_agent": max(agent_usage.items(), key=lambda x: x[1])[0] if agent_usage else None
        }
