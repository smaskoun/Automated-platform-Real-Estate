from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# Initialize extensions
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # --- Database Configuration ---
    # Use the DATABASE_URL from Render's environment variables
    # Provide a default for local development if needed
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///default.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the app with the extensions
    db.init_app(app)

    # --- Import and Register Blueprints ---
    # Note: These are imported *inside* the function to avoid circular imports
    from src.routes.user import user_bp
    from src.routes.brand_voice_routes import brand_voice_bp
    from src.routes.social_media import social_media_bp
    from src.routes.seo_routes import seo_bp
    from src.routes.ab_testing_routes import ab_testing_bp
    from src.routes.learning_algorithm_routes import learning_algorithm_bp
    from src.routes.manual_content_routes import manual_content_bp
    from src.routes.alternative_brand_voice_routes import alternative_brand_voice_bp

    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(brand_voice_bp)
    app.register_blueprint(social_media_bp) # No prefix needed as routes are specific
    app.register_blueprint(seo_bp, url_prefix='/seo')
    app.register_blueprint(ab_testing_bp, url_prefix='/ab-testing')
    app.register_blueprint(learning_algorithm_bp, url_prefix='/learning')
    app.register_blueprint(manual_content_bp, url_prefix='/manual-content')
    app.register_blueprint(alternative_brand_voice_bp, url_prefix='/alt-brand-voices')

    # --- NEW SECTION TO CREATE DATABASE TABLES ---
    with app.app_context():
        print("Checking and creating database tables...")
        db.create_all()
        print("Database tables are ready.")
    # --- END OF NEW SECTION ---

    return app

# This part is for Gunicorn to find the app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
