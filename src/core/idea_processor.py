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

    @property
    def agents(self) -> Dict[DomainType, BaseAgent]:
        """Lazy loading of agents"""
        if not self._agents:
            self._agents = {
                domain: AgentFactory.create_agent(domain) for domain in DomainType
            }
        return self._agents

    def develop_idea(self, raw_concept: str) -> Dict:
        """Main entry point for idea development."""
        logger.info("Starting idea development process")
        
        idea = self._create_structured_idea(raw_concept)
        response = self.agents[idea.domain].process_idea(idea)
        
        # Save to database
        idea_id = self.data_manager.save_idea(idea, response)
        
        return {
            "id": idea_id,
            "idea": {
                "concept": idea.concept,
                "domain": idea.domain.value,
                "keywords": idea.keywords
            },
            "development": {
                "suggestions": response.suggestions,
                "related_concepts": response.related_concepts,
                "questions": response.questions,
                "implementation_steps": response.implementation_steps,
                "next_steps_tree": response.next_steps_tree
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