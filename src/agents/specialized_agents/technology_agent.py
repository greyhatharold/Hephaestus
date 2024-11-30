from src.agents.base_agent import BaseAgent
from src.core.idea import Idea, AgentResponse
from typing import Dict, List
from src.utils.logger import get_logger
from functools import lru_cache
from src.core.domain_types import DomainType
from src.services.image_service import ImageService
logger = get_logger(__name__)

class TechnologyAgent(BaseAgent):
    def __init__(self, domain: DomainType):
        super().__init__(domain)
        self.completion_params = {
            'temperature': 0.7,
            'max_tokens': 300
        }
        self.image_service = ImageService()

    def process_idea(self, idea: Idea) -> AgentResponse:
        """Process a technology idea and generate recommendations."""
        try:
            analysis = self._analyze_idea(idea)
            implementation_steps = self._generate_implementation_steps(idea, analysis)
            next_steps_tree = self._generate_next_steps_diagram(idea, implementation_steps)
            
            # Generate concept image
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
            
            # Store the idea and response
            idea_id = self.data_manager.save_idea(idea, response)
            
            # Store diagram if generated
            if next_steps_tree:
                self.data_manager.save_diagram(
                    idea_id=idea_id,
                    image_data=next_steps_tree,
                    gpt_response=str(response)
                )
            
            # Store concept image if generated
            if concept_image:
                self.data_manager.save_diagram(
                    idea_id=idea_id,
                    image_data=concept_image,
                    gpt_response="Technology concept visualization"
                )
            
            return response
        except Exception as e:
            logger.error(f"Error processing technology idea: {str(e)}")
            raise

    @lru_cache(maxsize=100)
    def _analyze_idea_cached(self, concept: str, keywords_str: str) -> Dict[str, List[str]]:
        """Cached analysis helper that takes hashable parameters."""
        prompt = self._create_analysis_prompt_internal(concept, keywords_str)
        try:
            response = self.openai_service.create_completion(prompt)
            return self._parse_analysis_response(response)
        except Exception as e:
            logger.error(f"Error in technology analysis: {str(e)}")
            raise

    def _analyze_idea(self, idea: Idea) -> Dict[str, List[str]]:
        """Analyze a technology idea."""
        return self._analyze_idea_cached(
            idea.concept,
            ','.join(sorted(idea.keywords))
        )

    def _create_analysis_prompt_internal(self, concept: str, keywords_str: str) -> str:
        """Internal method to create analysis prompt from hashable parameters."""
        return f"""As a senior technology architect, provide an engaging narrative analysis for: {concept}
        Keywords: {keywords_str}
        
        Write a compelling technical story that covers:
        
        1. Begin with an executive summary that paints a vision of the technology's potential:
           - Core innovation and unique value proposition
           - Technical feasibility assessment
           - Potential market impact
        
        2. Deep-dive into the technical implementation strategy:
           - Specific technologies and components required
           - System architecture and integration points
           - Performance requirements and constraints
           - Development complexity and technical risks
           - Resource requirements and technical expertise needed
        
        3. Address critical engineering challenges:
           - Technical limitations and potential solutions
           - Safety and reliability considerations
           - Scalability and maintenance aspects
        
        4. Explore the technology landscape:
           - Similar existing technologies
           - Competing solutions and their approaches
           - Relevant patents and research papers
        
        5. Conclude with breakthrough possibilities:
           - Novel technical approaches
           - Future enhancement possibilities
           - Potential technical advantages
        
        Make the response technically precise yet engaging to read."""

    def _create_implementation_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        return f"""As a technical project architect, craft a detailed development narrative for: {idea.concept}
        
        Context from analysis:
        {chr(10).join([f"- {s}" for s in analysis.get("suggestions", [])[:3]])}
        
        Tell the story of bringing this technology to life, covering:
        
        1. Technical Discovery Phase:
           - Proof of concept development
           - Core technology validation
           - Initial prototyping approach
        
        2. Development Journey:
           - Component selection and integration
           - Technical challenges and solutions
           - Testing and validation methods
        
        3. Implementation Roadmap:
           - Development milestones
           - Technical dependencies
           - Quality and safety measures
        
        4. Production Considerations:
           - Scaling strategy
           - Performance optimization
           - Maintenance and support
        
        Write this as an engaging technical narrative that maintains engineering precision."""

    def _create_analysis_prompt(self, idea: Idea) -> str:
        """Create analysis prompt for technology ideas."""
        return self._create_analysis_prompt_internal(
            idea.concept,
            ', '.join(idea.keywords)
        )

    def _generate_implementation_steps(self, idea: Idea, analysis: Dict[str, List[str]]) -> List[str]:
        """Generate implementation steps for technology ideas."""
        prompt = self._create_implementation_prompt(idea, analysis)
        try:
            response = self.openai_service.create_completion(prompt)
            return [step.strip() for step in response.split('\n') if step.strip()]
        except Exception as e:
            logger.error(f"Error generating technology steps: {str(e)}")
            raise

    def _parse_analysis_response(self, response: str) -> Dict[str, List[str]]:
        """Parse the narrative response into structured sections."""
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        
        return {
            "suggestions": self._extract_key_points(paragraphs[1]),     # Technical implementation
            "questions": self._extract_key_points(paragraphs[2]),       # Engineering challenges
            "related_concepts": self._extract_key_points(paragraphs[3]), # Technology landscape
            "innovations": self._extract_key_points(paragraphs[4])      # Breakthrough possibilities
        }

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key technical points from narrative text."""
        points = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            # Look for technically meaningful content
            if (len(sentence) > 15 and 
                any(tech_word in sentence.lower() for tech_word in 
                    ['technolog', 'system', 'develop', 'implement', 'component', 'design'])):
                points.append(sentence)
        
        return points[:5]  # Return up to 5 most relevant technical points

    def _generate_image_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        """Generate a detailed prompt for image generation."""
        prompt = f"""Create a detailed image prompt, designed to be used with a Stable Diffusion model, for: {idea.concept}
        
        Context:
        {chr(10).join([f"- {s}" for s in analysis.get("suggestions", [])[:2]])}
        
        Focus on visual elements that represent:
        - Core functionality and purpose
        - Key technical components
        - Overall system architecture
        - User interaction points
        
        Make it visually compelling while maintaining technical accuracy."""
        
        try:
            return self.openai_service.create_completion(prompt)
        except Exception as e:
            logger.error(f"Error generating image prompt: {str(e)}")
            raise
  