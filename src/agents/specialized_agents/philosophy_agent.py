from src.agents.base_agent import BaseAgent
from src.core.idea import Idea, AgentResponse
from typing import Dict, List
from src.utils.logger import get_logger
from functools import lru_cache
from src.core.domain_types import DomainType
from src.services.image_service import ImageService

logger = get_logger(__name__)

class PhilosophyAgent(BaseAgent):
    def __init__(self, domain: DomainType):
        super().__init__(domain)
        self.completion_params = {
            'temperature': 0.8,  # Slightly higher for more creative philosophical exploration
            'max_tokens': 400    # More tokens for detailed philosophical analysis
        }
        self.image_service = ImageService()

    def process_idea(self, idea: Idea) -> AgentResponse:
        """Process a philosophical idea and generate recommendations."""
        try:
            analysis = self._analyze_idea(idea)
            implementation_steps = self._generate_implementation_steps(idea, analysis)
            next_steps_tree = self._generate_next_steps_diagram(idea, implementation_steps)
            
            image_prompt = self._generate_image_prompt(idea, analysis)
            concept_image = self.image_service.generate_image(image_prompt)
            
            response = AgentResponse(
                suggestions=analysis["suggestions"],
                questions=analysis["questions"],
                related_concepts=analysis["related_concepts"],
                implementation_steps=implementation_steps,
                next_steps_tree=next_steps_tree,
                concept_image=concept_image
            )
            
            idea_id = self.data_manager.save_idea(idea, response)
            
            if next_steps_tree:
                self.data_manager.save_diagram(
                    idea_id=idea_id,
                    image_data=next_steps_tree,
                    gpt_response=str(response)
                )
            
            if concept_image:
                self.data_manager.save_diagram(
                    idea_id=idea_id,
                    image_data=concept_image,
                    gpt_response="Philosophy concept visualization"
                )
            
            return response
        except Exception as e:
            logger.error(f"Error processing philosophical idea: {str(e)}")
            raise

    @lru_cache(maxsize=100)
    def _analyze_idea_cached(self, concept: str, keywords_str: str) -> Dict[str, List[str]]:
        """Cached analysis helper that takes hashable parameters."""
        prompt = self._create_analysis_prompt_internal(concept, keywords_str)
        try:
            response = self.openai_service.create_completion(prompt)
            return self._parse_analysis_response(response)
        except Exception as e:
            logger.error(f"Error in philosophical analysis: {str(e)}")
            raise

    def _analyze_idea(self, idea: Idea) -> Dict[str, List[str]]:
        """Analyze a philosophical idea."""
        return self._analyze_idea_cached(
            idea.concept,
            ','.join(sorted(idea.keywords))
        )

    def _create_analysis_prompt_internal(self, concept: str, keywords_str: str) -> str:
        """Internal method to create analysis prompt from hashable parameters."""
        return f"""As a philosophical expert, provide a comprehensive analysis for: {concept}
        Keywords: {keywords_str}
        
        Craft a philosophical exploration that covers:
        
        1. Begin with a conceptual framework:
           - Core philosophical principles
           - Key assumptions and premises
           - Historical context and relevance
        
        2. Deep-dive into philosophical implications:
           - Epistemological considerations
           - Ethical dimensions
           - Metaphysical aspects
           - Logical structure and arguments
        
        3. Address critical philosophical challenges:
           - Potential counterarguments
           - Paradoxes and contradictions
           - Practical implications
        
        4. Explore the philosophical landscape:
           - Related philosophical traditions
           - Contemporary perspectives
           - Interdisciplinary connections
        
        5. Conclude with transformative possibilities:
           - Novel philosophical approaches
           - Potential paradigm shifts
           - Future philosophical directions
        
        Make the response philosophically rigorous yet accessible."""

    def _create_implementation_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        return f"""As a philosophical practitioner, outline a structured approach for developing: {idea.concept}
        
        Context from analysis:
        {chr(10).join([f"- {s}" for s in analysis.get("suggestions", [])[:3]])}
        
        Detail the philosophical development process:
        
        1. Conceptual Foundation:
           - Core principles definition
           - Framework development
           - Initial premises establishment
        
        2. Philosophical Investigation:
           - Argument construction
           - Evidence and reasoning
           - Critical analysis methods
        
        3. Implementation Strategy:
           - Practical applications
           - Educational approach
           - Engagement methods
        
        4. Impact Considerations:
           - Societal implications
           - Ethical ramifications
           - Cultural integration
        
        Present this as a coherent essay."""

    def _create_analysis_prompt(self, idea: Idea) -> str:
        """Create analysis prompt for philosophical ideas."""
        return self._create_analysis_prompt_internal(
            idea.concept,
            ', '.join(idea.keywords)
        )

    def _generate_implementation_steps(self, idea: Idea, analysis: Dict[str, List[str]]) -> List[str]:
        """Generate implementation steps for philosophical ideas."""
        prompt = self._create_implementation_prompt(idea, analysis)
        try:
            response = self.openai_service.create_completion(prompt)
            return [step.strip() for step in response.split('\n') if step.strip()]
        except Exception as e:
            logger.error(f"Error generating philosophical steps: {str(e)}")
            raise

    def _parse_analysis_response(self, response: str) -> Dict[str, List[str]]:
        """Parse the philosophical response into structured sections."""
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        
        return {
            "suggestions": self._extract_key_points(paragraphs[1]),      # Philosophical implications
            "questions": self._extract_key_points(paragraphs[2]),        # Critical challenges
            "related_concepts": self._extract_key_points(paragraphs[3]), # Philosophical landscape
            "innovations": self._extract_key_points(paragraphs[4])       # Transformative possibilities
        }

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key philosophical points from narrative text."""
        points = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 15 and 
                any(phil_word in sentence.lower() for phil_word in 
                    ['philosoph', 'concept', 'argument', 'theory', 'ethics', 'logic'])):
                points.append(sentence)
        
        return points[:5]

    def _generate_image_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        """Generate a detailed prompt for philosophical concept visualization."""
        prompt = f"""Create an abstract visual representation prompt for: {idea.concept}
        
        Context:
        {chr(10).join([f"- {s}" for s in analysis.get("suggestions", [])[:2]])}
        
        Focus on visual elements that represent:
        - Abstract philosophical concepts
        - Logical relationships
        - Ethical dimensions
        - Metaphysical aspects
        
        Make it visually symbolic while maintaining philosophical depth."""
        
        try:
            return self.openai_service.create_completion(prompt)
        except Exception as e:
            logger.error(f"Error generating image prompt: {str(e)}")
            raise 