# src/main.py

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

# --- Import all blueprints from your route files ---
# This brings all your feature endpoints into the main application
from src.routes.user_routes import user_bp
from src.routes.brand_voice_routes import brand_voice_bp
from src.routes.social_media import social_media_bp
from src.routes.ab_testing_routes import ab_testing_bp
from src.routes.alternative_brand_voice_routes import alternative_brand_voice_bp
from src.routes.learning_algorithm_routes import learning_algorithm_bp
from src.routes.manual_content_routes import manual_content_bp
from src.routes.seo_routes import seo_bp

# Initialize the database instance
db = SQLAlchemy()

# This is the application factory function
def create_app():
    """
    Creates and configures an instance of the Flask application.
    """
    app = Flask(__name__)
    CORS(app)  # Enable Cross-Origin Resource Sharing

    # --- Database Configuration ---
    # Using the hardcoded string from your project. For production, this should be an environment variable.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@host/db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the app
    db.init_app(app)

    # --- Register All Blueprints ---
    # This is the crucial step that makes your endpoints live.
    # Each blueprint is given a URL prefix to organize the API.
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(brand_voice_bp, url_prefix='/brand-voices')
    app.register_blueprint(social_media_bp) # This blueprint likely has its own prefixes
    app.register_blueprint(ab_testing_bp, url_prefix='/ab-testing')
    app.register_blueprint(alternative_brand_voice_bp, url_prefix='/alt-brand-voices')
    app.register_blueprint(learning_algorithm_bp, url_prefix='/learning')
    app.register_blueprint(manual_content_bp, url_prefix='/manual-content')
    app.register_blueprint(seo_bp, url_prefix='/seo')

    # A simple root route to confirm the API is running
    @app.route('/')
    def index():
        return jsonify({"status": "API is running", "message": "Welcome to the Automated Real Estate Platform API!"}), 200

    return app

# Create the app instance that Gunicorn will use on Render
app = create_app()

# This block is for local development and won't be used by Gunicorn
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

