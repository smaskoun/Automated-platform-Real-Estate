from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # CORRECTED IMPORTS: Relative to the 'src' directory
    from routes.user import user_bp
    from routes.brand_voice_routes import brand_voice_bp
    # ... (and so on for all other route imports) ...
    # from routes.social_media import social_media_bp 
    # from routes.seo_routes import seo_bp
    # etc.

    app.register_blueprint(user_bp)
    app.register_blueprint(brand_voice_bp)
    # ... (and so on for all other blueprint registrations) ...

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
