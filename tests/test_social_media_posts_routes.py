import os
import sys
import json
from datetime import datetime

import pytest
from flask_migrate import Migrate, upgrade

# Configure in-memory SQLite database for testing
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("OPENAI_API_KEY", "test-key")

# Ensure the src directory is on the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main import create_app
from src.models import db
from src.models.social_media import SocialMediaAccount, SocialMediaPost


def setup_app():
    """Create a Flask app configured for testing with an in-memory DB."""
    app = create_app()
    app.config.update(TESTING=True)
    Migrate(app, db)
    with app.app_context():
        upgrade()
    return app


def test_get_posts_returns_scheduled_at():
    app = setup_app()
    scheduled_time = datetime(2024, 1, 1, 12, 0)

    with app.app_context():
        account = SocialMediaAccount(user_id=1, platform="twitter", account_name="acct")
        db.session.add(account)
        db.session.commit()

        post = SocialMediaPost(
            account_id=account.id,
            content="Test post",
            hashtags=json.dumps(["#test"]),
            scheduled_at=scheduled_time,
        )
        db.session.add(post)
        db.session.commit()

    client = app.test_client()
    response = client.get("/api/social-media/posts", query_string={"user_id": 1})

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["posts"]) == 1
    assert data["posts"][0]["scheduled_at"] == scheduled_time.isoformat()


def test_create_post_rejects_foreign_account():
    app = setup_app()

    with app.app_context():
        user1_account = SocialMediaAccount(user_id=1, platform="twitter", account_name="acct1")
        user2_account = SocialMediaAccount(user_id=2, platform="twitter", account_name="acct2")
        db.session.add_all([user1_account, user2_account])
        db.session.commit()
        foreign_account_id = user2_account.id

    client = app.test_client()
    response = client.post(
        "/api/social-media/posts",
        json={"account_id": foreign_account_id, "content": "Hello", "user_id": 1},
    )

    assert response.status_code == 403
