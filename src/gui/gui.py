import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from ..core.idea_processor import IdeaProcessor
import logging
from PIL import Image, ImageTk
import math
import base64
import io
from src.core.domain_types import DomainType
from src.gui.layers import LayerSystem
from .theme import UITheme
from .animations import FloatingAnimation
from src.agents.agent_factory import AgentFactory
from .agent_tree import AgentTree, AgentTreeView

class ProgressIndicator:
    def __init__(self, parent, theme: UITheme):
        self.frame = ctk.CTkFrame(parent, fg_color=theme.bg_secondary)
        self.progress_bar = ctk.CTkProgressBar(
            self.frame,
            fg_color=theme.bg_tertiary,
            progress_color=theme.accent_color,
            width=200
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)
        
        self.label = ctk.CTkLabel(
            self.frame,
            text="Processing...",
            font=theme.font_small,
            text_color=theme.text_secondary
        )
        self.label.pack(pady=5)
        self.frame.place_forget()
    
    def show(self, x: float = None, y: float = None):
        """Show progress indicator at the bottom center by default"""
        self.frame.place(relx=0.5, rely=0.95, anchor='s')  # 's' anchor for bottom alignment
        self.progress_bar.start()
    
    def hide(self):
        self.progress_bar.stop()
        self.frame.place_forget()
    
    def update_text(self, text: str):
        self.label.configure(text=text)

class Layer3DGUI:
    def __init__(self, system: IdeaProcessor, fullscreen: bool = False):
        self.root = tk.Tk()
        self.root.title("Hephaestus")
        
        # Initialize single theme
        self.current_theme = UITheme()
        self.data_manager = system.data_manager
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Set default window size if not fullscreen
        if fullscreen:
            self.root.attributes('-fullscreen', True)
            self.window_width = self.screen_width
            self.window_height = self.screen_height
        else:
            # Set to 80% of screen size
            self.window_width = int(self.screen_width * 0.8)
            self.window_height = int(self.screen_height * 0.8)
            
            # Center the window
            x = (self.screen_width - self.window_width) // 2
            y = (self.screen_height - self.window_height) // 2
            
            self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        
        # Ensure window opens in front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        
        self.root.configure(bg=self.current_theme.bg_color)
        
        # Use the provided system instance
        self.system = system
        self.current_layer = 0
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Replace layers initialization with LayerSystem
        self.layer_system = LayerSystem(
            self.root, 
            self.current_theme, 
            self.window_width, 
            self.window_height,
            self.data_manager
        )
        
        # Initialize layers
        self.setup_layers()
        
        # Bind escape key to exit only in fullscreen mode
        if fullscreen:
            self.root.bind('<Escape>', lambda e: self.root.quit())
        
        self.progress = ProgressIndicator(self.root, self.current_theme)
        self.floating_animation = None  # Will be initialized in setup_prompt_layer
        self.selected_supporting_domains = []  # Track selected supporting domains
        self.agent_tree = AgentTree()

    def setup_layers(self):
        # Initialize prompt layer
        self.setup_prompt_layer()

    def setup_prompt_layer(self):
        # Get the prompt layer
        prompt_layer = self.layer_system.layers[0]
        
        # Create floating entry frame with fixed width
        self.entry_frame = ctk.CTkFrame(
            prompt_layer.frame,
            fg_color=self.current_theme.bg_secondary,
            border_width=2,
            border_color=self.current_theme.border_color,
            corner_radius=15,
            width=600
        )
        
        # Add forge icon or decorative element
        self.forge_label = ctk.CTkLabel(
            self.entry_frame,
            text="⚒️",
            font=('Segoe UI Emoji', 24)
        )
        self.forge_label.pack(pady=(20, 0))
        
        # Add subtle prompt text
        self.prompt_label = ctk.CTkLabel(
            self.entry_frame,
            text="Speak your mind bro...",
            font=self.current_theme.font_title,
            text_color=self.current_theme.text_secondary
        )
        self.prompt_label.pack(pady=(5, 10))
        
        # Create a container frame for the entry
        entry_container = ctk.CTkFrame(
            self.entry_frame,
            fg_color=self.current_theme.bg_tertiary,
            width=400,
            height=45
        )
        entry_container.pack(pady=(0, 20))
        entry_container.pack_propagate(False)
        
        # Update input entry styling
        self.input_entry = ctk.CTkEntry(
            entry_container,
            placeholder_text="Speak it here...",
            font=self.current_theme.font,
            text_color=self.current_theme.text_color,
            border_color=self.current_theme.border_color,
            fg_color=self.current_theme.input_bg,
            placeholder_text_color=self.current_theme.text_disabled,
            height=45,
            width=380
        )
        self.input_entry.pack(expand=True)
        
        # Add chat button
        self.chat_button = ctk.CTkButton(
            self.entry_frame,
            text="Open Chat",
            command=self.show_chat_layer,
            font=self.current_theme.font_bold,
            fg_color=self.current_theme.button_bg,
            hover_color=self.current_theme.button_hover,
            text_color=self.current_theme.text_color,
            width=120,
            height=35
        )
        self.chat_button.pack(pady=(0, 20))
        
        # Center the entry frame
        self.entry_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Bind enter key
        self.input_entry.bind('<Return>', self.process_initial_input)
        
        # Initialize and start floating animation
        self.floating_animation = FloatingAnimation(self.root, self.entry_frame, self.current_theme)
        self.floating_animation.start()
        
        # Bind window resize event to recenter entry frame
        self.root.bind('<Configure>', self._on_window_resize)
        
        # Add domain selection frame
        self.domain_frame = ctk.CTkFrame(
            self.entry_frame,
            fg_color=self.current_theme.bg_tertiary
        )
        self.domain_frame.pack(pady=(0, 20))

        # Add supporting domains selector
        self.domain_vars = {}
        for domain in DomainType:
            var = tk.BooleanVar()
            self.domain_vars[domain] = var
            ctk.CTkCheckBox(
                self.domain_frame,
                text=domain.value.title(),
                variable=var,
                command=self._update_supporting_domains,
                font=self.current_theme.font_small
            ).pack(side='left', padx=5)

    def _update_supporting_domains(self):
        """Update the list of selected supporting domains"""
        self.selected_supporting_domains = [
            domain for domain, var in self.domain_vars.items() 
            if var.get()
        ]

    def setup_questions_layer(self, questions):
        # Get the prompt layer frame
        layer_frame = self.layer_system.get_layer(1)
        
        # Clear existing widgets from the frame
        for widget in layer_frame.winfo_children():
            widget.destroy()
        
        # Create questions display
        questions_frame = ctk.CTkFrame(layer_frame, fg_color='transparent')
        
        ctk.CTkLabel(
            questions_frame,
            text="To better understand your idea, please answer these questions:",
            font=self.current_theme.font,
            text_color=self.current_theme.text_color
        ).pack(pady=20)
        
        self.question_entries = []
        for i, question in enumerate(questions):
            ctk.CTkLabel(
                questions_frame,
                text=question,
                font=self.current_theme.font,
                text_color=self.current_theme.text_color
            ).pack(pady=5)
            
            entry = ctk.CTkEntry(questions_frame, width=500)
            entry.pack(pady=(0, 20))
            self.question_entries.append(entry)
        
        # Add button frame for multiple buttons
        button_frame = ctk.CTkFrame(questions_frame, fg_color='transparent')
        button_frame.pack(pady=20)
        
        # Generate Ideas button
        ctk.CTkButton(
            button_frame,
            text="Generate Ideas",
            command=self.process_questions
        ).pack(side='left', padx=10)
        
        # Skip button
        ctk.CTkButton(
            button_frame,
            text="Skip Questions",
            command=self.skip_questions,
            fg_color=self.current_theme.accent_color,
            hover_color=self.current_theme.accent_color
        ).pack(side='left', padx=10)
        
        questions_frame.place(relx=0.5, rely=0.5, anchor='center')

    def skip_questions(self):
        # Process the initial concept directly without additional context
        final_result = self.system.develop_idea(self.initial_result['idea']['concept'])
        
        # Setup and show results layer
        self.setup_results_layer(final_result)
        self.transition_to_layer(2)

    def setup_results_layer(self, results):
        layer_frame = self.layer_system.get_layer(2)
        
        # Clear existing widgets
        for widget in layer_frame.winfo_children():
            widget.destroy()
        
        # Create main content frame
        content_frame = ctk.CTkFrame(layer_frame, fg_color='transparent')
        content_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            content_frame,
            text=f"Ideas for: {results['idea']['concept']}",
            font=self.current_theme.font,
            text_color=self.current_theme.text_color
        ).pack(pady=(0, 20))
        
        # Create horizontal layout frame
        horizontal_frame = ctk.CTkFrame(content_frame, fg_color='transparent')
        horizontal_frame.pack(expand=True, fill='both')
        
        # Left side - Text content
        text_frame = ctk.CTkFrame(horizontal_frame, fg_color='transparent')
        text_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Text area
        text_area = ctk.CTkTextbox(
            text_frame,
            width=600,  # Adjusted width
            height=500,
            font=self.current_theme.font
        )
        text_area.pack(expand=True, fill='both')
        
        # Format and insert results
        formatted_text = self.format_results(results)
        text_area.insert('1.0', formatted_text)
        text_area.configure(state='disabled')
        
        # Right side - Image (if available)
        if results['development'].get('concept_image'):
            try:
                img_data = base64.b64decode(results['development']['concept_image'])
                img = Image.open(io.BytesIO(img_data))
                
                # Create image frame
                image_frame = ctk.CTkFrame(
                    horizontal_frame,
                    fg_color=self.current_theme.bg_secondary,
                    border_width=1,
                    border_color=self.current_theme.border_color
                )
                image_frame.pack(side='right', fill='y', padx=(10, 0))
                
                # Calculate appropriate image size
                max_width = min(self.window_width // 3, 400)
                max_height = min(self.window_height // 2, 400)
                
                # Resize image while maintaining aspect ratio
                img_width, img_height = img.size
                scale = min(max_width/img_width, max_height/img_height)
                new_size = (int(img_width * scale), int(img_height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Display image
                photo = ImageTk.PhotoImage(img)
                img_label = ttk.Label(image_frame, image=photo)
                img_label.image = photo
                img_label.pack(pady=10, padx=10)
                
                # Add caption
                ctk.CTkLabel(
                    image_frame,
                    text="Concept Visualization",
                    font=self.current_theme.font_small,
                    text_color=self.current_theme.text_secondary
                ).pack(pady=(0, 10))
                
            except Exception as e:
                self.logger.error(f"Error displaying concept image: {str(e)}")
        
        # Modify the button to go to next steps instead of restart
        ctk.CTkButton(
            content_frame,
            text="View Implementation Plan",
            command=lambda: self.show_next_steps(results)
        ).pack(pady=20)
        
        content_frame.place(relx=0.5, rely=0.5, anchor='center')

    def format_results(self, results):
        development = results['development']
        
        formatted = f"""Domain: {results['idea']['domain'].title()}
Keywords: {', '.join(results['idea']['keywords'])}
{f"Supporting Domains: {', '.join(d.title() for d in results['idea']['supporting_domains'])}" if results['idea'].get('supporting_domains') else ""}

Suggestions:
{self._format_list(development['suggestions'])}

Related Concepts:
{self._format_list(development['related_concepts'])}

Implementation Steps:
{self._format_list(development['implementation_steps']) if development['implementation_steps'] else 'No implementation steps provided.'}
"""
        return formatted

    def _format_list(self, items):
        return '\n'.join(f"• {item}" for item in items)

    def transition_to_layer(self, layer_index):
        if self.floating_animation:
            self.floating_animation.stop()
        self.layer_system.transition_to_layer(layer_index)
        self.current_layer = layer_index
        if layer_index == 0 and self.floating_animation:
            self.floating_animation.start()

    def process_initial_input(self, event=None):
        initial_concept = self.input_entry.get().strip()
        if not initial_concept:
            return
        
        self.progress.show()
        self.progress.update_text("Analyzing concept...")
        
        def process_in_thread():
            try:
                # Pass selected supporting domains to develop_idea
                result = self.system.develop_idea(
                    initial_concept, 
                    supporting_domains=self.selected_supporting_domains
                )
                self.initial_result = result
                self.root.after(0, lambda: self._update_after_processing(result))
            except Exception as error:
                error_msg = str(error)
                self.root.after(0, lambda: self._handle_processing_error(error_msg))
            finally:
                self.root.after(0, self.progress.hide)
        
        import threading
        thread = threading.Thread(target=process_in_thread, daemon=True)
        thread.start()

    def _update_after_processing(self, result):
        """Update GUI after processing completes"""
        self.progress.update_text("Updating interface...")
        self.update_theme(DomainType(result['idea']['domain']))
        self.setup_questions_layer(result['development']['questions'])
        self.transition_to_layer(1)

    def _handle_processing_error(self, error_msg):
        """Handle any errors during processing"""
        from tkinter import messagebox
        messagebox.showerror("Error", f"An error occurred: {error_msg}")

    def process_questions(self):
        """Process question responses in a separate thread"""
        self.progress.show()
        self.progress.update_text("Processing responses...")
        
        def process_in_thread():
            try:
                answers = [entry.get() for entry in self.question_entries]
                enhanced_concept = (f"{self.initial_result['idea']['concept']} - "
                                  f"Additional Context: {' | '.join(answers)}")
                
                self.root.after(0, lambda: self.progress.update_text("Generating enhanced results..."))
                final_result = self.system.develop_idea(enhanced_concept)
                
                self.root.after(0, lambda: self.progress.update_text("Preparing visualization..."))
                self.root.after(0, lambda: self._handle_questions_result(final_result))
                
            except Exception as error:
                error_msg = str(error)  # Capture error message in closure scope
                self.root.after(0, lambda: self._handle_processing_error(error_msg))
            finally:
                self.root.after(0, self.progress.hide)
        
        import threading
        thread = threading.Thread(target=process_in_thread, daemon=True)
        thread.start()

    def _handle_questions_result(self, final_result):
        """Handle the results from question processing"""
        self.setup_results_layer(final_result)
        self.transition_to_layer(2)

    def restart(self):
        # Clear and reset to initial layer
        self.input_entry.delete(0, tk.END)
        self.transition_to_layer(0)
        if self.floating_animation:
            self.floating_animation.start()

    def show_next_steps(self, results):
        try:
            self.progress.show()
            self.progress.update_text("Generating implementation plan...")
            
            layer_frame = self.layer_system.get_layer(3)
            
            # Clear existing widgets
            for widget in layer_frame.winfo_children():
                widget.destroy()
            
            next_steps_frame = ctk.CTkFrame(layer_frame, fg_color='transparent')
            
            # Title
            self._create_title_label(next_steps_frame, "Implementation Plan")
            
            if results['development'].get('next_steps_tree'):
                self._create_diagram_frame(next_steps_frame, results)
            
            self._create_navigation_buttons(next_steps_frame)
            next_steps_frame.place(relx=0.5, rely=0.5, anchor='center')
            self.transition_to_layer(3)
            
        finally:
            self.progress.hide()

    def _create_title_label(self, parent, text):
        return ctk.CTkLabel(
            parent,
            text=text,
            font=self.current_theme.font_header,
            text_color=self.current_theme.text_color
        ).pack(pady=20)

    def _create_diagram_frame(self, parent, results):
        try:
            diagram_frame = ctk.CTkFrame(
                parent,
                fg_color=self.current_theme.bg_secondary,
                border_width=1,
                border_color=self.current_theme.border_color,
                width=800,
                height=500
            )
            diagram_frame.pack(pady=20, padx=20, fill='both', expand=True)
            
            img_data = base64.b64decode(results['development']['next_steps_tree'])
            img = Image.open(io.BytesIO(img_data))
            
            # Optimize image loading
            max_size = (700, 400)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            img_label = ttk.Label(diagram_frame, image=photo)
            img_label.image = photo
            img_label.pack(pady=10)
            
        except Exception as e:
            self.logger.error(f"Error displaying diagram: {str(e)}")
            self._show_error_message(parent)

    def _show_error_message(self, parent):
        ctk.CTkLabel(
            parent,
            text="Error displaying diagram.",
            text_color=self.current_theme.text_color
        ).pack(pady=20)

    def copy_to_clipboard(self, text):
        """Helper method to copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

    def open_mermaid_editor(self, mermaid_code):
        """Open the Mermaid Live Editor with the current diagram"""
        import webbrowser
        import urllib.parse
        
        base_url = "https://mermaid.live/edit#pako:"
        encoded_code = urllib.parse.quote(mermaid_code)
        webbrowser.open(f"{base_url}{encoded_code}")

    def update_theme(self, domain: DomainType):
        """Theme updates are no longer needed as we use a single theme"""
        pass

    def _on_window_resize(self, event):
        """Handle window resize events to maintain centering"""
        if event.widget == self.root:
            # Update window dimensions
            self.window_width = event.width
            self.window_height = event.height
            
            # Recenter entry frame if it's visible
            if self.current_layer == 0:
                self.entry_frame.place(relx=0.5, rely=0.5, anchor='center')

    def show_chat_layer(self):
        """Show chat interface with selected agent"""
        chat_layer = self.layer_system.layers[4]  # Get chat layer
        
        # Set callbacks
        chat_layer.on_agent_changed = self._on_agent_changed
        chat_layer.on_back_pressed = lambda: self.transition_to_layer(2)
        
        # Bind chat return handler
        chat_layer.chat_input.bind('<Return>', self._handle_chat_return)
        
        # Show the layer
        self.transition_to_layer(4)

    def _on_agent_changed(self, domain: DomainType):
        """Handle changing the current chat agent"""
        self.current_agent = AgentFactory.create_agent(domain)
        # Update theme to match new agent's domain
        self.update_theme(UITheme.get_theme())

    def _handle_chat_return(self, event):
        if not event.state & 0x1:  # Shift key is not pressed
            self.send_chat_message()
            return 'break'  # Prevent default newline

    def send_chat_message(self):
        chat_layer = self.layer_system.layers[4]
        message = chat_layer.get_message()
        
        if not message:
            return
        
        chat_layer.clear_input()
        domain = self.current_agent.domain.value
        
        # Add user message immediately
        chat_layer.chat_manager.add_message("You", message, domain)
        chat_layer.add_message("You", message)
        
        self.progress.show()
        
        def process_chat_in_thread():
            try:
                response = self.current_agent.chat_response(message)
                self.root.after(0, lambda: self._update_chat(chat_layer, response, domain))
            except Exception as error:
                error_msg = str(error)  # Capture error message in closure scope
                self.root.after(0, lambda: self._handle_processing_error(error_msg))
            finally:
                self.root.after(0, self.progress.hide)
        
        import threading
        thread = threading.Thread(target=process_chat_in_thread, daemon=True)
        thread.start()

    def _update_chat(self, chat_layer, response, domain):
        """Update chat with agent response"""
        chat_layer.chat_manager.add_message("Agent", response, domain)
        chat_layer.add_message("Agent", response)

    def run(self):
        self.root.mainloop()

    def cleanup(self):
        """No need to explicitly save chat history as it's handled by DataManager"""
        pass

    def _create_navigation_buttons(self, parent):
        """Create navigation buttons for the implementation plan view
        
        Args:
            parent: The parent frame to add the buttons to
        """
        button_frame = ctk.CTkFrame(parent, fg_color='transparent')
        button_frame.pack(pady=20)
        
        # Back button to return to results
        ctk.CTkButton(
            button_frame,
            text="Back to Results",
            command=lambda: self.transition_to_layer(2),
            font=self.current_theme.font_bold,
            fg_color=self.current_theme.button_bg,
            hover_color=self.current_theme.button_hover,
            text_color=self.current_theme.text_color
        ).pack(side='left', padx=10)
        
        # Restart button
        ctk.CTkButton(
            button_frame,
            text="Start Over",
            command=self.restart,
            font=self.current_theme.font_bold,
            fg_color=self.current_theme.accent_color,
            hover_color=self.current_theme.accent_hover,
            text_color=self.current_theme.text_color
        ).pack(side='left', padx=10)