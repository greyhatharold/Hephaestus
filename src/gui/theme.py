from src.core.domain_types import DomainType
from dataclasses import dataclass

@dataclass
class UITheme:
    """Enhanced theme class with more sophisticated color palette and styling options"""
    # Primary colors
    bg_color: str
    accent_color: str
    text_color: str
    
    # Secondary colors
    secondary_color: str
    border_color: str
    hover_color: str
    
    # Background variations
    bg_secondary: str  # Slightly lighter than bg for layering
    bg_tertiary: str  # Even lighter for hover states
    
    # Text variations
    text_secondary: str  # Slightly dimmed text
    text_disabled: str  # Disabled text color
    
    # Fonts
    font: tuple  # Main font family and size
    font_bold: tuple  # Bold variant
    font_small: tuple  # Smaller size variant
    
    # Specific UI elements
    input_bg: str
    button_bg: str
    button_hover: str
    error_color: str
    success_color: str
    
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
        """Hover color for accent elements, derived from accent_color"""
        return self.hover_color  # Use existing hover_color for consistency

class DomainThemes:
    @staticmethod
    def get_theme(domain: DomainType) -> UITheme:
        themes = {
            DomainType.TECHNOLOGY: UITheme(
                # Primary colors - Cyberpunk-inspired theme
                bg_color='#0F0F12',
                accent_color='#FF6B35',
                text_color='#E0E0E0',
                
                # Secondary colors
                secondary_color='#4A4E69',
                border_color='#C06014',
                hover_color='#FF8B55',
                
                # Background variations
                bg_secondary='#1A1A1D',
                bg_tertiary='#252529',
                
                # Text variations
                text_secondary='#A0A0A0',
                text_disabled='#666666',
                
                # Fonts
                font=('JetBrains Mono', 14),
                font_bold=('JetBrains Mono Bold', 14),
                font_small=('JetBrains Mono', 12),
                
                # UI elements
                input_bg='#2A2A2D',
                button_bg='#FF6B35',
                button_hover='#FF8B55',
                error_color='#FF4444',
                success_color='#44FF44'
            ),
            
            DomainType.BUSINESS: UITheme(
                # Primary colors - Professional dark theme
                bg_color='#0A192F',
                accent_color='#64FFDA',
                text_color='#E6F1FF',
                
                # Secondary colors
                secondary_color='#112240',
                border_color='#233554',
                hover_color='#84FFEA',
                
                # Background variations
                bg_secondary='#112240',
                bg_tertiary='#1D3461',
                
                # Text variations
                text_secondary='#8892B0',
                text_disabled='#546A8F',
                
                # Fonts
                font=('Inter', 14),
                font_bold=('Inter Bold', 14),
                font_small=('Inter', 12),
                
                # UI elements
                input_bg='#233554',
                button_bg='#64FFDA',
                button_hover='#84FFEA',
                error_color='#FF5D5D',
                success_color='#64FFDA'
            ),
            
            DomainType.HARD_SCIENCE: UITheme(
                # Primary colors - Scientific precision theme
                bg_color='#1A1D21',
                accent_color='#00B4D8',
                text_color='#ECF0F1',
                
                # Secondary colors
                secondary_color='#2D3436',
                border_color='#0077B6',
                hover_color='#48CAE4',
                
                # Background variations
                bg_secondary='#2C3E50',
                bg_tertiary='#34495E',
                
                # Text variations
                text_secondary='#B2BEC3',
                text_disabled='#636E72',
                
                # Fonts
                font=('Space Mono', 14),
                font_bold=('Space Mono Bold', 14),
                font_small=('Space Mono', 12),
                
                # UI elements
                input_bg='#2D3436',
                button_bg='#00B4D8',
                button_hover='#48CAE4',
                error_color='#E74C3C',
                success_color='#00B4D8'
            ),
            
            DomainType.ARTS: UITheme(
                # Primary colors - Creative dark theme
                bg_color='#2D1B36',
                accent_color='#E84A5F',
                text_color='#FFFFFF',
                
                # Secondary colors
                secondary_color='#453545',
                border_color='#FF847C',
                hover_color='#FF847C',
                
                # Background variations
                bg_secondary='#382742',
                bg_tertiary='#453545',
                
                # Text variations
                text_secondary='#FECEAB',
                text_disabled='#8B728B',
                
                # Fonts
                font=('Playfair Display', 14),
                font_bold=('Playfair Display Bold', 14),
                font_small=('Playfair Display', 12),
                
                # UI elements
                input_bg='#453545',
                button_bg='#E84A5F',
                button_hover='#FF847C',
                error_color='#FF4D6D',
                success_color='#99E1D9'
            )
        }
        
        # Default to technology theme if domain not found
        return themes.get(domain, themes[DomainType.TECHNOLOGY]) 