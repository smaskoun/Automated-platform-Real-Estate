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
