# backend/services/enhancement_service.py
import re
from typing import Dict, List
from models.custom_agent import EnhancementRequest
from main import call_ollama  # Import the existing Ollama function


class PromptAnalyzer:
    """Analyzes user descriptions for completeness and quality"""
    
    def analyze_description(self, description: str) -> Dict[str, float]:
        """Analyze description and return quality scores"""
        scores = {
            "clarity": self._score_clarity(description),
            "completeness": self._score_completeness(description),
            "specificity": self._score_specificity(description),
            "consistency": self._score_consistency(description)
        }
        return scores
    
    def _score_clarity(self, description: str) -> float:
        """Score clarity based on sentence structure and readability"""
        sentences = description.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        # Optimal sentence length is 15-20 words
        if 10 <= avg_sentence_length <= 25:
            clarity_score = 10.0
        else:
            clarity_score = max(0, 10 - abs(avg_sentence_length - 17.5) * 0.3)
        
        return min(10.0, clarity_score)
    
    def _score_completeness(self, description: str) -> float:
        """Score completeness based on presence of key elements"""
        description_lower = description.lower()
        
        # Key elements to look for
        elements = {
            "values": any(word in description_lower for word in 
                         ["believe", "value", "prioritize", "important", "care about"]),
            "reasoning": any(word in description_lower for word in 
                           ["because", "reason", "logic", "think", "consider"]),
            "examples": any(word in description_lower for word in 
                          ["example", "such as", "like", "including", "for instance"]),
            "personality": any(word in description_lower for word in 
                             ["compassionate", "logical", "firm", "gentle", "strict", "flexible"]),
            "decision_making": any(word in description_lower for word in 
                                 ["decision", "choose", "evaluate", "judge", "determine"])
        }
        
        present_elements = sum(elements.values())
        completeness_score = (present_elements / len(elements)) * 10
        
        return completeness_score
    
    def _score_specificity(self, description: str) -> float:
        """Score specificity based on concrete details vs vague terms"""
        description_lower = description.lower()
        
        # Vague terms that reduce specificity
        vague_terms = ["good", "bad", "important", "very", "really", "always", "never", "everything"]
        vague_count = sum(description_lower.count(term) for term in vague_terms)
        
        # Specific terms that increase specificity
        specific_indicators = ["specific", "particular", "exactly", "precisely", "namely"]
        specific_count = sum(description_lower.count(term) for term in specific_indicators)
        
        # Calculate specificity score
        word_count = len(description.split())
        vague_ratio = vague_count / max(word_count, 1)
        specific_ratio = specific_count / max(word_count, 1)
        
        specificity_score = max(0, 10 - (vague_ratio * 20) + (specific_ratio * 10))
        
        return min(10.0, specificity_score)
    
    def _score_consistency(self, description: str) -> float:
        """Score consistency based on coherent theme and no contradictions"""
        # Simple consistency check - look for contradictory terms
        description_lower = description.lower()
        
        contradictions = [
            (["always", "never"], ["sometimes", "occasionally"]),
            (["strict", "rigid"], ["flexible", "adaptable"]),
            (["emotional", "feeling"], ["logical", "rational"])
        ]
        
        contradiction_count = 0
        for group1, group2 in contradictions:
            has_group1 = any(term in description_lower for term in group1)
            has_group2 = any(term in description_lower for term in group2)
            if has_group1 and has_group2:
                contradiction_count += 1
        
        # Start with high consistency, reduce for contradictions
        consistency_score = max(0, 10 - (contradiction_count * 2))
        
        return consistency_score
    
    def generate_suggestions(self, description: str, scores: Dict[str, float]) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        if scores["completeness"] < 6:
            suggestions.append("Consider adding specific examples of what this agent would prioritize")
            suggestions.append("Describe how this agent makes decisions or evaluates situations")
        
        if scores["clarity"] < 6:
            suggestions.append("Try using shorter, clearer sentences to describe the agent")
            suggestions.append("Break down complex ideas into simpler statements")
        
        if scores["specificity"] < 6:
            suggestions.append("Replace vague terms like 'good' or 'important' with specific values")
            suggestions.append("Add concrete examples of the agent's beliefs or principles")
        
        if scores["consistency"] < 6:
            suggestions.append("Review for any contradictory statements about the agent's personality")
            suggestions.append("Ensure the agent's values and reasoning style align consistently")
        
        # General suggestions
        description_lower = description.lower()
        if "reasoning" not in description_lower and "logic" not in description_lower:
            suggestions.append("Describe whether this agent uses logical, emotional, or rule-based reasoning")
        
        if len(description.split()) < 30:
            suggestions.append("Consider expanding the description with more details about the agent's personality")
        
        return suggestions


class PromptEnhancer:
    """Enhances user descriptions using AI"""
    
    ENHANCER_SYSTEM_PROMPT = (
        "You are an expert at creating ethical AI agent personalities. Your job is to take a user's "
        "brief description of an ethical agent and expand it into a comprehensive, professional personality "
        "description of exactly 4-5 well-structured sentences."
        "\n\nGuidelines for expansion:"
        "\n- Naturally incorporate the agent's name in the first sentence"
        "\n- Expand the core beliefs and values with specific details"
        "\n- Add a clear ethical reasoning framework (deontological, consequentialist, virtue ethics, or custom)"
        "\n- Describe their decision-making approach and criteria"
        "\n- Explain how they apply principles in ethical debates"
        "\n- Acknowledge nuances or limitations in their perspective"
        "\n- Stay faithful to the original intent - do NOT add arbitrary details"
        "\n- Make it rich, detailed, and professional"
        "\n\nIMPORTANT: Return ONLY the expanded personality description (4-5 sentences). Do NOT include "
        "any JSON instructions, system prompt formatting, or meta-commentary. Just the personality text."
    )
    
    def enhance_description(self, description: str, agent_name: str = "Agent") -> EnhancementRequest:
        """Enhance a user description into a better system prompt"""
        analyzer = PromptAnalyzer()
        
        # Analyze original description
        scores = analyzer.analyze_description(description)
        suggestions = analyzer.generate_suggestions(description, scores)
        
        # Generate enhancement prompt with agent name
        enhancement_prompt = (
            f"Agent Name: {agent_name}\n"
            f"Brief Description: \"{description}\"\n\n"
            f"Expand this into a comprehensive 4-5 sentence personality description that:\n"
            f"1. Starts by naturally incorporating '{agent_name}' in the first sentence\n"
            f"2. Elaborates on their core ethical beliefs and values\n"
            f"3. Describes their reasoning framework and decision-making approach\n"
            f"4. Explains how they apply their principles in ethical debates\n"
            f"5. Acknowledges nuances or limitations in their perspective\n\n"
            f"Stay faithful to the original description. Do not add arbitrary details.\n"
            f"Return ONLY the expanded personality text (4-5 sentences), nothing else."
        )
        
        try:
            # Use existing Ollama integration to enhance
            enhanced_prompt = call_ollama(
                self.ENHANCER_SYSTEM_PROMPT,
                enhancement_prompt,
                num_predict=500,
                temp=0.7
            )
            
            # Clean up the response - remove any JSON instructions or extra formatting
            enhanced_prompt = enhanced_prompt.strip()
            enhanced_prompt = enhanced_prompt.replace("Respond in compact JSON only.", "").strip()
            enhanced_prompt = enhanced_prompt.replace("```", "").strip()
            
            # Check quality - if too short or doesn't mention agent name, retry with more explicit instructions
            if len(enhanced_prompt.split()) < 50 or agent_name.lower() not in enhanced_prompt.lower():
                print(f"Enhancement quality check failed, retrying... (length: {len(enhanced_prompt.split())}, has name: {agent_name.lower() in enhanced_prompt.lower()})")
                
                retry_prompt = (
                    f"AGENT NAME: {agent_name}\n"
                    f"USER'S DESCRIPTION: {description}\n\n"
                    f"TASK: Write exactly 4-5 detailed sentences that describe this agent's personality.\n\n"
                    f"REQUIREMENTS:\n"
                    f"- First sentence MUST start with '{agent_name}' and describe their core belief\n"
                    f"- Expand on their ethical values and reasoning framework\n"
                    f"- Describe how they make decisions and evaluate dilemmas\n"
                    f"- Explain their debate style and argumentation approach\n"
                    f"- Acknowledge any nuances or limitations\n\n"
                    f"EXAMPLE FORMAT:\n"
                    f"'{agent_name} champions [core belief] as [description]. [Sentence about values]. "
                    f"[Sentence about reasoning]. [Sentence about application]. [Sentence about nuances].'\n\n"
                    f"Write ONLY the personality description, nothing else:"
                )
                
                enhanced_prompt = call_ollama(
                    self.ENHANCER_SYSTEM_PROMPT,
                    retry_prompt,
                    num_predict=500,
                    temp=0.75
                ).strip()
                
                # Clean again
                enhanced_prompt = enhanced_prompt.replace("Respond in compact JSON only.", "").strip()
                enhanced_prompt = enhanced_prompt.replace("```", "").strip()
            
            # Generate improvements list
            improvements = self._identify_improvements(description, enhanced_prompt, agent_name)
            
            return EnhancementRequest(
                original_description=description,
                enhanced_prompt=enhanced_prompt,
                improvements_made=improvements,
                analysis_scores=scores,
                suggestions=suggestions
            )
            
        except Exception as e:
            print(f"Enhancement error: {e}")
            # Fallback enhancement if AI fails
            return self._fallback_enhancement(description, agent_name, scores, suggestions)
    
    def _identify_improvements(self, original: str, enhanced: str, agent_name: str) -> List[str]:
        """Identify what improvements were made"""
        improvements = []
        
        original_lower = original.lower()
        enhanced_lower = enhanced.lower()
        
        # Check for agent name incorporation
        if agent_name.lower() in enhanced_lower and agent_name.lower() not in original_lower:
            improvements.append(f"Naturally incorporated agent name '{agent_name}' into description")
        
        # Check for expansion
        original_words = len(original.split())
        enhanced_words = len(enhanced.split())
        if enhanced_words > original_words * 2:
            improvements.append(f"Expanded from {original_words} to {enhanced_words} words with rich details")
        
        # Check for added elements
        if any(word in enhanced_lower for word in ["reasoning", "framework", "approach", "applies"]):
            improvements.append("Added clear ethical reasoning framework")
        
        if any(word in enhanced_lower for word in ["decision", "evaluate", "criteria", "considers"]):
            improvements.append("Specified decision-making approach and criteria")
        
        if any(word in enhanced_lower for word in ["debate", "argument", "position", "perspective"]):
            improvements.append("Described how agent applies principles in debates")
        
        if any(word in enhanced_lower for word in ["acknowledges", "limitation", "nuance", "however", "while"]):
            improvements.append("Added nuanced perspective and limitations")
        
        if any(word in enhanced_lower for word in ["deontological", "consequentialist", "virtue", "utilitarian", "autonomy", "rights", "outcomes"]):
            improvements.append("Connected to established ethical concepts")
        
        return improvements if improvements else ["Enhanced clarity and depth"]
    
    def _fallback_enhancement(self, description: str, agent_name: str, scores: Dict[str, float], suggestions: List[str]) -> EnhancementRequest:
        """Provide a basic enhancement if AI enhancement fails"""
        # Create a simple enhanced version with agent name
        enhanced = (
            f"{agent_name} is an ethical agent guided by the following principles: {description} "
            f"When evaluating ethical dilemmas, {agent_name} applies these core values consistently "
            f"and provides clear reasoning for positions taken. {agent_name} engages respectfully with "
            f"other perspectives while maintaining a strong ethical stance based on these foundational beliefs."
        )
        
        improvements = [
            f"Incorporated agent name '{agent_name}'",
            "Expanded description with structured approach",
            "Added consistency and reasoning guidelines"
        ]
        
        return EnhancementRequest(
            original_description=description,
            enhanced_prompt=enhanced,
            improvements_made=improvements,
            analysis_scores=scores,
            suggestions=suggestions
        )


class EnhancementService:
    """Main service for handling agent enhancement requests"""
    
    def __init__(self):
        self.analyzer = PromptAnalyzer()
        self.enhancer = PromptEnhancer()
    
    def enhance_agent_description(self, description: str, agent_name: str = "Agent") -> EnhancementRequest:
        """Main method to enhance an agent description"""
        return self.enhancer.enhance_description(description, agent_name)
    
    def analyze_only(self, description: str) -> Dict:
        """Analyze description without enhancement"""
        scores = self.analyzer.analyze_description(description)
        suggestions = self.analyzer.generate_suggestions(description, scores)
        
        return {
            "analysis_scores": scores,
            "suggestions": suggestions,
            "overall_score": sum(scores.values()) / len(scores)
        }
    
    def generate_system_prompt(self, enhanced_prompt: str, agent_name: str) -> str:
        """Convert enhanced prompt into final system prompt format"""
        # Clean the enhanced prompt to remove any name changes
        cleaned_prompt = self._preserve_agent_name(enhanced_prompt, agent_name)
        
        # Format the enhanced prompt as a proper system prompt
        system_prompt = (
            f"You are {agent_name}, an ethical agent. {cleaned_prompt} "
            f"When responding to opponents, ALWAYS start with their name followed by a comma. "
            f"Respond in compact JSON only."
        )
        
        return system_prompt
    
    def _preserve_agent_name(self, enhanced_prompt: str, original_name: str) -> str:
        """Remove any name changes from the enhanced prompt"""
        import re
        
        # Remove JSON-style name fields that might change the agent name
        patterns_to_remove = [
            r'"name"\s*:\s*"[^"]*"',
            r'"agentName"\s*:\s*"[^"]*"',
            r'"agent_name"\s*:\s*"[^"]*"',
            r'"Agent Name"\s*:\s*"[^"]*"'
        ]
        
        cleaned = enhanced_prompt
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, f'"name": "{original_name}"', cleaned, flags=re.IGNORECASE)
        
        return cleaned