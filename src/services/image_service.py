import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import io
import base64
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ImageService:
    def __init__(self):
        self.model_id = "runwayml/stable-diffusion-v1-5"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        self.default_image_size = (512, 512)  # Standard size for consistency
        
    def _load_model(self):
        """Lazy load the model only when needed."""
        if self.pipe is None:
            try:
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    use_auth_token=False,
                    safety_checker=None
                ).to(self.device)
                
                # Optimize for CPU if not using CUDA
                if self.device == "cpu":
                    self.pipe.enable_attention_slicing()
                    
            except Exception as e:
                logger.error(f"Error loading model: {str(e)}")
                raise RuntimeError(f"Failed to load Stable Diffusion model: {str(e)}")
            
    def generate_image(self, prompt: str) -> str:
        """Generate image from prompt and return as base64 string."""
        try:
            self._load_model()
            
            # Generate image with consistent size
            image = self.pipe(
                prompt,
                height=self.default_image_size[1],
                width=self.default_image_size[0]
            ).images[0]
            
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG", optimize=True, quality=90)
            return base64.b64encode(buffered.getvalue()).decode()
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None 