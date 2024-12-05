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
            default_image_size=(1024, 1024),  # Fixed parameter name
            num_inference_steps=50,    # More detailed generation
            guidance_scale=8.5         # Stronger prompt adherence
        )
        self.skip_questions = True  # Add flag to skip questions

    def process_idea(self, idea: Idea) -> AgentResponse:
        """Process an artistic idea with focus on visual generation."""
        try:
            # Check if idea contains art-related keywords
            if not self._is_art_related(idea):
                logger.info("Idea not strongly art-related, using standard processing")
                return super().process_idea(idea)

            analysis = self._analyze_idea(idea)
            implementation_steps = self._generate_implementation_steps(idea, analysis)
            
            # Generate image and store it directly in diagram field
            diagram = None
            try:
                concept_image = self._generate_concept_image(idea, analysis)
                if concept_image:
                    # Store image and get diagram reference
                    idea_id = self.data_manager.save_idea(idea, None)  # Temporary save to get ID
                    diagram = self.data_manager.save_diagram(
                        idea_id=idea_id,
                        image_data=concept_image,
                        gpt_response="Artistic visualization"
                    )
            except Exception as e:
                logger.error(f"Error generating concept image: {str(e)}")
            
            # Create response with diagram field
            response = AgentResponse(
                suggestions=analysis["suggestions"],
                questions=[],  # Empty questions due to skip_questions
                related_concepts=analysis["related_concepts"],
                implementation_steps=implementation_steps,
                diagram=diagram,  # Use stored diagram reference
                skip_questions=True
            )
            
            # Update the saved idea with complete response
            self.data_manager.save_idea(idea, response)
            
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
    
    def _generate_concept_image(
        self, idea: Idea, analysis: Dict[str, List[str]]
    ) -> Optional[str]:
        """Generate a single artistic interpretation of the concept."""
        try:
            base_prompt = self._generate_image_prompt(idea, analysis)
            # Use a single style for more consistent results
            style = "in a realistic style with dramatic lighting and rich details"
            return self.image_service.generate_image(f"{base_prompt}, {style}")
        except Exception as e:
            logger.error(f"Error generating concept image: {str(e)}")
            return None

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

    def _analyze_idea(self, idea: Idea) -> Dict[str, List[str]]:
        """Perform arts-specific analysis."""
        return self._analyze_idea_cached(
            idea.concept,
            ','.join(sorted(idea.keywords))
        )

    @lru_cache(maxsize=100)
    def _analyze_idea_cached(self, concept: str, keywords_str: str) -> Dict[str, List[str]]:
        """Cached analysis helper for art concepts."""
        prompt = self._create_analysis_prompt_internal(concept, keywords_str)
        try:
            response = self.openai_service.create_completion(prompt)
            return self._parse_analysis_response(response)
        except Exception as e:
            logger.error(f"Error in artistic analysis: {str(e)}")
            raise

    def _create_analysis_prompt(self, idea: Idea) -> str:
        """Create analysis prompt for artistic ideas."""
        return self._create_analysis_prompt_internal(
            idea.concept,
            ', '.join(idea.keywords)
        )

    def _create_implementation_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        """Create implementation prompt for artistic ideas."""
        return f"""As a visual arts expert, outline the creation process for: {idea.concept}
        
        Context from analysis:
        {chr(10).join([f"- {s}" for s in analysis.get("suggestions", [])[:3]])}
        
        Detail the artistic process:
        
        1. Preparation Phase:
           - Reference gathering
           - Style exploration
           - Medium selection
           - Composition planning
        
        2. Creation Process:
           - Initial sketching
           - Color palette development
           - Technical execution
           - Detail refinement
        
        3. Quality Enhancement:
           - Artistic review
           - Technical refinement
           - Style consistency
           - Visual impact assessment
        
        4. Finalization:
           - Final touches
           - Medium-specific finishing
           - Presentation preparation
           - Documentation
        
        Present this as a practical artistic creation guide."""

    def _generate_implementation_steps(self, idea: Idea, analysis: Dict[str, List[str]]) -> List[str]:
        """Generate implementation steps for artistic ideas."""
        prompt = self._create_implementation_prompt(idea, analysis)
        try:
            response = self.openai_service.create_completion(prompt)
            return [step.strip() for step in response.split('\n') if step.strip()]
        except Exception as e:
            logger.error(f"Error generating artistic steps: {str(e)}")
            raise

    def _parse_analysis_response(self, response: str) -> Dict[str, List[str]]:
        """Parse the artistic response into structured sections.
        
        Args:
            response: Raw response string from OpenAI
            
        Returns:
            Dict with categorized artistic points, with empty lists as fallbacks
        """
        try:
            # Split and filter empty lines, ensure at least 5 paragraphs with defaults
            paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
            while len(paragraphs) < 5:
                paragraphs.append("No additional artistic points available.")
            
            return {
                "suggestions": self._extract_key_points(paragraphs[1]),      # Visual Elements
                "questions": self._extract_key_points(paragraphs[2]),        # Technical Considerations
                "related_concepts": self._extract_key_points(paragraphs[3]), # Artistic Context
                "innovations": self._extract_key_points(paragraphs[4])       # Creative Possibilities
            }
        except Exception as e:
            logger.warning(f"Error parsing analysis response: {str(e)}. Using default structure.")
            # Provide safe defaults while maintaining expected response structure
            return {
                "suggestions": ["Focus on visual composition", "Consider color theory"],
                "questions": [],  # Empty as per skip_questions requirement
                "related_concepts": ["Artistic interpretation", "Creative expression"],
                "innovations": ["Unique artistic approach"]
            }

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key artistic points from narrative text."""
        points = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 15 and 
                any(art_word in sentence.lower() for art_word in 
                    ['visual', 'color', 'composition', 'style', 'medium', 'technique', 'artistic'])):
                points.append(sentence)
        
        return points[:5]