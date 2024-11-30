from typing import List, Dict
from src.core.idea import Idea, AgentResponse
from src.agents.agent_factory import AgentFactory
from src.core.domain_types import DomainType
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AgentCoordinator:
    """Coordinates multiple agents for complex tasks requiring cross-domain expertise"""
    
    def __init__(self, primary_domain: DomainType, supporting_domains: List[DomainType]):
        self.primary_agent = AgentFactory.create_agent(primary_domain)
        self.supporting_agents = [AgentFactory.create_agent(domain) for domain in supporting_domains]
        
    def process_complex_idea(self, idea: Idea) -> AgentResponse:
        # Get responses from all agents
        primary_response = self.primary_agent.process_idea(idea)
        supporting_responses = [agent.process_idea(idea) for agent in self.supporting_agents]
        
        # Combine responses using consensus mechanism
        return self._merge_responses(primary_response, supporting_responses)
        
    def _merge_responses(self, primary: AgentResponse, supporting: List[AgentResponse]) -> AgentResponse:
        # Implement consensus/voting logic here
        all_suggestions = self._get_consensus_suggestions([primary] + supporting)
        all_questions = self._get_consensus_questions([primary] + supporting)
        
        return AgentResponse(
            suggestions=all_suggestions,
            questions=all_questions,
            related_concepts=primary.related_concepts,  # Keep primary agent's concepts
            implementation_steps=self._merge_implementation_steps(primary, supporting),
            next_steps_tree=primary.next_steps_tree,
            concept_image=primary.concept_image
        ) 