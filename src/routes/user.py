from flask import Blueprint, request, jsonify

# Corrected relative import from the 'models' package
from models import db, User

# Create a Blueprint for user-related routes
user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/users', methods=['POST'])
def create_user():
    """Creates a new user."""
    data = request.get_json()
    if not data or not 'username' in data or not 'email' in data:
        return jsonify({'error': 'Username and email are required fields'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': f"User with email {data['email']} already exists"}), 409

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': f"User with username {data['username']} already exists"}), 409

    new_user = User(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    
    user_data = {'id': new_user.id, 'username': new_user.username, 'email': new_user.email}
    return jsonify({'message': 'User created successfully', 'user': user_data}), 201

@user_bp.route('/users', methods=['GET'])
def get_users():
    """Retrieves all users."""
    users = User.query.all()
    users_list = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return jsonify(users_list), 200

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retrieves a single user by ID."""
    user = User.query.get_or_404(user_id)
    user_data = {'id': user.id, 'username': user.username, 'email': user.email}
    return jsonify(user_data), 200

@user_bp.route('/users/<int:user_id>', methods=['PUT', 'PATCH'])
def update_user(user_id):
    """Updates a user's information."""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Update fields if they are provided in the request
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    
    db.session.commit()
    
    return jsonify({'message': 'User updated successfully'}), 200

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deletes a user."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200
