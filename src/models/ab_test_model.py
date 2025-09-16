# src/models/ab_test_model.py

from . import db
from datetime import datetime

class ABTest(db.Model):
    __tablename__ = 'ab_tests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    content_type = db.Column(db.String(100))
    platform = db.Column(db.String(50))
    status = db.Column(db.String(50), default='draft') # draft, running, completed
    winner_variation_id = db.Column(db.Integer)
    confidence_level = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    
    variations = db.relationship('ABTestVariation', backref='test', lazy=True, cascade='all, delete-orphan')

class ABTestVariation(db.Model):
    __tablename__ = 'ab_test_variations'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('ab_tests.id'), nullable=False)
    content = db.Column(db.Text)
    hashtags = db.Column(db.Text) # Stored as JSON string
    image_prompt = db.Column(db.Text)
    post_id = db.Column(db.String(100)) # ID of the post on the social media platform
    
    # Engagement data stored as JSON
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    saves = db.Column(db.Integer, default=0)
    reach = db.Column(db.Integer, default=0)
    impressions = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
