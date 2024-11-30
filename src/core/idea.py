from dataclasses import dataclass
from typing import Dict, List, Optional
from src.core.domain_types import DomainType

@dataclass
class Idea:
    concept: str
    domain: DomainType
    keywords: List[str]
    development_stage: str
    context: Optional[Dict[str, any]] = None

@dataclass
class AgentResponse:
    suggestions: List[str]
    questions: List[str]
    related_concepts: List[str]
    implementation_steps: List[str]
    next_steps_tree: str
    concept_image: Optional[str] = None