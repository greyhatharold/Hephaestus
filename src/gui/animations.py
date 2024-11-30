import math
from typing import Callable
import customtkinter as ctk
from src.gui.theme import UITheme

class FloatingAnimation:
    def __init__(self, root: ctk.CTk, frame: ctk.CTkFrame, theme: UITheme):
        self.root = root
        self.frame = frame
        self.theme = theme
        self.is_running = False
        self.counter = 0
        
    def start(self):
        self.is_running = True
        self.counter = 0
        self._animate()
    
    def stop(self):
        self.is_running = False
    
    def _animate(self):
        if not self.is_running:
            return
            
        # Slower, more subtle floating motion
        t = math.sin(math.pi * self.counter / 45) * 7
        self.frame.place(rely=0.5 + t/self.root.winfo_screenheight())
        
        # Add subtle glow effect
        glow_intensity = abs(math.sin(math.pi * self.counter / 60))
        new_border_color = self._blend_colors(
            self.theme.border_color, 
            self.theme.accent_color, 
            glow_intensity
        )
        self.frame.configure(border_color=new_border_color)
        
        self.counter += 1
        self.root.after(50, self._animate)
    
    def _blend_colors(self, color1: str, color2: str, ratio: float) -> str:
        """Blend two hex colors together based on ratio"""
        # Convert hex to RGB
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        # Blend
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        
        return f'#{r:02x}{g:02x}{b:02x}' 

class NodeCenteringAnimation:
    def __init__(self, root: ctk.CTk, view_frame: ctk.CTkFrame, theme: UITheme):
        self.root = root
        self.view_frame = view_frame
        self.theme = theme
        self.is_running = False
        
    def center_node(self, node_bubble: ctk.CTkFrame, other_nodes=None):
        """Fade other nodes without moving the selected node"""
        if self.is_running:
            return
            
        self.is_running = True
        other_nodes = other_nodes or []
        
        # Fade other nodes
        for other_node in other_nodes:
            other_node.configure(fg_color=self._adjust_color_opacity(
                self.theme.bg_tertiary, 0.5
            ))
        
        self.is_running = False
    
    def reset_nodes(self, nodes):
        """Reset all nodes to their original state"""
        for node in nodes:
            node.configure(fg_color=self.theme.bg_tertiary)
    
    def _adjust_color_opacity(self, color: str, opacity: float) -> str:
        """Adjust color opacity by blending with background"""
        bg = self.theme.bg_color
        # Convert hex to RGB
        r1, g1, b1 = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        r2, g2, b2 = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
        
        # Blend based on opacity
        r = int(r1 * opacity + r2 * (1 - opacity))
        g = int(g1 * opacity + g2 * (1 - opacity))
        b = int(b1 * opacity + b2 * (1 - opacity))
        
        return f'#{r:02x}{g:02x}{b:02x}'