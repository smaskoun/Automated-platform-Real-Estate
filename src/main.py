# src/main.py - NEW CORRECTED CODE

from flask import Flask
from flask_cors import CORS
import os

from models import db
from routes.user import user_bp

def create_app():
    """
    Creates and configures a Flask application instance.
    """
    app = Flask(__name__)

    # --- THIS IS THE CORRECTED LINE ---
    # Configure CORS to specifically allow requests from your live frontend URL.
    CORS(app, resources={r"/api/*": {"origins": "https://real-estate-frontend-lpug.onrender.com"}} )

    # Configure the database URI from an environment variable
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the app
    db.init_app(app)

    # Register the user blueprint
    app.register_blueprint(user_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app

# The entry point for Gunicorn on Render
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
