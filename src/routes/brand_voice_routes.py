from flask import Blueprint, request, jsonify
from models.brand_voice import BrandVoice
from main import db
import logging

brand_voice_bp = Blueprint('brand_voice_bp', __name__)

@brand_voice_bp.route("/brand-voices", methods=["GET"])
def get_brand_voices():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id query parameter is required"}), 400
    
    try:
        voices = BrandVoice.query.filter_by(user_id=int(user_id)).all()
        return jsonify({"brand_voices": [v.to_dict() for v in voices]})
    except Exception as e:
        logging.error(f"Error fetching brand voices for user_id {user_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch brand voices due to an internal error."}), 500

@brand_voice_bp.route("/brand-voices", methods=["POST"])
def create_brand_voice():
    data = request.get_json()
    if not data or 'name' not in data or 'description' not in data or 'user_id' not in data:
        return jsonify({"error": "Missing required fields: name, description, user_id"}), 400

    try:
        new_voice = BrandVoice(
            user_id=data['user_id'],
            name=data['name'],
            description=data['description']
        )
        db.session.add(new_voice)
        db.session.commit()
        logging.info(f"Created new brand voice '{data['name']}' for user_id {data['user_id']}.")
        return jsonify({"success": True, "brand_voice": new_voice.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating brand voice: {str(e)}")
        return jsonify({"error": "Failed to create brand voice."}), 500

@brand_voice_bp.route("/brand-voices/<int:voice_id>", methods=["DELETE"])
def delete_brand_voice(voice_id):
    try:
        voice = BrandVoice.query.get_or_404(voice_id)
        db.session.delete(voice)
        db.session.commit()
        logging.info(f"Deleted brand voice with id {voice_id}.")
        return jsonify({"success": True, "message": "Brand voice deleted."})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting brand voice {voice_id}: {str(e)}")
        return jsonify({"error": "Failed to delete brand voice."}), 500

# Placeholder for future AI content generation feature
@brand_voice_bp.route("/brand-voices/<int:voice_id>/generate", methods=["POST"])
def generate_content_from_voice(voice_id):
    # This is where the logic to call an AI service would go.
    # For now, it returns a placeholder.
    data = request.get_json()
    topic = data.get("topic", "a relevant topic")
    return jsonify({
        "message": "Content generation feature not yet implemented.",
        "generated_content": f"This is AI-generated content about {topic} based on brand voice {voice_id}."
    }), 501 # 501 Not Implemented
