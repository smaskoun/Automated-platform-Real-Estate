# src/main.py - FULL REPLACEMENT (with DB Reset Logic)

from flask import Flask
from flask_cors import CORS
from models import db
from config import Config
import logging

# Import all your blueprints
from routes.brand_voice_routes import brand_voice_bp
from routes.social_media import social_media_bp
# Add other blueprint imports here if you have them

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # --- Database Reset and Creation Logic ---
    with app.app_context():
        # This will drop all existing tables and recreate them based on your models.
        # It's safe for development but be careful in production.
        print("Dropping all database tables...")
        db.drop_all()
        print("Creating all database tables...")
        db.create_all()
        print("Database tables created successfully.")

    # Register blueprints
    app.register_blueprint(brand_voice_bp, url_prefix='/api/brand-voices')
    app.register_blueprint(social_media_bp, url_prefix='/api/social-media')
    # Register other blueprints here

    # Basic logging setup
    logging.basicConfig(level=logging.INFO)

    @app.route('/')
    def index():
        return "Backend is running!"

    return app

# This part is for running the app with Gunicorn on Render
app = create_app()

if __name__ == '__main__':
    # This is for local development, not used by Render
    app.run(debug=True)
