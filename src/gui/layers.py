import tkinter as tk
from src.gui.theme import UITheme
from src.data.chat_history import ChatHistoryManager
from src.data.data_manager import DataManager
from src.agents.agent_factory import AgentFactory
from src.core.domain_types import DomainType
import customtkinter as ctk
from .agent_tree import AgentTree, AgentTreeNode

class Layer:
    def __init__(self, root, theme: UITheme, window_width: int, window_height: int):
        self.root = root
        
        # Create a main container frame
        self.container = ctk.CTkFrame(
            root,
            fg_color=theme.bg_color,
            width=window_width,
            height=window_height
        )
        self.container.pack_propagate(False)  # Prevent container from shrinking
        self.container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Content frame for actual content
        self.frame = ctk.CTkFrame(
            self.container,
            fg_color='transparent',
            width=window_width,
            height=window_height
        )
        self.frame.pack(expand=True, fill='both')  # Fill the container
        self.frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Hide initially
        self.container.place_forget()
        
        # Add a property to track content state
        self.content_ready = False
        self.theme = theme  # Store theme reference

    def show(self):
        """Show the layer and ensure content is visible"""
        self.container.place(relx=0.5, rely=0.5, anchor='center')
        self.container.lift()  # Ensure layer is on top
        self.frame.lift()      # Ensure frame is visible
        
        # Ensure all child widgets are properly displayed
        for widget in self.frame.winfo_children():
            widget.lift()
        
        self.container.update()
        self.frame.update()

    def hide(self):
        self.container.place_forget()

    def clear(self):
        """Clear all widgets and reset content state"""
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.content_ready = False

    def delete(self, tag):
        # This method is added for compatibility with canvas-style calls
        self.clear()

    def update_safely(self, func):
        """Execute GUI updates safely from any thread"""
        self.root.after(0, func)

class ChatLayer(Layer):
    def __init__(self, root, theme: UITheme, window_width: int, window_height: int, data_manager: DataManager):
        super().__init__(root, theme, window_width, window_height)
        self.chat_manager = ChatHistoryManager(data_manager)
        self.theme = theme
        self.agent_tree = AgentTree()
        self.setup_chat_interface()
    
    def setup_chat_interface(self):
        # Main chat container
        chat_container = ctk.CTkFrame(
            self.frame,
            fg_color='transparent',
            width=800,
            height=600
        )
        chat_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Add agent selection at the top
        agent_frame = ctk.CTkFrame(
            chat_container,
            fg_color='transparent'
        )
        agent_frame.pack(pady=(0, 10))
        
        self.agent_tree_button = ctk.CTkButton(
            agent_frame,
            text="Agent Tree",
            command=self._show_agent_tree,
            font=self.theme.font,
            fg_color=self.theme.accent_color,
            hover_color=self.theme.accent_hover
        )
        self.agent_tree_button.pack(side='left')
        
        # Chat history display
        self.chat_history = ctk.CTkTextbox(
            chat_container,
            width=700,
            height=400,
            font=self.theme.font,
            state='disabled'
        )
        self.chat_history.pack(pady=20, fill='both', expand=True)
        
        # Chat input frame with fixed width
        input_frame = ctk.CTkFrame(
            chat_container,
            fg_color='transparent',
            width=700,  # Match chat history width
            height=100  # Increased height to accommodate multiple lines
        )
        input_frame.pack(pady=(0, 20))
        input_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Chat input as text widget instead of entry
        self.chat_input = ctk.CTkTextbox(
            input_frame,
            height=45,  # Initial height
            width=680,  # Slightly less than frame width
            font=self.theme.font,
            text_color=self.theme.text_color,
            border_color=self.theme.border_color,
            fg_color=self.theme.secondary_color,
            wrap='word'  # Enable word wrapping
        )
        self.chat_input.pack(side='left', padx=10, pady=10, fill='both', expand=True)
        
        # Bind text changes to adjust height
        self.chat_input.bind('<KeyRelease>', self._adjust_input_height)
        
        # Back button
        back_button = ctk.CTkButton(
            chat_container,
            text="Back",
            command=lambda: self.on_back_pressed() if hasattr(self, 'on_back_pressed') else None,
            fg_color=self.theme.accent_color,
            width=120,
            height=35
        )
        back_button.pack(pady=10)

    def _adjust_input_height(self, event=None):
        # Get number of lines
        text = self.chat_input.get("1.0", "end-1c")
        num_lines = len(text.split('\n'))
        
        # Calculate new height (limit to 4 lines)
        line_height = 25  # Approximate height per line
        new_height = min(max(45, num_lines * line_height), 100)  # Min 45px, Max 100px
        
        # Update textbox height
        self.chat_input.configure(height=new_height)

    def add_message(self, sender: str, message: str):
        self.chat_history.configure(state='normal')
        self.chat_history.insert('end', f"\n{sender}: {message}")
        self.chat_history.configure(state='disabled')
        self.chat_history.see('end')

    def clear_input(self):
        self.chat_input.delete("1.0", "end")
        self._adjust_input_height()  # Reset height

    def get_message(self):
        return self.chat_input.get("1.0", "end-1c").strip()

    def _show_agent_tree(self):
        """Show agent tree selection dialog"""
        tree_window = ctk.CTkToplevel(self.root)
        tree_window.title("Select Agent")
        tree_window.geometry("400x500")
        
        def create_tree_node(parent, node: AgentTreeNode):
            frame = ctk.CTkFrame(parent, fg_color='transparent')
            frame.pack(fill='x', padx=(20, 0), pady=2)
            
            label = ctk.CTkLabel(
                frame,
                text=node.name,
                font=self.theme.font_bold if node.domains else self.theme.font
            )
            label.pack(side='left')
            
            if node.domains:
                for domain in node.domains:
                    btn = ctk.CTkButton(
                        frame,
                        text=domain.value,
                        command=lambda d=domain: self._select_agent(d, tree_window),
                        font=self.theme.font_small,
                        fg_color=self.theme.button_bg,
                        hover_color=self.theme.button_hover,
                        width=100
                    )
                    btn.pack(side='right', padx=5)
            
            if node.children:
                for child in node.children:
                    create_tree_node(parent, child)
        
        tree_frame = ctk.CTkFrame(tree_window, fg_color=self.theme.bg_secondary)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        create_tree_node(tree_frame, self.agent_tree.root)
    
    def _select_agent(self, domain: DomainType, window: ctk.CTkToplevel):
        """Handle agent selection from tree"""
        if hasattr(self, 'on_agent_changed'):
            self.on_agent_changed(domain)
        window.destroy()

class LayerSystem:
    def __init__(self, root, theme: UITheme, window_width: int, window_height: int, data_manager: DataManager):
        self.root = root
        self.current_theme = theme
        self.window_width = window_width
        self.window_height = window_height
        self.current_layer = 0
        self.data_manager = data_manager
        
        # Initialize all layers with proper sizing
        self.layers = [
            Layer(root, theme, window_width, window_height) for _ in range(4)
        ]
        # Add chat layer
        self.layers.append(ChatLayer(root, theme, window_width, window_height, data_manager))
        
        # Show only the first layer
        self.layers[0].show()
        for layer in self.layers[1:]:
            layer.hide()

    def transition_to_layer(self, layer_index: int):
        # Hide current layer
        self.layers[self.current_layer].hide()
        # Show new layer
        self.layers[layer_index].show()
        self.current_layer = layer_index

    def update_theme(self, theme: UITheme):
        self.current_theme = theme
        for layer in self.layers:
            layer.container.configure(fg_color=theme.bg_color)

    def get_layer(self, layer_index: int) -> Layer:
        """
        Get a specific layer by index.
        
        Args:
            layer_index (int): Index of the layer to retrieve
            
        Returns:
            Layer: The requested layer
            
        Raises:
            IndexError: If layer_index is out of bounds
        """
        if 0 <= layer_index < len(self.layers):
            return self.layers[layer_index].frame
        raise IndexError(f"Layer index {layer_index} out of range")
        