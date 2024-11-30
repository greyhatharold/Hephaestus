from src.agents.base_agent import BaseAgent
from src.core.idea import Idea, AgentResponse
from typing import Dict, List
from src.utils.logger import get_logger
from functools import lru_cache
from src.core.domain_types import DomainType
logger = get_logger(__name__)

class ScienceAgent(BaseAgent):
    def __init__(self, domain: DomainType):
        super().__init__(domain)
        self.completion_params = {
            'temperature': 0.7,
            'max_tokens': 300
        }

    def process_idea(self, idea: Idea) -> AgentResponse:
        try:
            analysis = self._analyze_idea(idea)
            implementation_steps = self._generate_implementation_steps(idea, analysis)
            next_steps_tree = self._generate_next_steps_diagram(idea, implementation_steps)
            
            # Generate scientific visualization
            concept_image = self._generate_concept_image(idea, analysis)
            
            response = AgentResponse(
                suggestions=analysis["suggestions"],
                questions=analysis["questions"],
                related_concepts=analysis["related_concepts"],
                implementation_steps=implementation_steps,
                next_steps_tree=next_steps_tree,
                concept_image=concept_image  # Add concept image
            )
            
            # Store the idea and response
            idea_id = self.data_manager.save_idea(idea, response)
            
            # Store both diagram and concept image if generated
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
                    gpt_response="Scientific concept visualization"
                )
                
            return response
        except Exception as e:
            logger.error(f"Error processing scientific idea: {str(e)}")
            raise

    @lru_cache(maxsize=100)
    def _analyze_idea_cached(self, concept: str, keywords_str: str) -> Dict[str, List[str]]:
        """Cached analysis helper that takes hashable parameters."""
        prompt = self._create_analysis_prompt_internal(concept, keywords_str)
        try:
            response = self.openai_service.create_completion(prompt)
            return self._parse_analysis_response(response)
        except Exception as e:
            logger.error(f"Error in scientific analysis: {str(e)}")
            raise

    def _analyze_idea(self, idea: Idea) -> Dict[str, List[str]]:
        """Analyze a scientific idea."""
        return self._analyze_idea_cached(
            idea.concept,
            ','.join(sorted(idea.keywords))  # Sort for consistent caching
        )

    def _create_analysis_prompt_internal(self, concept: str, keywords_str: str) -> str:
        """Internal method to create analysis prompt from hashable parameters."""
        return f"""As a senior research scientist, provide a detailed scientific analysis for: {concept}
        Keywords: {keywords_str}
        
        Write a comprehensive scientific assessment in narrative form, covering:
        
        1. Begin with an executive summary of the research concept:
           - Core scientific principles involved
           - Current state of research
           - Potential scientific impact
        
        2. Deep-dive into the research methodology:
           - Experimental design considerations
           - Required equipment and materials
           - Data collection methods
           - Statistical analysis approaches
           - Potential confounding variables
        
        3. Address critical research challenges:
           - Methodological limitations
           - Control measures
           - Validity and reliability considerations
           - Ethical implications
        
        4. Explore the scientific landscape:
           - Related research papers
           - Current theoretical frameworks
           - Competing hypotheses
           - Relevant scientific debates
        
        5. Conclude with future research directions:
           - Novel experimental approaches
           - Potential breakthrough areas
           - Cross-disciplinary applications
        
        Make the response scientifically rigorous yet accessible to read."""

    def _create_analysis_prompt(self, idea: Idea) -> str:
        """Create analysis prompt for scientific ideas."""
        return self._create_analysis_prompt_internal(
            idea.concept,
            ', '.join(idea.keywords)
        )

    def _generate_implementation_steps(self, idea: Idea, analysis: Dict[str, List[str]]) -> List[str]:
        """Generate implementation steps for scientific ideas."""
        prompt = self._create_implementation_prompt(idea, analysis)
        try:
            response = self.openai_service.create_completion(prompt)
            return [step.strip() for step in response.split('\n') if step.strip()]
        except Exception as e:
            logger.error(f"Error generating scientific steps: {str(e)}")
            raise

    def _parse_analysis_response(self, response: str) -> Dict[str, List[str]]:
        """Parse the narrative response into structured sections."""
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        
        return {
            "suggestions": self._extract_key_points(paragraphs[1]),     # Methodology
            "questions": self._extract_key_points(paragraphs[2]),       # Research challenges
            "related_concepts": self._extract_key_points(paragraphs[3]), # Scientific landscape
            "innovations": self._extract_key_points(paragraphs[4])      # Future directions
        }

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key scientific points from narrative text."""
        points = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            # Look for scientifically meaningful content
            if (len(sentence) > 15 and 
                any(science_word in sentence.lower() for science_word in 
                    ['research', 'experiment', 'method', 'analysis', 'data', 'hypothesis', 'theory'])):
                points.append(sentence)
        
        return points[:5]  # Return up to 5 most relevant scientific points

    def _create_implementation_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        return f"""As a principal investigator, craft a detailed research narrative for: {idea.concept}
        
        Context from preliminary analysis:
        {chr(10).join([f"- {s}" for s in analysis.get("suggestions", [])[:3]])}
        
        Tell the story of this scientific investigation, covering:
        
        1. Research Design Phase:
           - Hypothesis formulation
           - Experimental design
           - Control group considerations
        
        2. Methodology Development:
           - Protocol development
           - Instrumentation setup
           - Calibration procedures
        
        3. Data Collection Strategy:
           - Sampling methods
           - Measurement techniques
           - Quality control measures
        
        4. Analysis Framework:
           - Statistical approaches
           - Data validation methods
           - Result interpretation guidelines
        
        Write this as an engaging scientific narrative that maintains methodological rigor."""

    def _generate_image_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        """Generate a science-focused image prompt."""
        prompt = f"""Create a detailed scientific visualization prompt, designed to be used with a Stable Diffusion model, for: {idea.concept}
        
        Scientific Context:
        {chr(10).join([f"- {s}" for s in analysis.get("suggestions", [])[:2]])}
        
        Focus on visual elements that represent:
        - Core scientific principles and mechanisms
        - Experimental setup and methodology
        - Data visualization and results
        - Scientific processes and interactions
        - Scale and measurement considerations
        
        Style Guidelines:
        - Technical accuracy and precision
        - Clear scientific notation and labeling
        - Appropriate use of scientific diagrams
        - Professional academic presentation
        - Cross-sectional or multi-view representation where relevant
        
        Additional Specifications:
        - Include relevant scientific symbols and notations
        - Show cause-and-effect relationships
        - Represent quantitative aspects where applicable
        - Include scale bars or reference points
        
        Make it scientifically accurate while being visually informative."""
        
        try:
            return self.openai_service.create_completion(prompt)
        except Exception as e:
            logger.error(f"Error generating scientific image prompt: {str(e)}")
            raise

    def _generate_concept_image(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        """Generate a concept image for a scientific idea."""
        prompt = self._generate_image_prompt(idea, analysis)
        try:
            return self.openai_service.create_image(prompt)
        except Exception as e:
            logger.error(f"Error generating scientific concept image: {str(e)}")
            raise 