from typing import Dict, Type, List, TYPE_CHECKING
from src.agents.base_agent import BaseAgent
from src.agents.domain_agent import DomainAgent
from src.agents.specialized_agents.technology_agent import TechnologyAgent
from src.agents.specialized_agents.business_agent import BusinessAgent
from src.agents.specialized_agents.science_agent import ScienceAgent
from src.agents.specialized_agents.code_agent import CodeAgent
from src.core.domain_types import DomainType
from src.utils.logger import get_logger
from functools import lru_cache
from src.data.data_manager import DataManager

if TYPE_CHECKING:
    from src.agents.composition.agent_coordinator import AgentCoordinator

logger = get_logger(__name__)

class AgentFactory:
    """
    Factory class responsible for creating appropriate agents based on domain type.
    Allows for easy extension with new specialized agents.
    """
    
    _agent_registry: Dict[DomainType, Type[BaseAgent]] = {
        DomainType.TECHNOLOGY: TechnologyAgent,
        DomainType.BUSINESS: BusinessAgent,
        DomainType.HARD_SCIENCE: ScienceAgent,
        DomainType.CODE: CodeAgent,
    }
    
    @classmethod
    def register_agent(cls, domain: DomainType, agent_class: Type[BaseAgent]) -> None:
        """
        Register a new agent class for a specific domain.
        
        Args:
            domain: The domain type for which to register the agent
            agent_class: The agent class to register
        """
        cls._agent_registry[domain] = agent_class
        logger.info(f"Registered new agent for domain: {domain.value}")
    
    @classmethod
    @lru_cache(maxsize=10)
    def create_agent(cls, domain: DomainType) -> BaseAgent:
        """
        Create and return an appropriate agent for the given domain.
        
        Args:
            domain: The domain type for which to create an agent
            
        Returns:
            An instance of the appropriate agent class
            
        Raises:
            ValueError: If domain is None
        """
        if domain is None:
            raise ValueError("Domain cannot be None")
            
        agent_class = cls._agent_registry.get(domain, DomainAgent)
        logger.debug(f"Creating agent for domain: {domain.value}")
        return agent_class(domain)
    
    @classmethod
    def get_available_domains(cls) -> list[DomainType]:
        """Get list of all available domain types"""
        return list(cls._agent_registry.keys()) 
    
    @classmethod
    def create_collaborative_agent(cls, 
                                 primary_domain: DomainType,
                                 supporting_domains: List[DomainType]) -> "AgentCoordinator":
        """
        Create a collaborative agent that coordinates multiple domain experts.
        
        Args:
            primary_domain: The main domain for the collaborative agent
            supporting_domains: List of supporting domains
            
        Returns:
            An AgentCoordinator instance configured with the specified domains
        """
        # Import here to avoid circular dependency
        from src.agents.composition.agent_coordinator import AgentCoordinator
        return AgentCoordinator(primary_domain, supporting_domains)