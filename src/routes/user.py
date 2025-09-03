from flask import Blueprint, request, jsonify
from src.models.user import User
from src.main import db
import logging

user_bp = Blueprint("user_bp", __name__)

# Registration is disabled for our "Middle Ground" approach.
# The endpoint is commented out to prevent public access.
# @user_bp.route('/register', methods=['POST'])
# def register():
#     # ... logic would go here ...
#     pass

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    try:
        user = User.query.filter_by(email=data['email']).first()

        # IMPORTANT: This is a temporary plain-text password check.
        # In a real-world app, you would use bcrypt to check a hashed password.
        if not user or user.password != data['password']:
            return jsonify({"error": "Invalid credentials"}), 401

        logging.info(f"User {user.email} logged in successfully.")
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": user.to_dict()
        })
    except Exception as e:
        logging.error(f"Error during login for email {data.get('email')}: {str(e)}")
        return jsonify({"error": "An internal error occurred during login."}), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict())
    except Exception as e:
        logging.error(f"Error fetching profile for user_id {user_id}: {str(e)}")
        return jsonify({"error": "User not found or internal error."}), 404
