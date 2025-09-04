# src/main.py - NEW AND COMPLETE VERSION

import os
from flask import Flask
from flask_cors import CORS

# Import the database object from the models package
from models import db

# Import all of your blueprints from the routes package
from routes.user import user_bp
from routes.brand_voice_routes import brand_voice_bp
from routes.alternative_brand_voice_routes import alternative_brand_voice_bp
from routes.social_media import social_media_bp
from routes.seo_routes import seo_bp
from routes.ab_testing_routes import ab_testing_bp
# If you have other route files, import their blueprints here as well

def create_app():
    """
    Creates and configures the complete Flask application.
    """
    app = Flask(__name__)

    # Configure CORS to allow requests ONLY from your live frontend URL
    CORS(app, resources={r"/api/*": {"origins": "https://real-estate-frontend-lpug.onrender.com"}} )

    # Get the database URL from Render's environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the application
    db.init_app(app)

    # Register all the blueprints with a common /api prefix for organization
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(brand_voice_bp, url_prefix='/api/brand-voices')
    app.register_blueprint(alternative_brand_voice_bp, url_prefix='/api/alternatives')
    app.register_blueprint(social_media_bp, url_prefix='/api/social-media')
    app.register_blueprint(seo_bp, url_prefix='/api/seo')
    app.register_blueprint(ab_testing_bp, url_prefix='/api/ab-testing')

    with app.app_context():
        # This will create all necessary tables for all your models
        # (Make sure you have imported all your models in your models/__init__.py)
        db.create_all()

    return app

# This is the entry point for the Gunicorn server on Render
app = create_app()

if __name__ == '__main__':
    # This block is for local development only
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
