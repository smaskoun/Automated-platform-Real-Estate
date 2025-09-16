"""Database models for social media accounts and generated posts."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict

from . import db


class SocialMediaAccount(db.Model):
    """A connected social media account owned by a user."""

    __tablename__ = "social_media_accounts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    posts = db.relationship(
        "SocialMediaPost",
        backref="account",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "platform": self.platform,
            "account_name": self.account_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SocialMediaPost(db.Model):
    """A social media post generated or scheduled through the platform."""

    __tablename__ = "social_media_posts"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("social_media_accounts.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_prompt = db.Column(db.Text)
    hashtags = db.Column(db.Text)  # Stored as a JSON array string
    scheduled_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), default="draft")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "account_id": self.account_id,
            "content": self.content,
            "image_prompt": self.image_prompt,
            "hashtags": json.loads(self.hashtags) if self.hashtags else [],
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AIImageGeneration(db.Model):
    """Record of images generated for social posts."""

    __tablename__ = "ai_image_generations"

    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PostingSchedule(db.Model):
    """Simple schedule of planned post times."""

    __tablename__ = "posting_schedules"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    platform = db.Column(db.String(50))
    scheduled_for = db.Column(db.DateTime)


__all__ = [
    "SocialMediaAccount",
    "SocialMediaPost",
    "AIImageGeneration",
    "PostingSchedule",
]
