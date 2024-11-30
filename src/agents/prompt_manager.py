from src.core.domain_types import DomainType

class PromptManager:
    @staticmethod
    def get_domain_prompt(domain: DomainType) -> str:
        prompts = {
            DomainType.LITERATURE: "Literary expert. Focus on narrative analysis and writing techniques.",
            DomainType.HARD_SCIENCE: "Scientific researcher. Focus on methodology and empirical evidence.",
            DomainType.SOCIAL_SCIENCE: "Social science researcher. Focus on human behavior and societal impact.",
        }
        return prompts.get(domain, "Domain expert focused on practical implementation.") 