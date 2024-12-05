import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import io
import base64
import importlib
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ImageService:
    def __init__(self, 
                 default_image_size: tuple[int, int] = (512, 512),
                 num_inference_steps: int = 20,
                 guidance_scale: float = 7.0):
        """Initialize the image service with configurable parameters.
        
        Args:
            default_image_size: Tuple of (width, height) for generated images
            num_inference_steps: Number of denoising steps for generation
            guidance_scale: How closely to follow the prompt
        """
        self.model_id = "runwayml/stable-diffusion-v1-5"
        self.pipe = None
        self.default_image_size = default_image_size
        self.num_inference_steps = num_inference_steps
        self.guidance_scale = guidance_scale
        self._cached_image = None
        self._has_accelerate = self._check_accelerate()
        
    def _check_accelerate(self) -> bool:
        """Check if accelerate is available."""
        try:
            importlib.import_module('accelerate')
            return True
        except ImportError:
            logger.warning(
                "Accelerate not found. Installing accelerate is recommended for "
                "better performance. Install with: pip install accelerate"
            )
            return False
        
    def _load_model(self):
        """Lazy load the model optimized for CPU."""
        if self.pipe is None:
            try:
                load_params = {
                    "pretrained_model_name_or_path": self.model_id,
                    "torch_dtype": torch.float32,
                    "use_auth_token": False,
                    "safety_checker": None,
                }
                
                # Add accelerate parameters if available
                if self._has_accelerate:
                    load_params.update({
                        "low_cpu_mem_usage": True,
                    })
                
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    **load_params
                ).to("cpu")
                
                # Enable memory efficient settings for CPU
                self.pipe.enable_attention_slicing(slice_size=1)
                self.pipe.enable_vae_slicing()
                if self._has_accelerate:
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
            
            with torch.inference_mode():
                image = self.pipe(
                    prompt,
                    height=self.default_image_size[1],
                    width=self.default_image_size[0],
                    num_inference_steps=self.num_inference_steps,
                    guidance_scale=self.guidance_scale,
                ).images[0]
            
            buffered = io.BytesIO()
            image.save(buffered, format="PNG", optimize=True, quality=85)
            self._cached_image = base64.b64encode(buffered.getvalue()).decode()
            return self._cached_image
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None 