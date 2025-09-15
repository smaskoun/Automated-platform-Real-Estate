# src/models/brand_voice.py - NEW VERSION

from . import db
from datetime import datetime

class BrandVoice(db.Model):
    __tablename__ = 'brand_voices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False) # Assuming user_id is an integer
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # NEW FIELD: To store the example post content
    post_example = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to example posts
    examples = db.relationship(
        'BrandVoiceExample', backref='brand_voice', lazy=True, cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'post_example': self.post_example, # Added to the output
            'created_at': self.created_at.isoformat()
        }
