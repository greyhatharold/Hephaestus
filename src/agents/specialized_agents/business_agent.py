from src.agents.base_agent import BaseAgent
from src.core.idea import Idea, AgentResponse
from typing import Dict, List
from src.utils.logger import get_logger
from functools import lru_cache
from src.core.domain_types import DomainType

logger = get_logger(__name__)

class BusinessAgent(BaseAgent):
    def __init__(self, domain: DomainType):
        super().__init__(domain)
        self.completion_params = {
            'temperature': 0.7,
            'max_tokens': 300
        }

    def process_idea(self, idea: Idea) -> AgentResponse:
        """Process a business idea and generate recommendations."""
        try:
            analysis = self._analyze_idea(idea)
            implementation_steps = self._generate_implementation_steps(idea, analysis)
            next_steps_tree = self._generate_next_steps_diagram(idea, implementation_steps)
            
            # Generate concept visualization
            concept_image = self._generate_concept_image(idea, analysis)
            
            return AgentResponse(
                suggestions=analysis["suggestions"],
                questions=analysis["questions"],
                related_concepts=analysis["related_concepts"],
                implementation_steps=implementation_steps,
                next_steps_tree=next_steps_tree,
                concept_image=concept_image
            )
        except Exception as e:
            logger.error(f"Error processing business idea: {str(e)}")
            raise

    def _generate_image_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        """Generate a business-focused image prompt."""
        prompt = f"""Create a detailed image prompt for a business concept: {idea.concept}
        
        Business Context:
        {chr(10).join([f"- {s}" for s in analysis.get("suggestions", [])[:2]])}
        
        Focus on visual elements that represent:
        - Brand identity and market positioning
        - Core business operations or service delivery
        - Target customer interaction
        - Business infrastructure or physical presence
        - Professional and corporate aesthetic
        
        Style Guidelines:
        - Modern and professional business aesthetic
        - Clean and polished presentation
        - Industry-appropriate visuals
        - Clear value proposition representation
        
        Make it visually compelling while maintaining business professionalism."""
        
        try:
            return self.openai_service.create_completion(prompt)
        except Exception as e:
            logger.error(f"Error generating business image prompt: {str(e)}")
            raise

    @lru_cache(maxsize=100)
    def _analyze_idea_cached(self, concept: str, keywords_str: str) -> Dict[str, List[str]]:
        """Cached analysis helper that takes hashable parameters."""
        prompt = self._create_analysis_prompt_internal(concept, keywords_str)
        try:
            response = self.openai_service.create_completion(prompt)
            return self._parse_analysis_response(response)
        except Exception as e:
            logger.error(f"Error in business analysis: {str(e)}")
            raise

    def _analyze_idea(self, idea: Idea) -> Dict[str, List[str]]:
        """Analyze a business idea."""
        return self._analyze_idea_cached(
            idea.concept,
            ','.join(sorted(idea.keywords))
        )

    def _create_analysis_prompt_internal(self, concept: str, keywords_str: str) -> str:
        """Internal method to create analysis prompt from hashable parameters."""
        return f"""As a seasoned business consultant, provide a detailed narrative analysis for: {concept}
        Keywords: {keywords_str}
        
        Write an engaging business assessment in a conversational style, covering:
        
        1. Begin with an executive summary of the business concept and market opportunity.
        
        2. Discuss 5 key business strategies, including:
           - Target market and positioning
           - Revenue models and pricing strategy
           - Resource requirements and initial investment
           - Competitive advantages
           - Growth potential
        
        3. Address critical market challenges and research questions.
        
        4. Explore similar business models and market competitors.
        
        5. Conclude with innovative approaches and scaling possibilities.
        
        Make the response engaging and flowing, while maintaining business practicality."""

    def _create_analysis_prompt(self, idea: Idea) -> str:
        """Create analysis prompt for business ideas."""
        return self._create_analysis_prompt_internal(
            idea.concept,
            ', '.join(idea.keywords)
        )

    def _generate_implementation_steps(self, idea: Idea, analysis: Dict[str, List[str]]) -> List[str]:
        """Generate implementation steps for business ideas."""
        prompt = self._create_implementation_prompt(idea, analysis)
        try:
            response = self.openai_service.create_completion(prompt)
            return [step.strip() for step in response.split('\n') if step.strip()]
        except Exception as e:
            logger.error(f"Error generating business steps: {str(e)}")
            raise

    def _parse_analysis_response(self, response: str) -> Dict[str, List[str]]:
        """Parse the narrative response into structured sections."""
        # Split the response into paragraphs
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        
        # Extract key points from each section
        return {
            "suggestions": self._extract_key_points(paragraphs[1]),  # Business strategies
            "questions": self._extract_key_points(paragraphs[2]),    # Challenges and questions
            "related_concepts": self._extract_key_points(paragraphs[3])  # Similar businesses
        }

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from a paragraph of text."""
        # Split on common markers like periods or semicolons
        points = []
        for sentence in text.split('.'):
            if len(sentence.strip()) > 10:  # Avoid very short fragments
                points.append(sentence.strip())
        return points[:5]  # Return up to 5 key points

    def _create_implementation_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        return f"""As a business strategist, write a narrative implementation plan for: {idea.concept}
        
        Frame this as a compelling business journey, covering:
        
        1. The path from concept validation to market entry
        2. Key business milestones and market objectives
        3. Required resources and partnerships
        4. Risk management and compliance considerations
        5. Growth and scaling strategy
        
        Write this as a flowing narrative that maintains strategic focus while being engaging to read."""
  