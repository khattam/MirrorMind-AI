# backend/services/agent_service.py
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from models.custom_agent import CustomAgent, AgentRating, AgentCreationRequest, AgentUpdateRequest


class AgentService:
    def __init__(self, storage_path: str = "data/agents"):
        self.storage_path = Path(storage_path)
        self.agents_file = self.storage_path / "custom_agents.json"
        self.ratings_file = self.storage_path / "agent_ratings.json"
        
        # Create storage directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize files if they don't exist
        if not self.agents_file.exists():
            self._save_agents({})
        if not self.ratings_file.exists():
            self._save_ratings({})

    def _load_agents(self) -> Dict[str, dict]:
        """Load agents from JSON file"""
        try:
            with open(self.agents_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_agents(self, agents: Dict[str, dict]) -> None:
        """Save agents to JSON file"""
        with open(self.agents_file, 'w', encoding='utf-8') as f:
            json.dump(agents, f, indent=2, ensure_ascii=False, default=str)

    def _load_ratings(self) -> Dict[str, dict]:
        """Load ratings from JSON file"""
        try:
            with open(self.ratings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_ratings(self, ratings: Dict[str, dict]) -> None:
        """Save ratings to JSON file"""
        with open(self.ratings_file, 'w', encoding='utf-8') as f:
            json.dump(ratings, f, indent=2, ensure_ascii=False, default=str)

    def create_agent(self, request: AgentCreationRequest, enhanced_prompt: str, system_prompt: str) -> CustomAgent:
        """Create a new custom agent"""
        # Check for duplicate names (including default agents)
        self._check_duplicate_name(request.name)
        
        agent = CustomAgent(
            name=request.name,
            avatar=request.avatar,
            description=request.description,
            enhanced_prompt=enhanced_prompt,
            system_prompt=system_prompt
        )
        
        # Load existing agents
        agents = self._load_agents()
        
        # Save agent
        agents[agent.id] = agent.dict()
        self._save_agents(agents)
        
        return agent
    
    def _check_duplicate_name(self, name: str) -> None:
        """Check if agent name already exists (custom or default)"""
        name_lower = name.lower().strip()
        
        # Check against default agents
        default_names = ["deon", "conse", "virtue"]
        if name_lower in default_names:
            raise ValueError(f"Agent name '{name}' conflicts with a default agent. Please choose a different name.")
        
        # Check against existing custom agents
        agents = self._load_agents()
        for existing_agent in agents.values():
            if existing_agent.get('name', '').lower().strip() == name_lower:
                raise ValueError(f"Agent with name '{name}' already exists. Please choose a different name.")

    def get_agent(self, agent_id: str) -> Optional[CustomAgent]:
        """Get a specific agent by ID"""
        agents = self._load_agents()
        agent_data = agents.get(agent_id)
        
        if agent_data:
            return CustomAgent(**agent_data)
        return None

    def get_agent_by_name(self, name: str) -> Optional[CustomAgent]:
        """Get a specific agent by name (case-insensitive)"""
        agents = self._load_agents()
        name_lower = name.lower().strip()
        
        for agent_data in agents.values():
            if agent_data.get('name', '').lower().strip() == name_lower:
                return CustomAgent(**agent_data)
        return None

    def list_agents(self, public_only: bool = True, search: Optional[str] = None, limit: int = 50) -> List[CustomAgent]:
        """List all agents with optional filtering"""
        agents = self._load_agents()
        agent_list = []
        
        for agent_data in agents.values():
            agent = CustomAgent(**agent_data)
            
            # Filter by public status
            if public_only and not agent.is_public:
                continue
            
            # Filter by search term
            if search:
                search_lower = search.lower()
                if (search_lower not in agent.name.lower() and 
                    search_lower not in agent.description.lower()):
                    continue
            
            agent_list.append(agent)
        
        # Sort by usage count and rating
        agent_list.sort(key=lambda a: (a.average_rating, a.usage_count), reverse=True)
        
        return agent_list[:limit]

    def update_agent(self, agent_id: str, request: AgentUpdateRequest, 
                    enhanced_prompt: Optional[str] = None, 
                    system_prompt: Optional[str] = None) -> Optional[CustomAgent]:
        """Update an existing agent"""
        agents = self._load_agents()
        
        if agent_id not in agents:
            return None
        
        agent_data = agents[agent_id]
        
        # Update fields if provided
        if request.name is not None:
            # Check for duplicate names (excluding current agent)
            for aid, existing_agent in agents.items():
                if (aid != agent_id and 
                    existing_agent.get('name', '').lower() == request.name.lower()):
                    raise ValueError(f"Agent with name '{request.name}' already exists")
            agent_data['name'] = request.name
        
        if request.avatar is not None:
            agent_data['avatar'] = request.avatar
        
        if request.description is not None:
            agent_data['description'] = request.description
        
        if enhanced_prompt is not None:
            agent_data['enhanced_prompt'] = enhanced_prompt
        
        if system_prompt is not None:
            agent_data['system_prompt'] = system_prompt
        
        # Save updated agents
        self._save_agents(agents)
        
        return CustomAgent(**agent_data)

    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent"""
        agents = self._load_agents()
        
        if agent_id in agents:
            del agents[agent_id]
            self._save_agents(agents)
            
            # Also delete associated ratings
            ratings = self._load_ratings()
            ratings = {rid: rating for rid, rating in ratings.items() 
                      if rating.get('agent_id') != agent_id}
            self._save_ratings(ratings)
            
            return True
        
        return False

    def increment_usage(self, agent_id: str) -> None:
        """Increment usage count for an agent"""
        agents = self._load_agents()
        
        if agent_id in agents:
            agents[agent_id]['usage_count'] = agents[agent_id].get('usage_count', 0) + 1
            self._save_agents(agents)

    def add_rating(self, rating: AgentRating) -> None:
        """Add a rating for an agent"""
        ratings = self._load_ratings()
        ratings[rating.id] = rating.dict()
        self._save_ratings(ratings)
        
        # Update agent's average rating
        self._update_agent_rating(rating.agent_id)

    def _update_agent_rating(self, agent_id: str) -> None:
        """Recalculate and update agent's average rating"""
        ratings = self._load_ratings()
        agent_ratings = [AgentRating(**rating) for rating in ratings.values() 
                        if rating.get('agent_id') == agent_id]
        
        if not agent_ratings:
            return
        
        # Calculate average of all rating criteria
        total_scores = []
        for rating in agent_ratings:
            avg_score = (rating.argument_quality + rating.consistency + 
                        rating.engagement + rating.overall_satisfaction) / 4
            total_scores.append(avg_score)
        
        average_rating = sum(total_scores) / len(total_scores)
        rating_count = len(agent_ratings)
        
        # Update agent data
        agents = self._load_agents()
        if agent_id in agents:
            agents[agent_id]['average_rating'] = round(average_rating, 2)
            agents[agent_id]['rating_count'] = rating_count
            self._save_agents(agents)

    def get_agent_ratings(self, agent_id: str) -> List[AgentRating]:
        """Get all ratings for a specific agent"""
        ratings = self._load_ratings()
        return [AgentRating(**rating) for rating in ratings.values() 
                if rating.get('agent_id') == agent_id]

    def get_default_agents(self) -> List[Dict[str, str]]:
        """Get the default agents (Deon, Conse, Virtue) in agent format"""
        return [
            {
                "id": "deon",
                "name": "Deon",
                "avatar": "⚖️",
                "description": "Deontologist who believes moral worth comes from following principles, duties, and rights. Prioritizes integrity, consent, fairness, and respect for universal rules.",
                "type": "default"
            },
            {
                "id": "conse", 
                "name": "Conse",
                "avatar": "◆",
                "description": "Consequentialist who evaluates actions purely by their outcomes. Rules are heuristics, not absolutes. Focuses on maximizing overall well-being.",
                "type": "default"
            },
            {
                "id": "virtue",
                "name": "Virtue", 
                "avatar": "✦",
                "description": "Virtue ethicist who focuses on character and human flourishing rather than strict rules or outcomes. Emphasizes virtues like honesty, compassion, and wisdom.",
                "type": "default"
            }
        ]

    def get_all_available_agents(self) -> List[Dict]:
        """Get all agents (default + custom) in a unified format"""
        all_agents = []
        
        # Add default agents
        all_agents.extend(self.get_default_agents())
        
        # Add custom agents
        custom_agents = self.list_agents(public_only=True)
        for agent in custom_agents:
            all_agents.append({
                "id": agent.id,
                "name": agent.name,
                "avatar": agent.avatar,
                "description": agent.description,
                "type": "custom",
                "rating": agent.average_rating,
                "usage_count": agent.usage_count
            })
        
        return all_agents