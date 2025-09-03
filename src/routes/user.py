from flask import Blueprint, request, jsonify
from src.models.user import User, db
import logging

# It's good practice to have a hashing library for passwords.
# If you don't have flask_bcrypt, add it to your requirements.in:
# from flask_bcrypt import Bcrypt
# bcrypt = Bcrypt()

user_bp = Blueprint("user", __name__)


"""
--- Public User Registration (DISABLED) ---
The /register endpoint is intentionally disabled as this platform is for private use.
New users should be created manually by an administrator directly in the database.
This prevents unauthorized sign-ups.

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing email or password"}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400
    
    # In a real scenario, always hash passwords.
    # hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    new_user = User(
        username=data.get('username', data['email']),
        email=data['email'],
        password=data['password'] # IMPORTANT: Replace with hashed_password
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "success": True,
            "user": new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating user: {str(e)}")
        return jsonify({"error": "Failed to create user"}), 500
"""


@user_bp.route('/login', methods=['POST'])
def login():
    """Authenticates a user and returns their details upon success."""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=data['email']).first()

    # IMPORTANT: This is a placeholder for password checking.
    # In a real app, you must compare hashed passwords.
    # For example: if user and bcrypt.check_password_hash(user.password, data['password']):
    if user and user.password == data['password']:
        logging.info(f"User {user.email} logged in successfully.")
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": user.to_dict()
        })
    else:
        logging.warning(f"Failed login attempt for email: {data['email']}")
        return jsonify({"error": "Invalid credentials"}), 401


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Retrieves the profile for a specific user by their ID."""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify(user.to_dict())

