from dataclasses import dataclass

@dataclass
class UITheme:
    """Primary theme class with sophisticated color palette and styling options"""
    # Primary colors
    bg_color: str = '#0F0F12'
    accent_color: str = '#FF6B35'
    text_color: str = '#E0E0E0'
    
    # Secondary colors
    secondary_color: str = '#4A4E69'
    border_color: str = '#C06014'
    hover_color: str = '#FF8B55'
    
    # Background variations
    bg_secondary: str = '#1A1A1D'
    bg_tertiary: str = '#252529'
    
    # Text variations
    text_secondary: str = '#A0A0A0'
    text_disabled: str = '#666666'
    
    # Fonts
    font: tuple = ('JetBrains Mono', 14)
    font_bold: tuple = ('JetBrains Mono Bold', 14)
    font_small: tuple = ('JetBrains Mono', 12)
    
    # UI elements
    input_bg: str = '#2A2A2D'
    button_bg: str = '#FF6B35'
    button_hover: str = '#FF8B55'
    error_color: str = '#FF4444'
    success_color: str = '#44FF44'
    
    @property
    def font_header(self) -> tuple:
        """Header font with larger size"""
        return (self.font[0], self.font[1] + 4)
    
    @property
    def font_title(self) -> tuple:
        """Title font with larger size"""
        return (self.font[0], self.font[1] + 2)
    
    @property
    def accent_hover(self) -> str:
        """Hover color for accent elements"""
        return self.hover_color 