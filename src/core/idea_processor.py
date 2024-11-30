from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

from src.core.idea import Idea, AgentResponse
from src.core.domain_types import DomainType
from src.agents.agent_factory import AgentFactory
from src.agents.base_agent import BaseAgent
from src.services.openai_service import OpenAIService
from src.utils.logger import get_logger
from src.data.data_manager import DataManager
from src.agents.composition.agent_coordinator import AgentCoordinator

logger = get_logger(__name__)

class IdeaProcessor:
    """
    Core system for processing and developing ideas across different domains.
    Separated from main system to avoid circular imports.
    """
    def __init__(self):
        logger.info("Initializing Idea Processor")
        load_dotenv()
        
        self.data_manager = DataManager()
        self.openai_service = OpenAIService()
        self._agents = {}
        self._collaborative_agents = {}  # Cache for collaborative agents

    @property
    def agents(self) -> Dict[DomainType, BaseAgent]:
        """Lazy loading of agents"""
        if not self._agents:
            self._agents = {
                domain: AgentFactory.create_agent(domain) for domain in DomainType
            }
        return self._agents

    def develop_idea(self, raw_concept: str, supporting_domains: List[DomainType] = None) -> Dict:
        """Main entry point for idea development with optional collaborative processing."""
        logger.info("Starting idea development process")
        
        idea = self._create_structured_idea(raw_concept)
        
        if supporting_domains:
            # Use collaborative agent if supporting domains are specified
            agent = self._get_collaborative_agent(idea.domain, supporting_domains)
            response = agent.process_complex_idea(idea)
        else:
            # Use single domain agent
            response = self.agents[idea.domain].process_idea(idea)
        
        # Save to database
        idea_id = self.data_manager.save_idea(idea, response)
        
        return {
            "id": idea_id,
            "idea": {
                "concept": idea.concept,
                "domain": idea.domain.value,
                "keywords": idea.keywords,
                "supporting_domains": [d.value for d in supporting_domains] if supporting_domains else []
            },
            "development": {
                "suggestions": response.suggestions,
                "related_concepts": response.related_concepts,
                "questions": response.questions,
                "implementation_steps": response.implementation_steps,
                "next_steps_tree": response.next_steps_tree,
                "concept_image": getattr(response, 'concept_image', None)
            },
            "timestamp": datetime.now().isoformat()
        }

    def _create_structured_idea(self, raw_concept: str) -> Idea:
        return Idea(
            concept=raw_concept,
            domain=self._classify_domain(raw_concept),
            keywords=self._extract_keywords(raw_concept),
            development_stage="initial"
        )

    def _classify_domain(self, concept: str) -> DomainType:
        prompt = (
            f"Classify the following concept into one of these domains:\n"
            f"{', '.join(d.value for d in DomainType)}\n\n"
            f"Concept: {concept}\n\nReturn only the domain name."
        )
        
        try:
            return DomainType(self.openai_service.create_completion(prompt).strip().lower())
        except Exception as e:
            logger.error(f"Error classifying domain: {str(e)}")
            raise

    def _extract_keywords(self, concept: str) -> List[str]:
        prompt = (
            f"Extract 5 key concepts or keywords from the following idea:\n"
            f"{concept}\n\nReturn them as a comma-separated list."
        )
        
        try:
            return [k.strip() for k in self.openai_service.create_completion(prompt).split(',')]
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            raise 

    def _get_collaborative_agent(self, primary_domain: DomainType, 
                               supporting_domains: List[DomainType]) -> AgentCoordinator:
        """Get or create a collaborative agent for the given domains."""
        cache_key = (primary_domain, tuple(sorted(supporting_domains)))
        if cache_key not in self._collaborative_agents:
            self._collaborative_agents[cache_key] = AgentFactory.create_collaborative_agent(
                primary_domain, supporting_domains
            )
        return self._collaborative_agents[cache_key]