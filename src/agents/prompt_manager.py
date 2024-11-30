from src.core.domain_types import DomainType

class PromptManager:
    @staticmethod
    def get_domain_prompt(domain: DomainType) -> str:
        """
        Get domain-specific prompt template.
        
        Args:
            domain: The domain type for which to get the prompt
            
        Returns:
            str: Domain-specific prompt template
        """
        prompts = {
            DomainType.TECHNOLOGY: """Technology expert and innovation consultant. 
                Focus on:
                - Technical feasibility and implementation
                - System architecture and integration
                - Scalability and performance
                - User experience and interface design
                - Technology stack selection""",
                
            DomainType.BUSINESS: """Business strategist and entrepreneurship consultant.
                Focus on:
                - Market analysis and positioning
                - Business model viability
                - Revenue streams and pricing
                - Growth strategy and scaling
                - Competitive advantage""",
                
            DomainType.HARD_SCIENCE: """Scientific researcher and methodology expert.
                Focus on:
                - Experimental design and methodology
                - Data collection and analysis
                - Empirical evidence and validation
                - Research implications and applications
                - Scientific rigor and reproducibility""",
                
            DomainType.CODE: """Software architect and development expert.
                Focus on:
                - Code architecture and design patterns
                - Implementation best practices
                - Testing and quality assurance
                - Performance optimization
                - Security considerations""",
                
            DomainType.LITERATURE: """Literary expert and creative writing consultant.
                Focus on:
                - Narrative structure and storytelling
                - Character development and arcs
                - Theme exploration and symbolism
                - Writing style and voice
                - Genre conventions and innovations""",
                
            DomainType.SOCIAL_SCIENCE: """Social science researcher and behavioral analyst.
                Focus on:
                - Human behavior and interaction
                - Societal impact and implications
                - Research methodology
                - Data collection and analysis
                - Ethical considerations""",
                
            DomainType.ARTS: """Arts and creative expression consultant.
                Focus on:
                - Artistic technique and execution
                - Creative vision and aesthetics
                - Medium-specific considerations
                - Cultural context and impact
                - Audience engagement""",
                
            DomainType.PHILOSOPHY: """Philosophy and critical thinking expert.
                Focus on:
                - Conceptual analysis and logic
                - Ethical implications
                - Theoretical frameworks
                - Arguments and counterarguments
                - Historical and contemporary context""",
                
            DomainType.WRITING: """Professional writing and content creation expert.
                Focus on:
                - Writing style and tone optimization
                - Content structure and organization
                - Audience engagement and readability
                - SEO and digital optimization
                - Editorial quality and consistency"""
        }
        
        # Default prompt for unregistered domains
        default_prompt = """Domain expert focused on practical implementation.
            Focus on:
            - Core principles and best practices
            - Implementation strategy
            - Quality assurance
            - Resource optimization
            - Impact assessment"""
        
        return prompts.get(domain, default_prompt).strip()

    @staticmethod
    def get_analysis_template(domain: DomainType) -> str:
        """
        Get analysis template for a specific domain.
        
        Args:
            domain: The domain type for which to get the analysis template
            
        Returns:
            str: Analysis template for the specified domain
        """
        templates = {
            DomainType.TECHNOLOGY: """Analysis template for Technology domain.
                Focus on:
                - Technical feasibility and implementation
                - System architecture and integration
                - Scalability and performance
                - User experience and interface design
                - Technology stack selection""",
                
            DomainType.BUSINESS: """Analysis template for Business domain.
                Focus on:
                - Market analysis and positioning
                - Business model viability
                - Revenue streams and pricing
                - Growth strategy and scaling
                - Competitive advantage""",
                
            DomainType.HARD_SCIENCE: """Analysis template for Hard Science domain.
                Focus on:
                - Experimental design and methodology
                - Data collection and analysis
                - Empirical evidence and validation
                - Research implications and applications
                - Scientific rigor and reproducibility""",
                
            DomainType.CODE: """Analysis template for Code domain.
                Focus on:
                - Code architecture and design patterns
                - Implementation best practices
                - Testing and quality assurance
                - Performance optimization
                - Security considerations""",
                
            DomainType.LITERATURE: """Analysis template for Literature domain.
                Focus on:
                - Narrative structure and storytelling
                - Character development and arcs
                - Theme exploration and symbolism
                - Writing style and voice
                - Genre conventions and innovations""",
                
            DomainType.SOCIAL_SCIENCE: """Analysis template for Social Science domain.
                Focus on:
                - Human behavior and interaction
                - Societal impact and implications
                - Research methodology
                - Data collection and analysis
                - Ethical considerations""",
                
            DomainType.ARTS: """Analysis template for Arts domain.
                Focus on:
                - Artistic technique and execution
                - Creative vision and aesthetics
                - Medium-specific considerations
                - Cultural context and impact
                - Audience engagement""",
                
            DomainType.PHILOSOPHY: """Analysis template for Philosophy domain.
                Focus on:
                - Conceptual analysis and logic
                - Ethical implications
                - Theoretical frameworks
                - Arguments and counterarguments
                - Historical and contemporary context""",
                
            DomainType.WRITING: """Analysis template for Writing domain.
                Focus on:
                - Content strategy and planning
                - Writing style and voice development
                - Audience targeting and engagement
                - SEO and digital optimization
                - Editorial standards and quality"""
        }
        
        return templates.get(domain, "Default analysis template for practical implementation.")