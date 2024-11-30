from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from ..core.idea import Idea, AgentResponse
from ..core.domain_types import DomainType
from ..services.openai_service import OpenAIService
from ..services.diagram_service import DiagramService
from ..services.image_service import ImageService
from ..data.data_manager import DataManager
from ..data.chat_history import ChatMessage

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    Defines the common interface and shared functionality.
    """
    
    def __init__(self, domain: DomainType):
        self.domain = domain
        self.openai_service = OpenAIService()
        self.diagram_service = DiagramService()
        self.image_service = ImageService()
        self.data_manager = DataManager()
        self.completion_params: Dict[str, Any] = {
            'temperature': 0.7,
            'max_tokens': 300,
            'presence_penalty': 0.0,
            'frequency_penalty': 0.0
        }
    
    def _create_completion(self, prompt: str) -> str:
        """
        Wrapper method for creating completions with proper parameters.
        
        Args:
            prompt: The prompt to send to the OpenAI service
            
        Returns:
            str: The completion response
            
        Raises:
            Exception: If the completion fails
        """
        try:
            return self.openai_service.create_completion(prompt)
        except Exception as e:
            self.logger.error(f"Error in completion: {str(e)}")
            raise
    
    @abstractmethod
    def process_idea(self, idea: Idea) -> AgentResponse:
        """Process an idea and generate recommendations."""
        pass
    
    @abstractmethod
    def _analyze_idea(self, idea: Idea) -> Dict[str, List[str]]:
        """Perform domain-specific analysis."""
        pass
    
    @abstractmethod
    def _generate_implementation_steps(self, idea: Idea, analysis: Dict[str, List[str]]) -> List[str]:
        """Generate implementation steps."""
        pass
    
    @abstractmethod
    def _create_analysis_prompt(self, idea: Idea) -> str:
        """Create analysis prompt."""
        pass
    
    @abstractmethod
    def _create_implementation_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        """Create implementation prompt."""
        pass
    
    @abstractmethod
    def _parse_analysis_response(self, response: str) -> Dict[str, List[str]]:
        """Parse the analysis response into structured format."""
        pass
    
    def _generate_next_steps_diagram(self, idea: Idea, steps: List[str]) -> Optional[str]:
        """Generate visual diagram of next steps. Can be overridden by specific agents."""
        prompt = self._create_diagram_prompt(idea, steps)
        try:
            response = self.openai_service.create_completion(prompt)
            diagram_data, _ = self.diagram_service.generate_diagram(idea.concept, response)
            return diagram_data
        except Exception as e:
            return None
    
    def _create_diagram_prompt(self, idea: Idea, steps: List[str]) -> str:
        """Create diagram prompt. Can be overridden by specific agents."""
        return f"""
        Create a diagram showing the relationship between these implementation steps:
        
        {chr(10).join([f"- {s}" for s in steps])}
        
        Return the relationships in the format:
        Step1 -> Step2
        Step2 -> Step3
        Step2 -> Step4
        etc.
        
        Only include the most important connections.
        """ 
    
    def chat_response(self, message: str) -> str:
        """Process a chat message and return a response."""
        prompt = f"""As a specialized {self.domain.value} agent, respond to this message:
        
        Message: {message}
        
        Provide a helpful response focusing on {self.domain.value}-specific insights and recommendations."""
        
        try:
            response = self.openai_service.create_completion(prompt)
            self.data_manager.add_chat_message(
                ChatMessage(
                    sender=f"{self.domain.value}_agent",
                    content=message,
                    timestamp=datetime.now(),
                    domain=self.domain.value
                ),
                session_id=str(uuid.uuid4())
            )
            return response
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    @abstractmethod
    def _generate_image_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        """Generate a prompt for image generation based on the idea and analysis."""
        pass
    
    def _generate_concept_image(self, idea: Idea, analysis: Dict[str, List[str]]) -> Optional[str]:
        """Generate an image visualization of the concept."""
        try:
            image_prompt = self._generate_image_prompt(idea, analysis)
            return self.image_service.generate_image(image_prompt)
        except Exception as e:
            self.logger.error(f"Error generating concept image: {str(e)}")
            return None