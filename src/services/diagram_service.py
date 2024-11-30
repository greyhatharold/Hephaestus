from graphviz import Digraph
import tempfile
import base64
from pathlib import Path
from typing import Tuple, Optional
from functools import lru_cache
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DiagramService:
    DIAGRAM_ATTRS = {
        'graph': {'rankdir': 'TB'},
        'node': {
            'shape': 'box',
            'style': 'rounded,filled',
            'fillcolor': 'lightblue'
        },
        'edge': {'color': '#666666'}
    }

    @staticmethod
    @lru_cache(maxsize=100)  # Cache recent diagram generations
    def generate_diagram(idea: str, gpt_response: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generates a diagram from GPT response and returns base64 encoded image.
        
        Args:
            idea: The original idea text
            gpt_response: Response containing node connections
            
        Returns:
            Tuple of (base64_encoded_image, gpt_response) or (None, None) on error
        """
        try:
            dot = DiagramService._create_digraph()
            DiagramService._add_connections(dot, gpt_response)
            img_data = DiagramService._render_diagram(dot)
            
            return img_data, gpt_response
            
        except Exception as e:
            logger.error(f"Error generating diagram: {str(e)}", exc_info=True)
            return None, None

    @classmethod
    def _create_digraph(cls) -> Digraph:
        """Creates and configures a new Digraph instance."""
        dot = Digraph(comment='Implementation Plan')
        
        # Apply stored attributes
        for attr_type, attrs in cls.DIAGRAM_ATTRS.items():
            if attr_type == 'graph':
                dot.attr(**attrs)
            else:
                dot.attr(attr_type, **attrs)
                
        return dot

    @staticmethod
    def _add_connections(dot: Digraph, gpt_response: str) -> None:
        """Parses and adds connections to the diagram."""
        if not gpt_response:
            raise ValueError("Empty GPT response")

        connections = [conn.strip() for conn in gpt_response.split('\n') if conn.strip()]
        
        for conn in connections:
            if '->' not in conn:
                continue
                
            try:
                source, target = map(str.strip, conn.split('->'))
                dot.edge(source, target)
            except ValueError as e:
                logger.warning(f"Invalid connection format: {conn}")
                continue

    @staticmethod
    def _render_diagram(dot: Digraph) -> str:
        """Renders the diagram and returns base64 encoded image data."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            try:
                # Render to temporary file
                dot.render(tmp.name, format='png', cleanup=True)
                png_path = Path(f"{tmp.name}.png")
                
                # Read and encode image
                img_data = base64.b64encode(png_path.read_bytes()).decode()
                
                return img_data
                
            finally:
                # Cleanup temporary files
                try:
                    Path(tmp.name).unlink(missing_ok=True)
                    png_path = Path(f"{tmp.name}.png")
                    if png_path.exists():
                        png_path.unlink()
                except Exception as e:
                    logger.warning(f"Error cleaning up temporary files: {e}")