# src/models/__init__.py

from flask_sqlalchemy import SQLAlchemy

# Initialize the db object
db = SQLAlchemy()

# Import the User model so it's accessible to the rest of the app
from .user import User 
