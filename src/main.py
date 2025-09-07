# src/main.py - SPECIAL TEST VERSION

from flask import Flask
from flask_cors import CORS
from models import db
from config import Config
import logging
import os
import requests
from dotenv import load_dotenv

# Import all your blueprints
from routes.brand_voice_routes import brand_voice_bp
from routes.social_media import social_media_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    CORS(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(brand_voice_bp, url_prefix='/api/brand-voices')
    app.register_blueprint(social_media_bp, url_prefix='/api/social-media')
    logging.basicConfig(level=logging.INFO)
    @app.route('/')
    def index():
        return "Backend is running!"
    return app

app = create_app()

# --- SPECIAL META API TEST CODE ---
def run_meta_test():
    """
    A simple, safe test to check if a Meta access token is valid.
    """
    load_dotenv() # Ensure environment variables are loaded
    print("\n\n--- Starting Meta API Connection Test ---")
    user_access_token = os.getenv("META_USER_ACCESS_TOKEN")

    if not user_access_token:
        print("ERROR: META_USER_ACCESS_TOKEN is not set.")
        print("--- Test Finished ---")
        return

    print("Successfully found the access token.")
    url = f"https://graph.facebook.com/v18.0/me?fields=id,name&access_token={user_access_token}"
    print(f"Attempting to connect to URL: {url[:60]}..." )

    try:
        response = requests.get(url)
        response_data = response.json()
        if response.status_code == 200:
            print("\nSUCCESS! Connection to Meta API is working.")
            print("API Response:")
            print(response_data)
        else:
            print("\nERROR: Failed to connect to Meta API.")
            print(f"Status Code: {response.status_code}")
            print("API Error Response:")
            print(response_data)
    except Exception as e:
        print(f"\nCRITICAL ERROR: An exception occurred: {e}")
    print("--- Test Finished ---\n\n")

# This will run the test function when the script is executed directly
if __name__ == '__main__':
    run_meta_test()
    app.run(debug=True)
