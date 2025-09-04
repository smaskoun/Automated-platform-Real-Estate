# src/models/brand_voice.py

from . import db # Import the db object from the models package
from datetime import datetime

class BrandVoice(db.Model):
    __tablename__ = 'brand_voices'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # This establishes a relationship with the User model
    user = db.relationship('User', backref=db.backref('brand_voices', lazy=True))

    def to_dict(self):
        """Converts the brand voice object to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
