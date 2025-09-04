# src/models/__init__.py - FINAL CORRECTED VERSION

from flask_sqlalchemy import SQLAlchemy

# Initialize the db object
db = SQLAlchemy()

# Import all your models here to make them accessible to the rest of the app
from .user import User
from .brand_voice import BrandVoice
# If you have other model files (like social_media.py), import their classes here too.
# from .social_media import SocialMediaPost 
