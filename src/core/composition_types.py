from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

class CollaborationType(Enum):
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    HYBRID = "hybrid"

@dataclass
class CollaborationConfig:
    type: CollaborationType
    voting_threshold: float = 0.5
    max_iterations: int = 3
    consensus_required: bool = True 