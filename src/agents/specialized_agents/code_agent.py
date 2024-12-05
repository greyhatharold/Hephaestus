from src.agents.base_agent import BaseAgent
from src.core.idea import Idea, AgentResponse
from typing import Dict, List
from src.utils.logger import get_logger
from functools import lru_cache
from src.core.domain_types import DomainType

logger = get_logger(__name__)

class CodeAgent(BaseAgent):
    def __init__(self, domain: DomainType):
        super().__init__(domain)
        self.completion_params = {
            'temperature': 0.8,  # Slightly higher for creative solutions
            'max_tokens': 300
        }

    def process_idea(self, idea: Idea) -> AgentResponse:
        try:
            analysis = self._analyze_idea(idea)
            implementation_steps = self._generate_implementation_steps(idea, analysis)
            next_steps_tree = self._generate_next_steps_diagram(idea, implementation_steps)
            
            response = AgentResponse(
                suggestions=analysis["suggestions"],
                questions=analysis["questions"],
                related_concepts=analysis["related_concepts"],
                implementation_steps=implementation_steps,
                next_steps_tree=next_steps_tree
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
            
            return response
        except Exception as e:
            logger.error(f"Error processing design idea: {str(e)}")
            raise

    @lru_cache(maxsize=100)
    def _analyze_idea_cached(self, concept: str, keywords_str: str) -> Dict[str, List[str]]:
        """Cached analysis helper that takes hashable parameters."""
        prompt = self._create_analysis_prompt_internal(concept, keywords_str)
        try:
            response = self.openai_service.create_completion(prompt)
            return self._parse_analysis_response(response)
        except Exception as e:
            logger.error(f"Error in design analysis: {str(e)}")
            raise

    def _analyze_idea(self, idea: Idea) -> Dict[str, List[str]]:
        """Analyze an application design idea."""
        return self._analyze_idea_cached(
            idea.concept,
            ','.join(sorted(idea.keywords))
        )

    def _create_analysis_prompt(self, idea: Idea) -> str:
        """Create prompt for analyzing the idea.
        
        Args:
            idea: The idea to analyze
            
        Returns:
            str: The formatted prompt
        """
        return self._create_analysis_prompt_internal(
            idea.concept,
            ','.join(sorted(idea.keywords))
        )

    def _create_analysis_prompt_internal(self, concept: str, keywords_str: str) -> str:
        """Internal method to create analysis prompt from hashable parameters."""
        return f"""As a senior software architect and UI/UX expert, provide a detailed analysis for: {concept}
        Keywords: {keywords_str}
        
        Write a comprehensive design assessment covering:
        
        1. Architecture Overview:
           - System components and interactions
           - Design patterns and principles
           - Technical stack considerations
           - Scalability and maintainability
           - Include related readings and key concepts.
        
        2. User Interface Design:
           - UI/UX principles and patterns
           - Accessibility considerations
           - Visual hierarchy and flow
           - Interactive elements
        
        3. Implementation Challenges:
           - Technical constraints
           - Performance considerations
           - Security implications
           - Cross-platform compatibility
           - Include cost and time estimates.
        
        4. Best Practices:
           - Coding standards
           - Testing strategies
           - Documentation requirements
           - Deployment considerations
        
        5. Innovation Opportunities:
           - Modern frameworks and tools
           - Emerging technologies
           - Performance optimizations
           - User experience enhancements
        
        Focus on practical, implementable solutions while maintaining high coding standards. Include a section on how to implement the design."""

    def _parse_analysis_response(self, response: str) -> Dict[str, List[str]]:
        """Parse the narrative response into structured sections."""
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        
        return {
            "suggestions": self._extract_key_points(paragraphs[1]),     # UI/UX design
            "questions": self._extract_key_points(paragraphs[2]),       # Implementation challenges
            "related_concepts": self._extract_key_points(paragraphs[3]), # Best practices
            "innovations": self._extract_key_points(paragraphs[4])      # Innovation opportunities
        }

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key design and implementation points from narrative text."""
        points = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 15 and 
                any(design_word in sentence.lower() for design_word in 
                    ['design', 'interface', 'component', 'pattern', 'architecture', 'user', 'code', 'implementation'])):
                points.append(sentence)
        
        return points[:5]

    def _create_implementation_prompt(self, idea: Idea, analysis: Dict[str, List[str]]) -> str:
        return f"""As a technical lead, provide implementation guidance for: {idea.concept}
        
        Context from preliminary analysis:
        {chr(10).join([f"- {s}" for s in analysis.get("suggestions", [])[:3]])}
        
        Detail the implementation approach covering:
        
        1. Setup Phase:
           - Project structure
           - Development environment
           - Dependencies and tools
        
        2. Core Implementation:
           - Component architecture
           - Data flow design
           - State management
        
        3. UI/UX Development:
           - Layout implementation
           - Interactive elements
           - Responsive design
        
        4. Quality Assurance:
           - Testing strategy
           - Performance optimization
           - Code review guidelines
        
        Provide practical, actionable steps while emphasizing clean code and best practices."""

    def _generate_image_prompt(self, idea: Idea) -> str:
        pass

    def _generate_implementation_steps(self, idea: Idea, analysis: Dict[str, List[str]]) -> List[str]:
        """Generate implementation steps based on analysis.
        
        Args:
            idea: The idea to implement
            analysis: Previous analysis results
            
        Returns:
            List[str]: Ordered implementation steps
        """
        prompt = self._create_implementation_prompt(idea, analysis)
        try:
            response = self.openai_service.create_completion(prompt)
            return self._parse_implementation_response(response)
        except Exception as e:
            logger.error(f"Error generating implementation steps: {str(e)}")
            raise

    def _parse_implementation_response(self, response: str) -> List[str]:
        """Parse implementation response into discrete steps.
        
        Args:
            response: Raw response text
            
        Returns:
            List[str]: Parsed implementation steps
        """
        steps = []
        sections = response.split('\n\n')
        
        for section in sections:
            if ':' in section:
                step = section.split(':', 1)[1].strip()
                if step and len(step) > 10:
                    steps.append(step)
        
        return steps[:8]  # Return top 8 most relevant steps