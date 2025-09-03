from flask import Flask
from flask_cors import CORS
import os

# Corrected relative imports
from models import db
from routes.user import user_bp

def create_app():
    """
    Creates and configures a Flask application instance.
    """
    app = Flask(__name__)
    
    # Enable CORS for all routes to allow your frontend to connect
    CORS(app)

    # Configure the database URI from an environment variable for security
    # Render will provide this DATABASE_URL automatically for its Postgres service
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the app
    db.init_app(app)

    # Register the user blueprint. All routes in user.py will be prefixed with /api
    # e.g., /users becomes /api/users
    app.register_blueprint(user_bp, url_prefix='/api')

    with app.app_context():
        # This command creates the database tables based on your models
        # It's safe to run on every startup; it won't recreate existing tables
        db.create_all()

    return app

# The entry point for Gunicorn on Render
app = create_app()

# This block is for running the app locally for testing (e.g., python src/main.py)
# It will not be used by Gunicorn in production
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
