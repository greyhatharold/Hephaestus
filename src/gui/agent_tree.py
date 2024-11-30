from dataclasses import dataclass
from typing import List, Optional
from src.core.domain_types import DomainType

@dataclass
class AgentTreeNode:
    name: str
    domains: Optional[List[DomainType]] = None
    children: Optional[List['AgentTreeNode']] = None
    
class AgentTree:
    def __init__(self):
        self.root = AgentTreeNode("Agents", children=[
            AgentTreeNode("Technology", children=[
                AgentTreeNode("Technical", domains=[
                    DomainType.TECHNOLOGY,
                    DomainType.CODE
                ])
            ]),
            AgentTreeNode("Humanities", children=[
                AgentTreeNode("Arts & Culture", domains=[
                    DomainType.LITERATURE,
                    DomainType.ARTS
                ]),
                AgentTreeNode("Theory", domains=[
                    DomainType.HARD_SCIENCE,
                    DomainType.PHILOSOPHY,
                    DomainType.SOCIAL_SCIENCE
                ])
            ]),
            AgentTreeNode("Practical", children=[
                AgentTreeNode("Business", domains=[
                    DomainType.BUSINESS
                ])
            ])
        ])
    
    def get_all_domains(self) -> List[DomainType]:
        """Get flattened list of all domains"""
        domains = []
        def collect_domains(node: AgentTreeNode):
            if node.domains:
                domains.extend(node.domains)
            if node.children:
                for child in node.children:
                    collect_domains(child)
        collect_domains(self.root)
        return domains 