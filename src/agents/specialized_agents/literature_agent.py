from src.agents.base_agent import BaseAgent
from src.core.idea import Idea, AgentResponse
from typing import Dict, List
from src.utils.logger import get_logger
from functools import lru_cache
from src.core.domain_types import DomainType

logger = get_logger(__name__)

class LiteratureAgent(BaseAgent):
    def __init__(self, domain: DomainType):
        super().__init__(domain)
        self.completion_params = {
            'temperature': 0.8,  # Higher temperature for more creative responses
            'max_tokens': 300
        }

    def process_idea(self, idea: Idea) -> AgentResponse:
        """Process a literary idea and generate recommendations."""
        try:
            analysis = self._analyze_idea(idea)
            implementation_steps = self._generate_implementation_steps(idea, analysis)
            next_steps_tree = self._generate_next_steps_diagram(idea, implementation_steps)
            concept_image = self._generate_concept_image(idea, analysis)
            
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
            
            if next_steps_tree:
                self.data_manager.save_diagram(
                    idea_id=idea_id,
                    image_data=next_steps_tree,
                    gpt_response=str(response)
                )
            
            return response
        except Exception as e:
            logger.error(f"Error processing literary idea: {str(e)}")
            raise

    def _create_analysis_prompt_internal(self, concept: str, keywords_str: str) -> str:
        """Internal method to create analysis prompt from hashable parameters."""
        return f"""As a literary expert and creative writing consultant, provide a detailed analysis for: {concept}
        Keywords: {keywords_str}
        
        Write an engaging literary assessment covering:
        
        1. Narrative Elements:
           - Plot structure and development
           - Character arcs and relationships
           - Setting and world-building
           - Theme exploration
           - Voice and style considerations
        
        2. Literary Techniques:
           - Genre conventions and innovations
           - Literary devices and symbolism
           - Narrative perspective
           - Pacing and tension
        
        3. Writing Challenges:
           - Character development
           - Plot coherence
           - Thematic depth
           - Style consistency
        
        4. Literary Context:
           - Similar works and influences
           - Genre expectations
           - Target audience considerations
        
        5. Creative Opportunities:
           - Unique narrative approaches
           - Stylistic innovations
           - Thematic expansions
        
        Make the response both analytically insightful and creatively inspiring."""

    def _generate_image_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        """Generate a literature-focused image prompt."""
        prompt = f"""Create a detailed artistic prompt, designed to be used with a Stable Diffusion model, for: {idea.concept}
        
        Literary Context:
        {chr(10).join([f"- {s}" for s in analysis.get("suggestions", [])[:2]])}
        
        Focus on visual elements that represent:
        - Key scenes or moments
        - Character appearances and interactions
        - Setting and atmosphere
        - Symbolic elements
        - Emotional resonance
        
        Style Guidelines:
        - Evocative and atmospheric
        - Rich in symbolic detail
        - Genre-appropriate aesthetic
        - Narrative-enhancing visuals
        
        Make it visually compelling while maintaining literary significance."""
        
        try:
            return self.openai_service.create_completion(prompt)
        except Exception as e:
            logger.error(f"Error generating literary image prompt: {str(e)}")
            raise

    @lru_cache(maxsize=100)
    def _analyze_idea_cached(self, concept: str, keywords_str: str) -> Dict[str, List[str]]:
        """Cached analysis helper that takes hashable parameters."""
        prompt = self._create_analysis_prompt_internal(concept, keywords_str)
        try:
            response = self.openai_service.create_completion(prompt)
            return self._parse_analysis_response(response)
        except Exception as e:
            logger.error(f"Error in literary analysis: {str(e)}")
            raise

    def _analyze_idea(self, idea: Idea) -> Dict[str, List[str]]:
        """Analyze a literary idea."""
        return self._analyze_idea_cached(
            idea.concept,
            ','.join(sorted(idea.keywords))
        )

    def _create_analysis_prompt(self, idea: Idea) -> str:
        """Create analysis prompt for literary ideas."""
        return self._create_analysis_prompt_internal(
            idea.concept,
            ', '.join(idea.keywords)
        )

    def _parse_analysis_response(self, response: str) -> Dict[str, List[str]]:
        """Parse the narrative response into structured sections."""
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        
        return {
            "suggestions": self._extract_key_points(paragraphs[1]),     # Literary techniques
            "questions": self._extract_key_points(paragraphs[2]),       # Writing challenges
            "related_concepts": self._extract_key_points(paragraphs[3]) # Literary context
        }

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key literary points from narrative text."""
        points = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 15 and 
                any(lit_word in sentence.lower() for lit_word in 
                    ['character', 'plot', 'theme', 'narrative', 'story', 'writing', 'genre'])):
                points.append(sentence)
        
        return points[:5]

    def _create_implementation_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        return f"""As a literary consultant, craft a detailed writing plan for: {idea.concept}
        
        Context from analysis:
        {chr(10).join([f"- {s}" for s in analysis.get("suggestions", [])[:3]])}
        
        Detail the writing journey, covering:
        
        1. Development Phase:
           - Character development
           - Plot outlining
           - World-building
           - Research needs
        
        2. Writing Process:
           - Scene structuring
           - Narrative flow
           - Voice development
           - Description crafting
        
        3. Revision Strategy:
           - Character arc refinement
           - Plot coherence
           - Thematic strengthening
           - Style consistency
        
        4. Final Polish:
           - Language refinement
           - Pacing adjustment
           - Theme enhancement
           - Reader engagement
        
        Write this as an engaging creative guide that maintains literary excellence."""

    def _generate_implementation_steps(self, idea: Idea, analysis: Dict[str, List[str]]) -> List[str]:
        """Generate implementation steps for literary ideas."""
        prompt = self._create_implementation_prompt(idea, analysis)
        try:
            response = self.openai_service.create_completion(prompt)
            return [step.strip() for step in response.split('\n') if step.strip()]
        except Exception as e:
            logger.error(f"Error generating literary steps: {str(e)}")
            raise 