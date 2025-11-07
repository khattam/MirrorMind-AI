# backend/services/debate_history_service.py
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from uuid import uuid4


class DebateHistoryService:
    def __init__(self, storage_path: str = "data"):
        self.storage_path = Path(storage_path)
        self.history_file = self.storage_path / "debate_history.json"
        
        # Create storage directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize file if it doesn't exist
        if not self.history_file.exists():
            self._save_history([])

    def _load_history(self) -> List[dict]:
        """Load debate history from JSON file"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_history(self, history: List[dict]) -> None:
        """Save debate history to JSON file"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False, default=str)

    def save_debate(self, transcript: dict, verdict: dict) -> dict:
        """Save a completed debate to history"""
        history = self._load_history()
        
        debate_entry = {
            "id": str(uuid4()),
            "title": transcript.get("dilemma", {}).get("title", "Untitled Debate"),
            "date": datetime.now().isoformat(),
            "timestamp": datetime.now().timestamp(),
            "transcript": transcript,
            "verdict": verdict,
            "recommendation": verdict.get("final_recommendation", "Unknown"),
            "confidence": verdict.get("confidence", 0)
        }
        
        # Add to beginning of history (most recent first)
        history.insert(0, debate_entry)
        
        # Keep only last 100 debates to avoid file getting too large
        history = history[:100]
        
        self._save_history(history)
        
        return debate_entry

    def get_all_debates(self, limit: int = 50) -> List[dict]:
        """Get all debates, most recent first"""
        history = self._load_history()
        return history[:limit]

    def get_debate_by_id(self, debate_id: str) -> Optional[dict]:
        """Get a specific debate by ID"""
        history = self._load_history()
        for debate in history:
            if debate.get("id") == debate_id:
                return debate
        return None

    def delete_debate(self, debate_id: str) -> bool:
        """Delete a debate from history"""
        history = self._load_history()
        original_length = len(history)
        
        history = [d for d in history if d.get("id") != debate_id]
        
        if len(history) < original_length:
            self._save_history(history)
            return True
        
        return False

    def clear_all_history(self) -> bool:
        """Clear all debate history (use with caution)"""
        self._save_history([])
        return True

    def get_stats(self) -> dict:
        """Get statistics about debate history"""
        history = self._load_history()
        
        if not history:
            return {
                "total_debates": 0,
                "most_recent": None,
                "oldest": None
            }
        
        return {
            "total_debates": len(history),
            "most_recent": history[0].get("date") if history else None,
            "oldest": history[-1].get("date") if history else None,
            "topics": [d.get("title") for d in history[:10]]  # Last 10 topics
        }
