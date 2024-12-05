from src.agents.base_agent import BaseAgent
from src.core.idea import Idea, AgentResponse
from typing import Dict, List
from src.utils.logger import get_logger
from functools import lru_cache
from src.core.domain_types import DomainType
from src.services.image_service import ImageService

logger = get_logger(__name__)

class WritingAgent(BaseAgent):
    def __init__(self, domain: DomainType):
        super().__init__(domain)
        self.completion_params = {
            'temperature': 0.75,  # Balance between creativity and consistency
            'max_tokens': 500     # More tokens for detailed writing analysis
        }
        self.image_service = ImageService()

    def process_idea(self, idea: Idea) -> AgentResponse:
        """Process a writing-related idea and generate recommendations."""
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
                    gpt_response="Writing concept visualization"
                )
            
            return response
        except Exception as e:
            logger.error(f"Error processing writing idea: {str(e)}")
            raise

    @lru_cache(maxsize=100)
    def _analyze_idea_cached(self, concept: str, keywords_str: str) -> Dict[str, List[str]]:
        """Cached analysis helper that takes hashable parameters."""
        prompt = self._create_analysis_prompt_internal(concept, keywords_str)
        try:
            response = self.openai_service.create_completion(prompt)
            return self._parse_analysis_response(response)
        except Exception as e:
            logger.error(f"Error in writing analysis: {str(e)}")
            raise

    def _analyze_idea(self, idea: Idea) -> Dict[str, List[str]]:
        """Analyze a writing-related idea."""
        return self._analyze_idea_cached(
            idea.concept,
            ','.join(sorted(idea.keywords))
        )

    def _create_analysis_prompt_internal(self, concept: str, keywords_str: str) -> str:
        """Internal method to create analysis prompt from hashable parameters."""
        return f"""As a professional writing and content strategy expert, analyze: {concept}
        Keywords: {keywords_str}
        
        Provide a comprehensive content analysis covering:
        
        1. Content Strategy Overview:
           - Target audience and reader personas
           - Core message and value proposition
           - Content goals and objectives
           - Platform and format considerations
        
        2. Writing Style Analysis:
           - Tone and voice recommendations
           - Language level and complexity
           - Engagement techniques
           - Structural elements
        
        3. Content Optimization:
           - SEO considerations
           - Readability improvements
           - Engagement metrics
           - Distribution channels
        
        4. Editorial Considerations:
           - Quality standards
           - Style guide alignment
           - Fact-checking requirements
           - Review process
        
        5. Success Metrics:
           - KPI recommendations
           - Performance benchmarks
           - Impact measurement
           - Iteration strategy
        
        Provide actionable insights for content creation and optimization."""

    def _create_implementation_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        return f"""As a content strategy expert, outline the development process for: {idea.concept}
        
        Context from analysis:
        {chr(10).join([f"- {s}" for s in analysis.get("suggestions", [])[:3]])}
        
        Detail the content development process:
        
        1. Planning Phase:
           - Research and discovery
           - Audience analysis
           - Content strategy development
           - Resource allocation
        
        2. Content Development:
           - Writing guidelines
           - Structure and formatting
           - SEO optimization
           - Media integration
        
        3. Quality Assurance:
           - Editorial review process
           - Fact-checking
           - Style consistency
           - Engagement testing
        
        4. Distribution Strategy:
           - Channel selection
           - Timing and scheduling
           - Promotion plan
           - Performance tracking
        
        Present this as a practical content development roadmap."""

    def _create_analysis_prompt(self, idea: Idea) -> str:
        """Create analysis prompt for writing-related ideas."""
        return self._create_analysis_prompt_internal(
            idea.concept,
            ', '.join(idea.keywords)
        )

    def _generate_implementation_steps(self, idea: Idea, analysis: Dict[str, List[str]]) -> List[str]:
        """Generate implementation steps for writing projects."""
        prompt = self._create_implementation_prompt(idea, analysis)
        try:
            response = self.openai_service.create_completion(prompt)
            return [step.strip() for step in response.split('\n') if step.strip()]
        except Exception as e:
            logger.error(f"Error generating writing steps: {str(e)}")
            raise

    def _parse_analysis_response(self, response: str) -> Dict[str, List[str]]:
        """Parse the content strategy response into structured sections."""
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        
        return {
            "suggestions": self._extract_key_points(paragraphs[1]),      # Writing Style Analysis
            "questions": self._extract_key_points(paragraphs[2]),        # Content Optimization
            "related_concepts": self._extract_key_points(paragraphs[3]), # Editorial Considerations
            "innovations": self._extract_key_points(paragraphs[4])       # Success Metrics
        }

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key writing and content strategy points from narrative text."""
        points = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 15 and 
                any(writing_word in sentence.lower() for writing_word in 
                    ['content', 'write', 'style', 'audience', 'edit', 'seo', 'engage'])):
                points.append(sentence)
        
        return points[:5]

    def _generate_image_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        pass