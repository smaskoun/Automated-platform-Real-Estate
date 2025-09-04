# src/main.py - FINAL CORRECTED VERSION

import os
from flask import Flask
from flask_cors import CORS

from models import db
from routes.user import user_bp
from routes.brand_voice_routes import brand_voice_bp
from routes.alternative_brand_voice_routes import alternative_brand_voice_bp
from routes.social_media import social_media_bp
from routes.seo_routes import seo_bp
from routes.ab_testing_routes import ab_testing_bp

def create_app():
    app = Flask(__name__)

    # --- THIS IS THE CORRECTED LINE ---
    # We now explicitly allow all common HTTP methods.
    CORS(
        app, 
        resources={r"/api/*": {"origins": "https://real-estate-frontend-lpug.onrender.com"}},
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        supports_credentials=True
     )

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(brand_voice_bp, url_prefix='/api/brand-voices')
    app.register_blueprint(alternative_brand_voice_bp, url_prefix='/api/alternatives')
    app.register_blueprint(social_media_bp, url_prefix='/api/social-media')
    app.register_blueprint(seo_bp, url_prefix='/api/seo')
    app.register_blueprint(ab_testing_bp, url_prefix='/api/ab-testing')

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
