from flask import Flask
from flask_cors import CORS
from models import db
from config import Config
import logging

# Import all your blueprints
from routes.brand_voice_routes import brand_voice_bp
from routes.social_media import social_media_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    CORS(app)

    # This will create tables if they don't exist, but won't delete them.
    with app.app_context():
        db.create_all()

    app.register_blueprint(brand_voice_bp, url_prefix='/api/brand-voices')
    app.register_blueprint(social_media_bp, url_prefix='/api/social-media')
    
    logging.basicConfig(level=logging.INFO)
    
    @app.route('/')
    def index():
        return "Backend is running!"
        
    return app

# This is the entry point for Gunicorn on Render
app = create_app()

# This block is for local development and is not used by Gunicorn
if __name__ == '__main__':
    app.run(debug=True)

