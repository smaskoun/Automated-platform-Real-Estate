from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
import logging

from config import Config
from .models import db
from .routes.brand_voice_routes import brand_voice_bp
from .routes.alternative_brand_voice_routes import alternative_brand_voice_bp
from .routes.social_media import social_media_bp
from .routes.seo_routes import seo_bp
from .routes.seo_tools_routes import seo_tools_bp
from .routes.ab_testing_routes import ab_testing_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    Migrate(app, db)
    CORS(app)

    app.register_blueprint(brand_voice_bp, url_prefix='/api/brand-voices')
    app.register_blueprint(alternative_brand_voice_bp, url_prefix='/api/alt-brand-voice')
    app.register_blueprint(social_media_bp, url_prefix='/api/social-media')
    app.register_blueprint(seo_bp, url_prefix='/api/seo')
    app.register_blueprint(seo_tools_bp, url_prefix='/api/seo-tools')
    app.register_blueprint(ab_testing_bp, url_prefix='/api/ab-testing')
   
    
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
