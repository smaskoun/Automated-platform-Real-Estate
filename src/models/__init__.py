# src/models/__init__.py - FINAL AND COMPLETE VERSION

from flask_sqlalchemy import SQLAlchemy

# Initialize the db object
db = SQLAlchemy()

# Import all your models here to make them accessible to the rest of the app
from .user import User
from .brand_voice import BrandVoice
from .brand_voice_example import BrandVoiceExample
from .social_media import SocialMediaAccount, SocialMediaPost, AIImageGeneration, PostingSchedule
