import os
import sys
import json
from types import SimpleNamespace
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from services.ai_content_service import AIContentService


def test_generate_optimized_post_returns_fields():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        service = AIContentService()
        expected = {
            "content": "Test content",
            "hashtags": ["#tag1", "#tag2"],
            "image_prompt": "Image prompt"
        }
        mock_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(expected)))]
        )
        with patch("openai.chat.completions.create", return_value=mock_response) as mock_create:
            result = service.generate_optimized_post("topic", "voice", {})
        assert result == expected
        mock_create.assert_called_once()


def test_generate_optimized_post_handles_exception():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        service = AIContentService()
        with patch("openai.chat.completions.create", side_effect=Exception("OpenAI error")):
            result = service.generate_optimized_post("topic", "voice", {})
        assert result == {"error": "OpenAI error"}
