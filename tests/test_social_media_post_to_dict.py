import os
import sys
from datetime import datetime

import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Add src directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from main import create_app
from models import db
from models.social_media import SocialMediaAccount, SocialMediaPost


def setup_app():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        db.create_all()
        account = SocialMediaAccount(id=1, user_id=1, platform="twitter", account_name="acct")
        db.session.add(account)
        db.session.commit()
    return app


def test_social_media_post_to_dict_includes_scheduled_at():
    app = setup_app()
    with app.app_context():
        scheduled = datetime(2024, 1, 1, 12, 0)
        post = SocialMediaPost(
            account_id=1,
            content="Hello",
            image_prompt="prompt",
            hashtags="[\"#test\"]",
            scheduled_at=scheduled,
        )
        db.session.add(post)
        db.session.commit()
        data = post.to_dict()
        assert data["scheduled_at"] == scheduled.isoformat()
