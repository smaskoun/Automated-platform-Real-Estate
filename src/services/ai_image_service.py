 codex/fix-syntax-error-in-ab_testing_routes-tnow9p
"""Generate AI imagery for social posts without relying on third-party services."""

from __future__ import annotations

import base64
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from openai import OpenAI
from PIL import Image

LOGGER = logging.getLogger(__name__)
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "static" / "generated_images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class AIImageService:
    """Create social-media-friendly imagery using the OpenAI Images API."""

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        self._client: Optional[OpenAI] = OpenAI(api_key=api_key) if api_key else None
        self._placeholder_path = OUTPUT_DIR / "placeholder.png"
        if not self._placeholder_path.exists():
            self._create_placeholder_image()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_image(self, prompt: str, size: str = "1024x1024") -> Dict[str, Optional[str]]:
        """Generate an image for ``prompt`` or return a local placeholder."""

        if not prompt:
            raise ValueError("Prompt is required for image generation.")

        if not self._client:
            return self._placeholder_response("OpenAI API key is not configured.")

        try:
            response = self._client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size=size,
                response_format="b64_json",
            )
            b64_data = response.data[0].b64_json
            image_bytes = base64.b64decode(b64_data)
            file_name = self._save_image(image_bytes)
            return {
                "success": True,
                "image_url": f"/static/generated_images/{file_name}",
                "provider": "openai",
                "prompt": prompt,
                "size": size,
            }
        except Exception as exc:  # pragma: no cover - network errors are runtime only
            LOGGER.error("Failed to generate image via OpenAI: %s", exc)
            return self._placeholder_response(str(exc))

    def optimize_prompt_for_social_media(
        self,
        base_prompt: str,
        platform: str = "instagram",
        content_type: str = "post",
    ) -> str:
        """Apply light prompt engineering tuned for the real-estate domain."""

        if not base_prompt:
            return ""

        platform_styles = {
            "instagram": {
                "post": "high quality, vibrant, professional real estate photography",
                "story": "vertical composition, bold typography space, mobile friendly",
                "cover": "landscape orientation, clean branding area",
            },
            "facebook": {
                "post": "engaging, shareable marketing image, natural lighting",
                "story": "vertical composition, strong focal point",
                "cover": "1200x630 proportion, community focused scene",
            },
        }

        descriptors = platform_styles.get(platform, {}).get(content_type, "professional real estate photo")
        quality_tags = "high resolution, sharp focus, well lit"
        return f"{base_prompt}, {descriptors}, {quality_tags}"

    def generate_social_media_image(
        self,
        prompt: str,
        platform: str = "instagram",
        content_type: str = "post",
    ) -> Dict[str, Optional[str]]:
        """Optimise the prompt and request image generation in one step."""

        optimized_prompt = self.optimize_prompt_for_social_media(prompt, platform, content_type)
        size = self._platform_dimensions(platform, content_type)
        return self.generate_image(optimized_prompt or prompt, size=size)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _save_image(self, data: bytes) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"openai_{timestamp}.png"
        path = OUTPUT_DIR / filename
        with path.open("wb") as fh:
            fh.write(data)

        # Ensure the image can be opened; convert to RGB if needed
        try:
            with Image.open(path) as image:
                if image.mode != "RGB":
                    image.convert("RGB").save(path, format="PNG")
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.warning("Generated image validation failed: %s", exc)

        return filename

    def _create_placeholder_image(self) -> None:
        with Image.new("RGB", (512, 512), color=(230, 230, 230)) as image:
            image.save(self._placeholder_path, format="PNG")

    def _placeholder_response(self, reason: str) -> Dict[str, Optional[str]]:
        return {
            "success": False,
            "image_url": f"/static/generated_images/{self._placeholder_path.name}",
            "provider": "placeholder",
            "error": reason,
        }

    @staticmethod
    def _platform_dimensions(platform: str, content_type: str) -> str:
        if platform == "instagram":
            if content_type == "story":
                return "1080x1920"
            return "1080x1080"
        if platform == "facebook" and content_type == "cover":
            return "1200x630"
        return "1024x1024"


ai_image_service = AIImageService()

__all__ = ["ai_image_service", "AIImageService"]
=======
import requests
import os
import logging
import time
from datetime import datetime
import base64
import io
from PIL import Image
import json

class AIImageService:
    """Service for generating AI images using multiple providers"""
    
    def __init__(self):
        self.huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY', '')
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.stability_api_key = os.getenv('STABILITY_API_KEY', '')
        
        # Default models for each provider
        self.models = {
            'huggingface': {
                'stable-diffusion-v1-5': 'runwayml/stable-diffusion-v1-5',
                'stable-diffusion-xl': 'stabilityai/stable-diffusion-xl-base-1.0',
                'stable-diffusion-2-1': 'stabilityai/stable-diffusion-2-1'
            },
            'pollination': {
                'stable-diffusion': 'stable-diffusion'
            }
        }
        
        # Image generation parameters
        self.default_params = {
            'width': 1024,
            'height': 1024,
            'num_inference_steps': 20,
            'guidance_scale': 7.5,
            'negative_prompt': 'blurry, low quality, distorted, deformed, ugly, bad anatomy'
        }
    
    def generate_image(self, prompt, model='stable-diffusion-v1-5', provider='auto', **kwargs):
        """
        Generate an image using the specified provider and model
        
        Args:
            prompt (str): Text prompt for image generation
            model (str): Model to use for generation
            provider (str): Provider to use ('huggingface', 'pollination', 'auto')
            **kwargs: Additional parameters for image generation
        
        Returns:
            dict: Result containing image_url, success status, and metadata
        """
        
        # Merge default parameters with provided kwargs
        params = {**self.default_params, **kwargs}
        
        # Auto-select provider if not specified
        if provider == 'auto':
            provider = self._select_best_provider()
        
        try:
            if provider == 'huggingface':
                return self._generate_with_huggingface(prompt, model, params)
            elif provider == 'pollination':
                return self._generate_with_pollination(prompt, model, params)
            elif provider == 'openai':
                return self._generate_with_openai(prompt, params)
            else:
                # Fallback to free options
                return self._generate_with_fallback(prompt, model, params)
                
        except Exception as e:
            logging.error(f"Error generating image with {provider}: {str(e)}")
            
            # Try fallback provider
            if provider != 'pollination':
                try:
                    return self._generate_with_pollination(prompt, model, params)
                except:
                    pass
            
            return {
                'success': False,
                'error': str(e),
                'image_url': None,
                'provider': provider,
                'model': model
            }
    
    def _select_best_provider(self):
        """Select the best available provider based on API keys and availability"""
        
        # Check if Hugging Face API key is available
        if self.huggingface_api_key:
            return 'huggingface'
        
        # Fallback to free options
        return 'pollination'
    
    def _generate_with_huggingface(self, prompt, model, params):
        """Generate image using Hugging Face Inference API"""
        
        model_id = self.models['huggingface'].get(model, model)
        api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": params.get('num_inference_steps', 20),
                "guidance_scale": params.get('guidance_scale', 7.5),
                "negative_prompt": params.get('negative_prompt', ''),
                "width": params.get('width', 1024),
                "height": params.get('height', 1024)
            }
        }
        
        start_time = time.time()
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            # Save image
            image_filename = self._save_image(response.content, 'huggingface')
            
            return {
                'success': True,
                'image_url': f"/generated_images/{image_filename}",
                'provider': 'huggingface',
                'model': model_id,
                'generation_time': generation_time,
                'prompt': prompt,
                'parameters': params
            }
        else:
            error_msg = f"Hugging Face API error: {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error', response.text)}"
                except:
                    error_msg += f" - {response.text}"
            
            raise Exception(error_msg)
    
    def _generate_with_pollination(self, prompt, model, params):
        """Generate image using Pollination AI (free Stable Diffusion API)"""
        
        api_url = "https://image.pollinations.ai/prompt/"
        
        # Pollination uses URL parameters
        encoded_prompt = requests.utils.quote(prompt)
        
        # Build URL with parameters
        url_params = []
        if params.get('width'):
            url_params.append(f"width={params['width']}")
        if params.get('height'):
            url_params.append(f"height={params['height']}")
        
        # Add style parameters
        url_params.append("model=flux")  # Use Flux model for better quality
        url_params.append("enhance=true")  # Enable enhancement
        
        full_url = f"{api_url}{encoded_prompt}"
        if url_params:
            full_url += "?" + "&".join(url_params)
        
        start_time = time.time()
        response = requests.get(full_url, timeout=60)
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            # Save image
            image_filename = self._save_image(response.content, 'pollination')
            
            return {
                'success': True,
                'image_url': f"/generated_images/{image_filename}",
                'provider': 'pollination',
                'model': 'flux',
                'generation_time': generation_time,
                'prompt': prompt,
                'parameters': params
            }
        else:
            raise Exception(f"Pollination API error: {response.status_code} - {response.text}")
    
    def _generate_with_openai(self, prompt, params):
        """Generate image using OpenAI DALL-E (paid option)"""
        
        if not self.openai_api_key:
            raise Exception("OpenAI API key not available")
        
        api_url = "https://api.openai.com/v1/images/generations"
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        # Map size parameters to DALL-E format
        size = "1024x1024"
        if params.get('width') and params.get('height'):
            size = f"{params['width']}x{params['height']}"
        
        payload = {
            "prompt": prompt,
            "n": 1,
            "size": size,
            "quality": "standard",
            "response_format": "url"
        }
        
        start_time = time.time()
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            image_url = result['data'][0]['url']
            
            # Download and save the image locally
            image_response = requests.get(image_url)
            image_filename = self._save_image(image_response.content, 'openai')
            
            return {
                'success': True,
                'image_url': f"/generated_images/{image_filename}",
                'provider': 'openai',
                'model': 'dall-e-3',
                'generation_time': generation_time,
                'prompt': prompt,
                'parameters': params
            }
        else:
            error_data = response.json()
            raise Exception(f"OpenAI API error: {error_data.get('error', {}).get('message', 'Unknown error')}")
    
    def _generate_with_fallback(self, prompt, model, params):
        """Fallback method using free alternatives"""
        
        # Try Pollination first as it's most reliable free option
        try:
            return self._generate_with_pollination(prompt, model, params)
        except Exception as e:
            logging.error(f"Pollination fallback failed: {str(e)}")
            
            # Could add more free alternatives here
            raise Exception("All free image generation services are currently unavailable")
    
    def _save_image(self, image_data, provider):
        """Save image data to local storage and return filename"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"{provider}_{timestamp}.png"
        image_path = os.path.join('src', 'static', 'generated_images', image_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        # Save image
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
        # Verify image was saved correctly
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary and save as PNG
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    img.save(image_path, 'PNG')
        except Exception as e:
            logging.warning(f"Image verification failed: {str(e)}")
        
        return image_filename
    
    def optimize_prompt_for_social_media(self, base_prompt, platform='instagram', content_type='post'):
        """
        Optimize image generation prompt for social media use
        
        Args:
            base_prompt (str): Base prompt from user
            platform (str): Target platform ('instagram', 'facebook')
            content_type (str): Type of content ('post', 'story', 'cover')
        
        Returns:
            str: Optimized prompt
        """
        
        # Platform-specific optimizations
        platform_styles = {
            'instagram': {
                'post': 'high quality, professional photography, vibrant colors, Instagram-worthy, clean composition, good lighting',
                'story': 'vertical format, mobile-friendly, eye-catching, bold text overlay space, story format',
                'cover': 'professional headshot, clean background, business portrait style'
            },
            'facebook': {
                'post': 'engaging, shareable, professional quality, clear subject, good contrast',
                'story': 'vertical format, mobile-optimized, attention-grabbing',
                'cover': 'landscape format, professional, brand-appropriate, cover photo style'
            }
        }
        
        # Real estate specific enhancements
        real_estate_keywords = [
            'professional real estate photography',
            'architectural photography',
            'property showcase',
            'clean modern style',
            'high-end real estate marketing'
        ]
        
        # Build optimized prompt
        style_additions = platform_styles.get(platform, {}).get(content_type, '')
        
        optimized_prompt = f"{base_prompt}, {style_additions}"
        
        # Add real estate context if relevant
        if any(keyword in base_prompt.lower() for keyword in ['house', 'home', 'property', 'real estate', 'listing']):
            optimized_prompt += f", {', '.join(real_estate_keywords[:2])}"
        
        # Add quality enhancers
        quality_enhancers = [
            'professional photography',
            'high resolution',
            'sharp focus',
            'excellent lighting',
            'commercial quality'
        ]
        
        optimized_prompt += f", {', '.join(quality_enhancers[:3])}"
        
        return optimized_prompt
    
    def generate_social_media_image(self, prompt, platform='instagram', content_type='post', **kwargs):
        """
        Generate an image optimized for social media
        
        Args:
            prompt (str): Base image prompt
            platform (str): Target platform
            content_type (str): Type of content
            **kwargs: Additional generation parameters
        
        Returns:
            dict: Generation result with optimized image
        """
        
        # Optimize prompt for social media
        optimized_prompt = self.optimize_prompt_for_social_media(prompt, platform, content_type)
        
        # Set platform-appropriate dimensions
        if platform == 'instagram':
            if content_type == 'story':
                kwargs.update({'width': 1080, 'height': 1920})  # 9:16 ratio
            else:
                kwargs.update({'width': 1080, 'height': 1080})  # 1:1 ratio
        elif platform == 'facebook':
            if content_type == 'cover':
                kwargs.update({'width': 1200, 'height': 630})   # Cover photo ratio
            else:
                kwargs.update({'width': 1200, 'height': 1200})  # Square post
        
        # Generate image with optimized settings
        result = self.generate_image(optimized_prompt, **kwargs)
        
        if result['success']:
            result['original_prompt'] = prompt
            result['optimized_prompt'] = optimized_prompt
            result['platform'] = platform
            result['content_type'] = content_type
        
        return result

# Global instance
ai_image_service = AIImageService()

 main
