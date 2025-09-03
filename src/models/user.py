# Corrected relative import from the current package (__init__.py in the same folder)
from . import db

class User(db.Model):
    """
    User model for the database.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User id={self.id} username={self.username}>'
