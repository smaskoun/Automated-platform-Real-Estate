import os
import sys
from unittest.mock import patch

import pytest
from flask_migrate import Migrate, upgrade


os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("OPENAI_API_KEY", "test-key")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main import create_app
from src.models import db
import src.routes.social_media as social_media_routes
from src.models.brand_voice import BrandVoice
from src.models.brand_voice_example import BrandVoiceExample


def setup_app():
    app = create_app()
    app.config.update(TESTING=True)
    Migrate(app, db)
    with app.app_context():
        upgrade()
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
        "src.routes.social_media.learning_algorithm_service.get_content_recommendations",
        return_value={"error": "Insufficient data"},
    ), patch(
        "src.routes.social_media.ai_content_service.generate_optimized_post",
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


def test_generate_post_combines_all_examples():
    app = setup_app()
    client = app.test_client()

    with app.app_context():
        db.session.add_all(
            [
                BrandVoiceExample(
                    brand_voice_id=1,
                    content="Secondary sample one",
                ),
                BrandVoiceExample(
                    brand_voice_id=1,
                    content="Secondary sample two",
                ),
            ]
        )
        db.session.commit()

    mock_response = {
        "content": "Generated",
        "hashtags": ["#one"],
        "image_prompt": "img",
    }

    with patch(
        "src.routes.social_media.learning_algorithm_service.get_content_recommendations",
        return_value={},
    ), patch(
        "src.routes.social_media.ai_content_service.generate_optimized_post",
        return_value=mock_response,
    ) as mock_generate:
        response = client.post(
            "/api/social-media/posts/generate",
            json={"user_id": 1, "topic": "hi", "brand_voice_id": 1},
        )

    assert response.status_code == 200
    called_kwargs = mock_generate.call_args.kwargs
    assert called_kwargs["brand_voice_example"] == (
        "Example\n\nSecondary sample one\n\nSecondary sample two"
    )


def test_generate_post_uses_primary_when_no_extras():
    app = setup_app()
    client = app.test_client()

    mock_response = {
        "content": "Generated",
        "hashtags": ["#one"],
        "image_prompt": "img",
    }

    with patch(
        "src.routes.social_media.learning_algorithm_service.get_content_recommendations",
        return_value={},
    ), patch(
        "src.routes.social_media.ai_content_service.generate_optimized_post",
        return_value=mock_response,
    ) as mock_generate:
        response = client.post(
            "/api/social-media/posts/generate",
            json={"user_id": 1, "topic": "hi", "brand_voice_id": 1},
        )

    assert response.status_code == 200
    called_kwargs = mock_generate.call_args.kwargs
    assert called_kwargs["brand_voice_example"] == "Example"


def test_generate_post_truncates_long_example_block(monkeypatch):
    app = setup_app()
    client = app.test_client()

    with app.app_context():
        db.session.add(
            BrandVoiceExample(
                brand_voice_id=1,
                content="A" * 120,
            )
        )
        db.session.commit()

    monkeypatch.setattr(social_media_routes, "BRAND_VOICE_EXAMPLES_MAX_CHARS", 50)

    mock_response = {
        "content": "Generated",
        "hashtags": ["#one"],
        "image_prompt": "img",
    }

    with patch(
        "src.routes.social_media.learning_algorithm_service.get_content_recommendations",
        return_value={},
    ), patch(
        "src.routes.social_media.ai_content_service.generate_optimized_post",
        return_value=mock_response,
    ) as mock_generate:
        response = client.post(
            "/api/social-media/posts/generate",
            json={"user_id": 1, "topic": "hi", "brand_voice_id": 1},
        )

    assert response.status_code == 200
    combined_examples = mock_generate.call_args.kwargs["brand_voice_example"]
    assert combined_examples.startswith("Example\n\n")
    assert len(combined_examples) <= 50
    assert combined_examples.endswith("A" * (50 - len("Example\n\n")))
