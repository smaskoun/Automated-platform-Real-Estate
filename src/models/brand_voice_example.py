from . import db
from datetime import datetime

class BrandVoiceExample(db.Model):
    __tablename__ = 'brand_voice_examples'

    id = db.Column(db.Integer, primary_key=True)
    brand_voice_id = db.Column(db.Integer, db.ForeignKey('brand_voices.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'brand_voice_id': self.brand_voice_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
