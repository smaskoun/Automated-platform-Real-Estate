"""Database initialisation and model exports for the application."""

from flask_sqlalchemy import SQLAlchemy

# The single SQLAlchemy instance used across the application

db = SQLAlchemy()

# Import models so that metadata is populated when the module loads.
from .user import User  # noqa: E402,F401
from .brand_voice import BrandVoice  # noqa: E402,F401
from .brand_voice_example import BrandVoiceExample  # noqa: E402,F401
from .social_media import (  # noqa: E402,F401
    SocialMediaAccount,
    SocialMediaPost,
    AIImageGeneration,
    PostingSchedule,
)
from .ab_test_model import ABTest, ABTestVariation  # noqa: E402,F401

__all__ = [
    "db",
    "User",
    "BrandVoice",
    "BrandVoiceExample",
    "SocialMediaAccount",
    "SocialMediaPost",
    "AIImageGeneration",
    "PostingSchedule",
    "ABTest",
    "ABTestVariation",
]
