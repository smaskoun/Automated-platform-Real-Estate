from flask import Flask
from flask_cors import CORS
from models import db
from config import Config
import logging
from flask_migrate import Migrate
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import text
import sys

# Import all your blueprints
from routes.brand_voice_routes import brand_voice_bp
from routes.alternative_brand_voice_routes import alternative_brand_voice_bp
from routes.social_media import social_media_bp
from routes.seo_routes import seo_bp
from routes.seo_tools_routes import seo_tools_bp
from routes.ab_testing_routes import ab_testing_bp


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

    def _check_tables():
        try:
            db.session.execute(text('SELECT 1 FROM brand_voices LIMIT 1'))
            db.session.execute(text('SELECT 1 FROM social_media_accounts LIMIT 1'))
            db.session.execute(text('SELECT 1 FROM social_media_posts LIMIT 1'))
        except ProgrammingError as e:
            logging.critical('Required database tables are missing: %s', e)
            sys.exit(1)

    if 'pytest' not in sys.modules:
        with app.app_context():
            _check_tables()
    
    @app.route('/')
    def index():
        return "Backend is running!"
        
    return app

# This is the entry point for Gunicorn on Render
app = create_app()

# This block is for local development and is not used by Gunicorn
if __name__ == '__main__':
    app.run(debug=True)

