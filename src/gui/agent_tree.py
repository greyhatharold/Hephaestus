from dataclasses import dataclass
from typing import List, Optional, Callable
from src.core.domain_types import DomainType
import customtkinter as ctk
from .theme import UITheme

@dataclass
class AgentNode:
    name: str
    description: str
    icon: str
    domains: Optional[List[DomainType]] = None
    children: Optional[List['AgentNode']] = None

class AgentTree:
    """Static class to manage agent tree data"""
    @staticmethod
    def create_agent_tree() -> List[AgentNode]:
        return [
            AgentNode(
                name="Technology",
                description="Technical and engineering focused agents",
                icon="💻",
                children=[
                    AgentNode(
                        name="Software Development",
                        description="Programming and software architecture expertise",
                        icon="⚙️",
                        domains=[DomainType.TECHNOLOGY, DomainType.CODE]
                    )
                ]
            ),
            AgentNode(
                name="Creative",
                description="Arts and cultural expertise",
                icon="🎨",
                children=[
                    AgentNode(
                        name="Arts & Literature",
                        description="Creative writing and artistic guidance",
                        icon="📚",
                        domains=[DomainType.LITERATURE, DomainType.ARTS]
                    ),
                    AgentNode(
                        name="Theory & Research",
                        description="Academic and theoretical knowledge",
                        icon="🔬",
                        domains=[DomainType.HARD_SCIENCE, DomainType.PHILOSOPHY]
                    )
                ]
            ),
            AgentNode(
                name="Business",
                description="Professional and business expertise",
                icon="💼",
                children=[
                    AgentNode(
                        name="Strategy",
                        description="Business planning and management",
                        icon="📊",
                        domains=[DomainType.BUSINESS]
                    )
                ]
            )
        ]

class AgentTreeView(ctk.CTkFrame):
    def __init__(self, parent, theme: UITheme, on_select: Callable[[DomainType], None]):
        super().__init__(parent, fg_color="transparent")
        self.theme = theme
        self.on_domain_select = on_select
        
        # Reuse the ModernAgentTree implementation
        self.tree_view = ModernAgentTree(self, theme, on_select)
        self.tree_view.pack(fill="both", expand=True)

class ModernAgentTree(ctk.CTkFrame):
    def __init__(self, parent, theme: UITheme, on_domain_select: Callable[[DomainType], None]):
        super().__init__(parent, fg_color="transparent")
        self.theme = theme
        self.on_domain_select = on_domain_select
        
        # Main container with gradient background
        self.container = ctk.CTkFrame(
            self,
            fg_color=theme.bg_secondary,
            corner_radius=15
        )
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self.header = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        self.header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            self.header,
            text="AI Agents",
            font=(theme.font[0], 24, "bold"),
            text_color=theme.text_color
        ).pack(side="left")
        
        # Search bar
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        
        self.search_frame = ctk.CTkFrame(
            self.container,
            fg_color=theme.bg_tertiary,
            corner_radius=20,
            height=40
        )
        self.search_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Search agents...",
            font=theme.font,
            border_width=0,
            fg_color="transparent",
            textvariable=self.search_var
        ).pack(fill="x", padx=15, pady=5)
        
        # Content area with cards
        self.content = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent"
        )
        self.content.pack(fill="both", expand=True, padx=10)
        
        # Initialize tree and create cards
        self.tree = self._create_agent_tree()
        self._create_category_cards(self.tree)
    
    def _create_agent_card(self, node: AgentNode, is_category: bool = False):
        """Create a modern card-style node"""
        card = ctk.CTkFrame(
            self.content,
            fg_color=self.theme.bg_tertiary,
            corner_radius=12
        )
        card.pack(fill="x", padx=10, pady=5)
        
        # Hover effect
        def on_enter(e):
            card.configure(fg_color=self.theme.accent_color)
        def on_leave(e):
            card.configure(fg_color=self.theme.bg_tertiary)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # Card content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=10)
        
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header,
            text=node.icon,
            font=(self.theme.font[0], 20)
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text=node.name,
            font=(self.theme.font[0], 16, "bold"),
            text_color=self.theme.text_color
        ).pack(side="left", padx=10)
        
        if not is_category:
            ctk.CTkLabel(
                content,
                text=node.description,
                font=self.theme.font_small,
                text_color=self.theme.text_secondary,
                wraplength=400
            ).pack(fill="x", pady=(5, 0))
        
        # Domain buttons for leaf nodes
        if node.domains:
            domain_frame = ctk.CTkFrame(content, fg_color="transparent")
            domain_frame.pack(fill="x", pady=(10, 0))
            
            for domain in node.domains:
                btn = ctk.CTkButton(
                    domain_frame,
                    text=domain.value,
                    font=self.theme.font_small,
                    fg_color=self.theme.accent_color,
                    hover_color=self.theme.accent_hover,
                    height=30,
                    command=lambda d=domain: self.on_domain_select(d)
                )
                btn.pack(side="left", padx=(0, 5))
    
    def _create_category_cards(self, nodes: List[AgentNode]):
        """Create cards for all nodes"""
        for node in nodes:
            self._create_agent_card(node, is_category=bool(node.children))
            if node.children:
                self._create_category_cards(node.children)
    
    def _on_search(self, *args):
        """Filter cards based on search text"""
        search_text = self.search_var.get().lower()
        
        # Clear and recreate cards based on search
        for widget in self.content.winfo_children():
            widget.destroy()
        
        def should_show_node(node: AgentNode) -> bool:
            return (search_text in node.name.lower() or 
                   search_text in node.description.lower())
        
        def filter_nodes(nodes: List[AgentNode]) -> List[AgentNode]:
            filtered = []
            for node in nodes:
                if should_show_node(node):
                    filtered.append(node)
                elif node.children:
                    child_results = filter_nodes(node.children)
                    if child_results:
                        filtered.extend(child_results)
            return filtered
        
        filtered_nodes = filter_nodes(self.tree)
        self._create_category_cards(filtered_nodes)
    
    def _create_agent_tree(self) -> List[AgentNode]:
        """Create the agent hierarchy"""
        return AgentTree.create_agent_tree()