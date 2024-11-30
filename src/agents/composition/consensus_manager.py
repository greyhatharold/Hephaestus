from typing import List, Dict
from collections import Counter
from src.core.idea import AgentResponse
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ConsensusManager:
    """Manages voting and consensus mechanisms between multiple agents"""
    
    @staticmethod
    def get_consensus_suggestions(responses: List[AgentResponse], threshold: float = 0.5) -> List[str]:
        """Get suggestions that have consensus among agents"""
        all_suggestions = []
        for response in responses:
            all_suggestions.extend(response.suggestions)
            
        # Count occurrence of similar suggestions
        suggestion_counts = Counter(all_suggestions)
        
        # Return suggestions that appear in more than threshold % of responses
        min_count = len(responses) * threshold
        return [sug for sug, count in suggestion_counts.items() if count >= min_count]
    
    @staticmethod
    def merge_implementation_steps(responses: List[AgentResponse]) -> List[str]:
        """Merge implementation steps from multiple agents"""
        primary_steps = responses[0].implementation_steps
        supporting_steps = [r.implementation_steps for r in responses[1:]]
        
        # Identify common steps and unique contributions
        common_steps = set.intersection(*map(set, [primary_steps] + supporting_steps))
        unique_steps = set.union(*map(set, supporting_steps)) - common_steps
        
        # Combine and order steps
        final_steps = list(common_steps)
        final_steps.extend(sorted(unique_steps, key=lambda x: len(x)))
        
        return final_steps[:10]  # Limit to top 10 most relevant steps 