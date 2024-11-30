from typing import Dict, List
from dataclasses import dataclass
from src.core.idea import Idea
from src.core.domain_types import DomainType
from src.agents.agent_factory import AgentFactory

@dataclass
class SubTask:
    description: str
    domain: DomainType
    context: Dict
    parent_task_id: str

class SubtaskDelegator:
    """Handles delegation and orchestration of subtasks between agents"""
    
    def __init__(self):
        self.task_registry: Dict[str, List[SubTask]] = {}
        
    def create_subtasks(self, idea: Idea, primary_domain: DomainType) -> List[SubTask]:
        """Break down complex tasks into domain-specific subtasks"""
        subtasks = []
        
        # Example subtask creation logic - expand based on idea characteristics
        if "technical" in idea.keywords:
            subtasks.append(SubTask(
                description="Technical feasibility analysis",
                domain=DomainType.TECHNOLOGY,
                context={"focus": "feasibility"},
                parent_task_id=idea.id
            ))
            
        if "market" in idea.keywords:
            subtasks.append(SubTask(
                description="Market analysis",
                domain=DomainType.BUSINESS,
                context={"focus": "market"},
                parent_task_id=idea.id
            ))
            
        return subtasks 