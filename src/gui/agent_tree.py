from dataclasses import dataclass
from typing import List, Optional, Dict
from src.core.domain_types import DomainType
import customtkinter as ctk
from .theme import UITheme
from .animations import NodeCenteringAnimation

@dataclass
class AgentTreeNode:
    name: str
    description: str
    icon: str = "🔹"  # Default icon, can be customized per node
    domains: Optional[List[DomainType]] = None
    children: Optional[List['AgentTreeNode']] = None
    expanded: bool = False
    
class AgentTreeView(ctk.CTkFrame):
    def __init__(self, parent, theme: UITheme, on_select=None):
        super().__init__(parent, fg_color="transparent")
        self.theme = theme
        self.on_select = on_select
        self.node_frames = {}
        
        # Add scrollbar
        self.scrollbar = ctk.CTkScrollbar(self)
        self.scrollbar.pack(side='right', fill='y')
        
        self.canvas = ctk.CTkCanvas(
            self,
            background=self.theme.bg_color,
            highlightthickness=0,
            yscrollcommand=self.scrollbar.set
        )
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.configure(command=self.canvas.yview)
        
        # Inner frame for nodes
        self.inner_frame = ctk.CTkFrame(
            self.canvas,
            fg_color=self.theme.bg_secondary
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')
        
        # Bind configuration events
        self.inner_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Add mouse wheel binding for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.animation = NodeCenteringAnimation(parent, self.inner_frame, theme)
        self.centered_node = None
        
        self.tree = AgentTree()
        # Set root node to expanded by default
        self.tree.root.expanded = True
        self._populate_tree(self.tree.root)
    
    def _on_frame_configure(self, event=None):
        """Update the scroll region when the inner frame changes size"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Resize the inner frame when the canvas changes size"""
        width = event.width
        self.canvas.itemconfig(self.canvas_window, width=width)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_node(self, node: AgentTreeNode, level: int = 0, parent_pos=None):
        # Node container
        container = ctk.CTkFrame(
            self.inner_frame,
            fg_color="transparent"
        )
        
        # Pack container with reduced spacing
        if level == 0:
            container.pack(fill='x', pady=(10, 20))  # Reduced root spacing
        else:
            container.pack(fill='x', pady=5)  # Reduced general spacing
        
        # Node bubble with border
        bubble = ctk.CTkFrame(
            container,
            fg_color=self.theme.bg_tertiary,
            corner_radius=12,  # Slightly smaller corners
            border_width=1,
            border_color=self.theme.border_color
        )
        bubble.pack(anchor='center')
        
        # Content layout with reduced padding
        content = ctk.CTkFrame(bubble, fg_color="transparent")
        content.pack(padx=10, pady=5)  # Reduced padding
        
        # Icon/expand button with reduced size
        if node.children:
            expand_btn = ctk.CTkButton(
                content,
                text="⊕" if not node.expanded else "⊖",
                width=20,  # Smaller button
                height=20,
                corner_radius=10,
                font=(self.theme.font[0], 10),
                fg_color=self.theme.accent_color,
                hover_color=self.theme.accent_hover,
                command=lambda: self.toggle_node(node, container, parent_pos)
            )
            expand_btn.pack(pady=(0, 3))  # Reduced spacing
            self.node_frames[id(node)] = {
                "container": container,
                "button": expand_btn,
                "bubble": bubble
            }
        else:
            icon = ctk.CTkLabel(
                content,
                text=node.icon,
                font=(self.theme.font[0], 12)  # Smaller icon
            )
            icon.pack()

        # Title and description with reduced spacing
        title = ctk.CTkLabel(
            content,
            text=node.name,
            font=self.theme.font_bold,
            text_color=self.theme.text_color
        )
        title.pack(pady=(0, 2))  # Reduced spacing
        
        description = ctk.CTkLabel(
            content,
            text=node.description,
            font=self.theme.font_small,
            text_color=self.theme.text_secondary,
            wraplength=180  # Slightly narrower text wrap
        )
        description.pack()
        
        # Add domain buttons if present
        if node.domains:
            domain_frame = ctk.CTkFrame(content, fg_color="transparent")
            domain_frame.pack(pady=(5, 0))
            for domain in node.domains:
                domain_btn = ctk.CTkButton(
                    domain_frame,
                    text=domain.value,
                    font=self.theme.font_small,
                    fg_color=self.theme.accent_color,
                    hover_color=self.theme.accent_hover,
                    width=80,
                    height=25,
                    command=lambda d=domain: self.on_select(d) if self.on_select else None
                )
                domain_btn.pack(side='left', padx=2)
        
        # Draw connecting lines after node is created
        if parent_pos and level > 0:
            self.draw_connection(parent_pos, bubble)
        
        # Add click handler for top-level nodes
        if level == 0:
            bubble.bind('<Button-1>', lambda e: self._handle_node_click(node, bubble))
        
        return bubble

    def draw_connection(self, parent_bubble, child_bubble):
        def update_line():
            # Get positions
            px = parent_bubble.winfo_x() + parent_bubble.winfo_width() // 2
            py = parent_bubble.winfo_y() + parent_bubble.winfo_height()
            cx = child_bubble.winfo_x() + child_bubble.winfo_width() // 2
            cy = child_bubble.winfo_y()
            
            # Draw connecting lines with shorter vertical gaps
            if abs(px - cx) > 10:
                # Shorter vertical segments
                self.canvas.create_line(
                    px, py, px, py + 10,  # Reduced vertical gap
                    fill=self.theme.border_color,
                    width=1  # Thinner lines
                )
                self.canvas.create_line(
                    px, py + 10, cx, py + 10,
                    fill=self.theme.border_color,
                    width=1
                )
                self.canvas.create_line(
                    cx, py + 10, cx, cy,
                    fill=self.theme.border_color,
                    width=1
                )
            else:
                self.canvas.create_line(
                    px, py, cx, cy,
                    fill=self.theme.border_color,
                    width=1
                )
        
        self.after(10, update_line)

    def toggle_node(self, node: AgentTreeNode, container, parent_pos):
        """Toggle node expansion state and update display"""
        node.expanded = not node.expanded
        
        # Store current node's bubble
        current_bubble = self.node_frames[id(node)]["bubble"]
        
        # Clear existing children first
        current_index = self.inner_frame.winfo_children().index(container)
        for widget in self.inner_frame.winfo_children()[current_index + 1:]:
            widget.destroy()
        
        if node.expanded:
            # Get only valid (non-destroyed) nodes at the same level
            same_level_nodes = []
            for frame_id, frame in self.node_frames.items():
                if frame_id != id(node) and 'bubble' in frame:
                    try:
                        # Check if widget still exists
                        frame['bubble'].winfo_exists()
                        same_level_nodes.append(frame['bubble'])
                    except:
                        continue
            
            # Fade other nodes if they still exist
            for other_node in same_level_nodes:
                try:
                    other_node.configure(fg_color=self.theme.bg_secondary)
                except:
                    continue
            
            # Add children centered below
            if node.children:
                child_container = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
                child_container.pack(fill='x', expand=True, pady=20)
                
                # Create children horizontally for same level
                for child in node.children:
                    child_bubble = self.create_node(child, level=1, parent_pos=current_bubble)
                    child_bubble.pack(side='left', padx=10)  # Pack horizontally
                    self.draw_connection(current_bubble, child_bubble)
        else:
            # Reset colors of existing nodes
            for frame_id, frame in self.node_frames.items():
                if 'bubble' in frame:
                    try:
                        frame['bubble'].configure(fg_color=self.theme.bg_tertiary)
                    except:
                        continue
        
        # Update button text
        if id(node) in self.node_frames and 'button' in self.node_frames[id(node)]:
            try:
                self.node_frames[id(node)]["button"].configure(
                    text="⊖" if node.expanded else "⊕"
                )
            except:
                pass
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _redraw_children(self, node: AgentTreeNode, container, parent_pos):
        """Helper method to redraw children after animation"""
        current_bubble = self.node_frames[id(node)]["bubble"]
        
        if node.children:
            # Create container for children
            child_container = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
            child_container.pack(fill='x', expand=True)
            
            # Create all children in the same container
            for child in node.children:
                child_bubble = self.create_node(child, 1, current_bubble)
                self.draw_connection(current_bubble, child_bubble)
                
                # If this child has children and is expanded, create them
                if child.children and child.expanded:
                    grandchild_container = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
                    grandchild_container.pack(fill='x', expand=True)
                    for grandchild in child.children:
                        grandchild_bubble = self.create_node(grandchild, 2, child_bubble)
                        self.draw_connection(child_bubble, grandchild_bubble)

    def _handle_node_click(self, node: AgentTreeNode, bubble: ctk.CTkFrame):
        """Handle clicking on a node"""
        # Don't animate if it's already centered
        if self.centered_node == node:
            return
        
        # Reset previous centered node if exists
        if self.centered_node and id(self.centered_node) in self.node_frames:
            prev_bubble = self.node_frames[id(self.centered_node)]["bubble"]
            self.animation.reset_nodes([prev_bubble])
        
        # Center the clicked node and fade others
        self.animation.center_node(bubble)
        self.centered_node = node
        
        # Collapse other nodes
        for other_id, other_frame in self.node_frames.items():
            if other_id != id(node):
                if "button" in other_frame:
                    other_node = next((n for n in self._get_all_nodes(self.tree.root) 
                                     if id(n) == other_id), None)
                    if other_node and other_node.expanded:
                        other_node.expanded = False
                        self.toggle_node(other_node, other_frame["container"], None)

    def _get_all_nodes(self, root_node: AgentTreeNode) -> List[AgentTreeNode]:
        """Helper method to get all nodes in the tree"""
        nodes = [root_node]
        if root_node.children:
            for child in root_node.children:
                nodes.extend(self._get_all_nodes(child))
        return nodes

    def _populate_tree(self, root_node: AgentTreeNode, level: int = 0, parent_pos=None):
        """Recursively populate the tree starting from root"""
        bubble = self.create_node(root_node, level, parent_pos)
        
        if root_node.children and root_node.expanded:
            # Create container for children
            child_container = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
            child_container.pack(fill='x', expand=True)
            
            # Create all children in the same container
            for child in root_node.children:
                child_bubble = self.create_node(child, level + 1, bubble)
                self.draw_connection(bubble, child_bubble)
                
                # If this child has children and is expanded, create them in a new vertical container
                if child.children and child.expanded:
                    grandchild_container = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
                    grandchild_container.pack(fill='x', expand=True)
                    for grandchild in child.children:
                        grandchild_bubble = self.create_node(grandchild, level + 2, child_bubble)
                        self.draw_connection(child_bubble, grandchild_bubble)

class AgentTree:
    def __init__(self):
        self.root = AgentTreeNode(
            name="Agent Categories",
            description="Select a category to explore available agents",
            icon="🔍",
            children=[
                AgentTreeNode(
                    name="Technology",
                    description="Technical and engineering focused agents",
                    icon="💻",
                    children=[
                        AgentTreeNode(
                            name="Technical",
                            description="Software, hardware, and general technology expertise",
                            icon="⚙️",
                            domains=[DomainType.TECHNOLOGY, DomainType.CODE]
                        )
                    ]
                ),
                AgentTreeNode(
                    name="Humanities",
                    description="Arts, culture, and theoretical knowledge",
                    icon="🎭",
                    children=[
                        AgentTreeNode(
                            name="Arts & Culture",
                            description="Creative and cultural expertise",
                            icon="🎨",
                            domains=[DomainType.LITERATURE, DomainType.ARTS]
                        ),
                        AgentTreeNode(
                            name="Theory",
                            description="Scientific and philosophical understanding",
                            icon="🔬",
                            domains=[DomainType.HARD_SCIENCE, DomainType.PHILOSOPHY, DomainType.SOCIAL_SCIENCE]
                        )
                    ]
                ),
                AgentTreeNode(
                    name="Practical",
                    description="Real-world application and business expertise",
                    icon="💼",
                    children=[
                        AgentTreeNode(
                            name="Business",
                            description="Business strategy and management",
                            icon="📊",
                            domains=[DomainType.BUSINESS]
                        )
                    ]
                )
            ]
        )
    
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