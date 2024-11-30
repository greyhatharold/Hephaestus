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
        self.pipe = None
        self.default_image_size = (512, 512)
        self._cached_image = None
        
    def _load_model(self):
        """Lazy load the model optimized for CPU."""
        if self.pipe is None:
            try:
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float32,
                    use_auth_token=False,
                    safety_checker=None,
                    # CPU optimizations
                    low_memory=True,
                ).to("cpu")
                
                # Enable memory efficient settings for CPU
                self.pipe.enable_attention_slicing(slice_size=1)
                self.pipe.enable_vae_slicing()
                self.pipe.enable_sequential_cpu_offload()
                
            except Exception as e:
                logger.error(f"Error loading model: {str(e)}")
                raise RuntimeError(f"Failed to load Stable Diffusion model: {str(e)}")
            
    def generate_image(self, prompt: str) -> str:
        """Generate image from prompt and return as base64 string."""
        if self._cached_image:
            return self._cached_image
            
        try:
            self._load_model()
            
            with torch.inference_mode():  # Faster than no_grad()
                image = self.pipe(
                    prompt,
                    height=self.default_image_size[1],
                    width=self.default_image_size[0],
                    num_inference_steps=20,  # Further reduced for CPU
                    guidance_scale=7.0,
                ).images[0]
            
            # Optimize image saving
            buffered = io.BytesIO()
            image.save(buffered, format="PNG", optimize=True, quality=85)
            self._cached_image = base64.b64encode(buffered.getvalue()).decode()
            return self._cached_image
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None 