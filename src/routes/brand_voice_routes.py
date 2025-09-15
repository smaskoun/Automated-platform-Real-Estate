# src/routes/brand_voice_routes.py - NEW VERSION

from flask import Blueprint, request, jsonify
from ..models import db
from ..models.brand_voice import BrandVoice
from ..models.brand_voice_example import BrandVoiceExample
import logging

brand_voice_bp = Blueprint('brand_voice_bp', __name__)

@brand_voice_bp.route("/", methods=["GET"])
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

@brand_voice_bp.route("/", methods=["POST"])
def create_brand_voice():
    data = request.get_json()
    # UPDATED: Added 'post_example' to the required fields
    required_fields = ['name', 'description', 'user_id', 'post_example']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields: name, description, user_id, post_example"}), 400

    try:
        new_voice = BrandVoice(
            user_id=data['user_id'],
            name=data['name'],
            description=data['description'],
            post_example=data['post_example'] # Added new field
        )
        db.session.add(new_voice)
        db.session.commit()
        logging.info(f"Created new brand voice '{data['name']}' for user_id {data['user_id']}.")
        return jsonify({"success": True, "brand_voice": new_voice.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating brand voice: {str(e)}")
        return jsonify({"error": "Failed to create brand voice."}), 500

@brand_voice_bp.route("/<int:voice_id>", methods=["DELETE"])
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

@brand_voice_bp.route("/<int:voice_id>/generate", methods=["POST"])
def generate_content_from_voice(voice_id):
    data = request.get_json()
    topic = data.get("topic", "a relevant topic")
    return jsonify({
        "message": "Content generation feature not yet implemented.",
        "generated_content": f"This is AI-generated content about {topic} based on brand voice {voice_id}."
    }), 501

@brand_voice_bp.route("/<int:voice_id>/examples/batch", methods=["POST"])
def add_examples_batch(voice_id):
    data = request.get_json()
    examples = data.get('examples') if data else None
    if not examples or not isinstance(examples, list):
        return jsonify({"error": "Examples must be a non-empty list."}), 400

    try:
        BrandVoice.query.get_or_404(voice_id)
        new_examples = [
            BrandVoiceExample(brand_voice_id=voice_id, content=content.strip())
            for content in examples if isinstance(content, str) and content.strip()
        ]
        if not new_examples:
            return jsonify({"error": "No valid examples provided."}), 400
        db.session.add_all(new_examples)
        db.session.commit()
        return jsonify({
            "success": True,
            "examples": [e.to_dict() for e in new_examples]
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error saving examples for brand voice {voice_id}: {str(e)}")
        return jsonify({"error": "Failed to save examples."}), 500
