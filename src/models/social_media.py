# src/models/social_media.py - CORRECTED VERSION

from . import db  # CORRECTED: Import the shared 'db' object
from datetime import datetime
import json

# REMOVED: The extra 'db = SQLAlchemy()' line is gone.

class SocialMediaAccount(db.Model):
    __tablename__ = 'social_media_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    account_id = db.Column(db.String(100), nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text)
    token_expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    posts = db.relationship('SocialMediaPost', backref='account', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'account_id': self.account_id,
            'account_name': self.account_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SocialMediaPost(db.Model):
    __tablename__ = 'social_media_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('social_media_accounts.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    image_prompt = db.Column(db.Text)
    hashtags = db.Column(db.Text)
    status = db.Column(db.String(50), default='draft')
    scheduled_at = db.Column(db.DateTime)
    posted_at = db.Column(db.DateTime)
    platform_post_id = db.Column(db.String(100))
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'content': self.content,
            'image_url': self.image_url,
            'image_prompt': self.image_prompt,
            'hashtags': json.loads(self.hashtags) if self.hashtags else [],
            'status': self.status,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'platform_post_id': self.platform_post_id,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AIImageGeneration(db.Model):
    __tablename__ = 'ai_image_generations'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    model_used = db.Column(db.String(100))
    generation_time = db.Column(db.Float)
    status = db.Column(db.String(50), default='pending')
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'prompt': self.prompt,
            'image_url': self.image_url,
            'model_used': self.model_used,
            'generation_time': self.generation_time,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PostingSchedule(db.Model):
    __tablename__ = 'posting_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    schedule_config = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'schedule_config': json.loads(self.schedule_config) if self.schedule_config else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
