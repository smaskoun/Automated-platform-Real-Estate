# src/models/social_media.py - FULL REPLACEMENT (Corrected and Simplified)

from . import db
from datetime import datetime
import json

class SocialMediaAccount(db.Model):
    __tablename__ = 'social_media_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    # --- THIS IS THE CORRECTED LINE ---
    user_id = db.Column(db.Integer, nullable=False)
    
    # Simplified fields for internal management
    platform = db.Column(db.String(50), nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    posts = db.relationship('SocialMediaPost', backref='account', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'platform': self.platform,
            'account_name': self.account_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SocialMediaPost(db.Model):
    __tablename__ = 'social_media_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('social_media_accounts.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_prompt = db.Column(db.Text)
    hashtags = db.Column(db.Text) # Stored as a JSON string
    scheduled_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default='draft')
    scheduled_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

 codex/add-put-and-delete-routes-for-posts
    # Additional fields like image_url can be added in future as needed


    # Removed unused fields like image_url for simplicity
    
 main
    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'content': self.content,
            'image_prompt': self.image_prompt,
            'hashtags': json.loads(self.hashtags) if self.hashtags else [],
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'status': self.status,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# The other models (AIImageGeneration, PostingSchedule) are fine but are not currently used.
# They can be left as they are for future development.
class AIImageGeneration(db.Model):
    __tablename__ = 'ai_image_generations'
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    # ... other fields

class PostingSchedule(db.Model):
    __tablename__ = 'posting_schedules'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False) # Corrected this as well
    # ... other fields
