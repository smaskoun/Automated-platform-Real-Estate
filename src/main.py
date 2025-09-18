import os

from flask import Flask, abort, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate, upgrade
import logging

from config import Config
from .models import db
from .routes.brand_voice_routes import brand_voice_bp
from .routes.alternative_brand_voice_routes import alternative_brand_voice_bp
from .routes.social_media import social_media_bp
from .routes.manual_content_routes import manual_content_bp
from .routes.learning_algorithm_routes import learning_algorithm_bp
from .routes.seo_routes import seo_bp
from .routes.seo_tools_routes import seo_tools_bp
from .routes.realtor_routes import realtor_bp
from .routes.user import user_bp


def _ensure_database_schema(app: Flask) -> None:
    """Run database migrations (or create tables) to guarantee the schema exists."""

    with app.app_context():
        try:
            upgrade()
            app.logger.info("Database schema is up to date.")
        except Exception as exc:  # pragma: no cover - defensive logging for production
            app.logger.warning("Automatic database migration failed: %s", exc)
            try:
                db.create_all()
                app.logger.info("Database tables ensured with create_all().")
            except Exception:
                app.logger.exception("Failed to ensure database schema.")
                raise


def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='')
    app.config.from_object(Config)
    db.init_app(app)
    Migrate(app, db)
    CORS(app)

    app.register_blueprint(brand_voice_bp, url_prefix='/api/brand-voices')
    app.register_blueprint(alternative_brand_voice_bp, url_prefix='/api/alt-brand-voice')
    app.register_blueprint(social_media_bp, url_prefix='/api/social-media')
    app.register_blueprint(manual_content_bp, url_prefix='/api/manual-content')
    app.register_blueprint(learning_algorithm_bp, url_prefix='/api/learning-algorithm')
    app.register_blueprint(seo_bp, url_prefix='/api/seo')
    app.register_blueprint(seo_tools_bp, url_prefix='/api/seo-tools')
    app.register_blueprint(realtor_bp, url_prefix='/api/realtor')
    app.register_blueprint(user_bp, url_prefix='/api')

    logging.basicConfig(level=logging.INFO)

    _ensure_database_schema(app)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def index(path):
        if path.startswith('api/'):
            abort(404)

        static_dir = app.static_folder
        if path and static_dir:
            full_path = os.path.join(static_dir, path)
            if os.path.isfile(full_path):
                return send_from_directory(static_dir, path)

        return app.send_static_file('index.html')

    return app


# This is the entry point for Gunicorn on Render
app = create_app()

# This block is for local development and is not used by Gunicorn
if __name__ == '__main__':
    app.run(debug=True)
