# src/models/__init__.py

from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy object.
# This object will be imported by other parts of your application (like main.py and user.py)
db = SQLAlchemy()
