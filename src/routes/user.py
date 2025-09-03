from flask import Blueprint, request, jsonify
from models.user import User
from main import db

user_bp = Blueprint('user_bp', __name__)

# Note: Registration is disabled for our "Middle Ground" approach
# @user_bp.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     # ... registration logic ...

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or user.password != data['password']:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": user.to_dict()
    })

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())
