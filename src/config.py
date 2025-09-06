# src/config.py (NEW FILE)

import os
from dotenv import load_dotenv

# Load environment variables from the .env file in Render
load_dotenv()

class Config:
    """Set Flask configuration from environment variables."""

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for session management (good practice)
    SECRET_KEY = os.getenv("SECRET_KEY", "a_default_secret_key_for_development")

