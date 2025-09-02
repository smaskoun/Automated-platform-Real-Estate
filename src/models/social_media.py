from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class SocialMediaAccount(db.Model):
    __tablename__ = 'social_media_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)  # User identifier
    platform = db.Column(db.String(50), nullable=False)  # 'facebook' or 'instagram'
    account_id = db.Column(db.String(100), nullable=False)  # Platform account ID
    account_name = db.Column(db.String(200), nullable=False)  # Display name
    access_token = db.Column(db.Text, nullable=False)  # Encrypted access token
    refresh_token = db.Column(db.Text)  # Refresh token if available
    token_expires_at = db.Column(db.DateTime)  # Token expiration
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
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
    content = db.Column(db.Text, nullable=False)  # Post text content
    image_url = db.Column(db.String(500))  # Generated or uploaded image URL
    image_prompt = db.Column(db.Text)  # AI image generation prompt
    hashtags = db.Column(db.Text)  # JSON array of hashtags
    status = db.Column(db.String(50), default='draft')  # draft, approved, scheduled, posted, failed
    scheduled_at = db.Column(db.DateTime)  # When to post
    posted_at = db.Column(db.DateTime)  # When actually posted
    platform_post_id = db.Column(db.String(100))  # ID from social media platform
    error_message = db.Column(db.Text)  # Error details if posting failed
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
    prompt = db.Column(db.Text, nullable=False)  # Image generation prompt
    image_url = db.Column(db.String(500))  # Generated image URL
    model_used = db.Column(db.String(100))  # AI model used
    generation_time = db.Column(db.Float)  # Time taken to generate
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed
    error_message = db.Column(db.Text)  # Error details if generation failed
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
    name = db.Column(db.String(200), nullable=False)  # Schedule name
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    schedule_config = db.Column(db.Text)  # JSON configuration for schedule
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

