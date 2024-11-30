from src.agents.base_agent import BaseAgent
from src.core.idea import Idea, AgentResponse
from typing import Dict, List, Optional
from src.utils.logger import get_logger
from functools import lru_cache
from src.core.domain_types import DomainType
from src.services.image_service import ImageService

logger = get_logger(__name__)

class ArtsAgent(BaseAgent):
    def __init__(self, domain: DomainType):
        super().__init__(domain)
        self.completion_params = {
            'temperature': 0.9,  # Higher temperature for more creative outputs
            'max_tokens': 400
        }
        # Override default image service with enhanced settings
        self.image_service = ImageService(
            image_size=(1024, 1024),  # Higher resolution
            num_inference_steps=50,    # More detailed generation
            guidance_scale=8.5         # Stronger prompt adherence
        )

    def process_idea(self, idea: Idea) -> AgentResponse:
        """Process an artistic idea with focus on visual generation."""
        try:
            # Check if idea contains art-related keywords
            if not self._is_art_related(idea):
                logger.info("Idea not strongly art-related, using standard processing")
                return super().process_idea(idea)

            analysis = self._analyze_idea(idea)
            implementation_steps = self._generate_implementation_steps(idea, analysis)
            
            # Generate multiple concept images for artistic ideas
            concept_images = self._generate_multiple_concept_images(idea, analysis)
            
            response = AgentResponse(
                suggestions=analysis["suggestions"],
                questions=analysis["questions"],
                related_concepts=analysis["related_concepts"],
                implementation_steps=implementation_steps,
                concept_images=concept_images  # Multiple images
            )
            
            idea_id = self.data_manager.save_idea(idea, response)
            
            # Store all generated images
            for idx, image in enumerate(concept_images):
                if image:
                    self.data_manager.save_diagram(
                        idea_id=idea_id,
                        image_data=image,
                        gpt_response=f"Artistic visualization {idx + 1}"
                    )
            
            return response
        except Exception as e:
            logger.error(f"Error processing artistic idea: {str(e)}")
            raise
        
    def _is_art_related(self, idea: Idea) -> bool:
        """Check if the idea is strongly related to visual arts."""
        art_keywords = {
            'draw', 'paint', 'sketch', 'illustrate', 'design', 'compose',
            'visual', 'artistic', 'creative', 'artwork', 'drawing', 'painting',
            'illustration', 'graphic', 'canvas', 'portrait', 'landscape'
        }
        idea_words = set(idea.concept.lower().split() + idea.keywords)
        return bool(idea_words & art_keywords)
    
    def _generate_multiple_concept_images(
        self, idea: Idea, analysis: Dict[str, List[str]]
    ) -> List[Optional[str]]:
        """Generate multiple artistic interpretations of the concept."""
        try:
            base_prompt = self._generate_image_prompt(idea, analysis)
            style_variations = [
                "in a realistic style",
                "in an impressionist style",
                "in a minimalist style",
                "in a surrealist style"
            ]
            
            return [
                self.image_service.generate_image(f"{base_prompt}, {style}")
                for style in style_variations
            ]
        except Exception as e:
            logger.error(f"Error generating multiple concept images: {str(e)}")
            return [None]

    def _create_analysis_prompt_internal(self, concept: str, keywords_str: str) -> str:
        return f"""As an art director and visual design expert, analyze this creative concept: {concept}
        Keywords: {keywords_str}
        
        Provide a visual arts analysis covering:
        
        1. Visual Composition:
           - Core visual elements
           - Color palette suggestions
           - Composition principles
           - Style recommendations
        
        2. Technical Execution:
           - Medium selection
           - Technique requirements
           - Tool recommendations
           - Process considerations
        
        3. Artistic Vision:
           - Mood and atmosphere
           - Visual storytelling elements
           - Symbolic elements
           - Aesthetic direction
        
        4. Implementation Strategy:
           - Production workflow
           - Resource requirements
           - Quality considerations
           - Timeline estimation
        
        Focus on practical artistic execution and visual impact."""

    def _generate_image_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        """Generate a detailed artistic prompt for image generation."""
        artistic_elements = analysis.get("suggestions", [])[:2]
        mood_elements = analysis.get("related_concepts", [])[:2]
        
        prompt = f"""Create a visually striking interpretation of: {idea.concept}
        
        Artistic elements to incorporate:
        {chr(10).join([f"- {s}" for s in artistic_elements])}
        
        Mood and atmosphere:
        {chr(10).join([f"- {s}" for s in mood_elements])}
        
        Style: Professional, high-quality, detailed artistic rendering
        Include: Dynamic composition, meaningful symbolism, rich textures
        Lighting: Dramatic and evocative
        
        Make it visually compelling and gallery-worthy."""
        
        try:
            return self.openai_service.create_completion(prompt)
        except Exception as e:
            logger.error(f"Error generating artistic prompt: {str(e)}")
            raise 