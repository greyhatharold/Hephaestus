from typing import Dict, List, Optional
from dataclasses import asdict

from ..core.idea import Idea, AgentResponse
from ..core.domain_types import DomainType
from ..services.openai_service import OpenAIService
from ..services.diagram_service import DiagramService
from ..utils.logger import get_logger

logger = get_logger(__name__)

class DomainAgent:
    """
    Agent responsible for processing ideas within a specific domain.
    Handles domain-specific analysis, suggestions, and development steps.
    """
    
    def __init__(self, domain: DomainType):
        self.domain = domain
        self.openai_service = OpenAIService()
        self.diagram_service = DiagramService()
        
    def process_idea(self, idea: Idea) -> AgentResponse:
        """
        Process an idea through domain-specific analysis and generate recommendations.
        
        Args:
            idea: Structured Idea object containing the concept and metadata
            
        Returns:
            AgentResponse containing analysis results and recommendations
        """
        logger.info(f"Processing idea in {self.domain.value} domain")
        
        try:
            # Generate domain-specific analysis
            analysis = self._analyze_idea(idea)
            
            # Generate implementation steps
            implementation_steps = self._generate_implementation_steps(idea, analysis)
            
            # Generate next steps diagram
            next_steps_tree = self._generate_next_steps_diagram(idea, implementation_steps)
            
            # Create agent response
            response = AgentResponse(
                suggestions=analysis["suggestions"],
                questions=analysis["questions"],
                related_concepts=analysis["related_concepts"],
                implementation_steps=implementation_steps,
                next_steps_tree=next_steps_tree
            )
            
            logger.debug(f"Successfully processed idea: {idea.concept[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error processing idea in {self.domain.value} domain: {str(e)}")
            raise

    def _analyze_idea(self, idea: Idea) -> Dict[str, List[str]]:
        """Performs domain-specific analysis of the idea."""
        prompt = self._create_analysis_prompt(idea)
        
        try:
            response = self.openai_service.create_completion(prompt)
            analysis = self._parse_analysis_response(response)
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing idea: {str(e)}")
            raise

    def _generate_implementation_steps(self, idea: Idea, analysis: Dict[str, List[str]]) -> List[str]:
        """Generates concrete implementation steps based on the idea and analysis."""
        prompt = self._create_implementation_prompt(idea, analysis)
        
        try:
            response = self.openai_service.create_completion(prompt)
            steps = [step.strip() for step in response.split('\n') if step.strip()]
            return steps
        except Exception as e:
            logger.error(f"Error generating implementation steps: {str(e)}")
            raise

    def _generate_next_steps_diagram(self, idea: Idea, steps: List[str]) -> Optional[str]:
        """Generates a visual diagram of next steps."""
        prompt = self._create_diagram_prompt(idea, steps)
        
        try:
            response = self.openai_service.create_completion(prompt)
            diagram_data, _ = self.diagram_service.generate_diagram(idea.concept, response)
            return diagram_data
        except Exception as e:
            logger.error(f"Error generating diagram: {str(e)}")
            return None

    def _create_analysis_prompt(self, idea: Idea) -> str:
        """Creates a domain-specific prompt for idea analysis."""
        return f"""
        As an expert in {self.domain.value}, analyze this idea:
        
        Concept: {idea.concept}
        Keywords: {', '.join(idea.keywords)}
        
        Provide:
        1. 5 specific suggestions for improvement
        2. 5 critical questions to consider
        3. 5 related concepts or ideas to explore
        
        Format your response as:
        SUGGESTIONS:
        - suggestion 1
        - suggestion 2
        ...
        
        QUESTIONS:
        - question 1
        - question 2
        ...
        
        RELATED_CONCEPTS:
        - concept 1
        - concept 2
        ...
        """

    def _create_implementation_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        """Creates a prompt for generating implementation steps."""
        return f"""
        Based on this {self.domain.value} idea and its analysis:
        
        Concept: {idea.concept}
        
        Key Suggestions:
        {chr(10).join([f"- {s}" for s in analysis["suggestions"]])}
        
        Generate 7-10 concrete implementation steps.
        Each step should be clear, actionable, and specific to the domain.
        List them in chronological order.
        """

    def _create_diagram_prompt(self, idea: Idea, steps: List[str]) -> str:
        """Creates a prompt for generating the next steps diagram."""
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

    def _parse_analysis_response(self, response: str) -> Dict[str, List[str]]:
        sections = {
            "suggestions": [],
            "questions": [],
            "related_concepts": []
        }
        
        current_section = None
        for line in response.splitlines():
            line = line.strip()
            if not line:
                continue
                
            if ':' in line:
                section = line.split(':')[0].lower()
                if section in sections:
                    current_section = section
            elif line.startswith('- ') and current_section:
                sections[current_section].append(line[2:])
                
        return sections 