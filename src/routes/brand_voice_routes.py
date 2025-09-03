from flask import Blueprint, request, jsonify
from ..models.brand_voice import BrandVoice
from src.main import db
import logging

brand_voice_bp = Blueprint('brand_voice_bp', __name__)

# CORRECTED ROUTE: Now explicitly '/brand-voices'
@brand_voice_bp.route("/brand-voices", methods=["GET"])
def get_brand_voices():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        voices = BrandVoice.query.filter_by(user_id=user_id).all()
        return jsonify({"brand_voices": [v.to_dict() for v in voices]})
    except Exception as e:
        logging.error(f"Error fetching brand voices: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# CORRECTED ROUTE: Now explicitly '/brand-voices'
@brand_voice_bp.route("/brand-voices", methods=["POST"])
def create_brand_voice():
    data = request.get_json()
    if not data or 'name' not in data or 'description' not in data or 'user_id' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        new_voice = BrandVoice(
            user_id=data['user_id'],
            name=data['name'],
            description=data['description']
        )
        db.session.add(new_voice)
        db.session.commit()
        return jsonify({"success": True, "brand_voice": new_voice.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating brand voice: {str(e)}")
        return jsonify({"error": "Failed to create brand voice"}), 500

# CORRECTED ROUTE: Now explicitly '/brand-voices/<id>'
@brand_voice_bp.route("/brand-voices/<int:voice_id>", methods=["GET"])
def get_brand_voice(voice_id):
    voice = BrandVoice.query.get_or_404(voice_id)
    return jsonify(voice.to_dict())

# CORRECTED ROUTE: Now explicitly '/brand-voices/<id>'
@brand_voice_bp.route("/brand-voices/<int:voice_id>", methods=["PUT"])
def update_brand_voice(voice_id):
    voice = BrandVoice.query.get_or_404(voice_id)
    data = request.get_json()
    
    voice.name = data.get('name', voice.name)
    voice.description = data.get('description', voice.description)
    
    try:
        db.session.commit()
        return jsonify({"success": True, "brand_voice": voice.to_dict()})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating brand voice: {str(e)}")
        return jsonify({"error": "Failed to update brand voice"}), 500

# CORRECTED ROUTE: Now explicitly '/brand-voices/<id>'
@brand_voice_bp.route("/brand-voices/<int:voice_id>", methods=["DELETE"])
def delete_brand_voice(voice_id):
    voice = BrandVoice.query.get_or_404(voice_id)
    try:
        db.session.delete(voice)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting brand voice: {str(e)}")
        return jsonify({"error": "Failed to delete brand voice"}), 500

# This route can stay as it is, it's a sub-resource
@brand_voice_bp.route('/brand-voices/<int:voice_id>/generate', methods=['POST'])
def generate_content_from_voice(voice_id):
    # ... (Your existing generation logic here)
    return jsonify({"error": "Not implemented yet"}), 501
