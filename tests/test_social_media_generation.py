import os
import sys
from unittest.mock import patch

import pytest


os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("OPENAI_API_KEY", "test-key")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from main import create_app
from models import db
from models.brand_voice import BrandVoice


def setup_app():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        db.create_all()
        bv = BrandVoice(id=1, user_id=1, name="Test", description="", post_example="Example")
        db.session.add(bv)
        db.session.commit()
    return app


def test_generate_post_fallback_on_insufficient_insights():
    app = setup_app()
    client = app.test_client()

    mock_content = {
        "content": "Generated text",
        "hashtags": ["#one"],
        "image_prompt": "img",
    }

    with patch(
        "routes.social_media.learning_algorithm_service.get_content_recommendations",
        return_value={"error": "Insufficient data"},
    ), patch(
        "routes.social_media.ai_content_service.generate_optimized_post",
        return_value=mock_content,
    ):
        response = client.post(
            "/api/social-media/posts/generate",
            json={"user_id": 1, "topic": "hi", "brand_voice_id": 1},
        )

    assert response.status_code == 200
    data = response.get_json()
    assert data["content"] == "Generated text"
    assert data["insights_used"] is False
