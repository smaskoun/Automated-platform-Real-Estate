import os
import sys

import pytest
from flask_migrate import Migrate, upgrade

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("OPENAI_API_KEY", "test-key")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main import create_app
from src.models import db


def setup_app():
    app = create_app()
    app.config.update(TESTING=True)
    Migrate(app, db)
    with app.app_context():
        upgrade()
    return app


def test_get_posts_rejects_invalid_user_id():
    app = setup_app()
    client = app.test_client()
    response = client.get("/api/social-media/posts", query_string={"user_id": "abc"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "user_id must be an integer"


def test_get_accounts_rejects_invalid_user_id():
    app = setup_app()
    client = app.test_client()
    response = client.get("/api/social-media/social-accounts", query_string={"user_id": "xyz"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "user_id must be an integer"


def test_create_account_rejects_invalid_user_id():
    app = setup_app()
    client = app.test_client()
    response = client.post(
        "/api/social-media/social-accounts",
        json={"user_id": "abc", "account_name": "acct", "platform": "twitter"},
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "user_id must be an integer"
