# src/routes/social_media.py - FULL REPLACEMENT

from flask import Blueprint, request, jsonify
from models import db
from models.social_media import SocialMediaAccount, SocialMediaPost
from models.brand_voice import BrandVoice
from services.learning_algorithm_service import learning_algorithm_service
from services.ai_content_service import ai_content_service
import json
from datetime import datetime
import logging

social_media_bp = Blueprint("social_media", __name__)

# NEW: AI Post Generation Route
@social_media_bp.route("/posts/generate", methods=["POST"])
def generate_ai_post():
    data = request.get_json()
    user_id = data.get("user_id")
    topic = data.get("topic")
    brand_voice_id = data.get("brand_voice_id")

    if not all([user_id, topic, brand_voice_id]):
        return jsonify({"error": "user_id, topic, and brand_voice_id are required"}), 400

    # 1. Fetch the Brand Voice for the style example
    brand_voice = BrandVoice.query.filter_by(id=brand_voice_id, user_id=user_id).first()
    if not brand_voice:
        return jsonify({"error": "BrandVoice not found"}), 404

    # 2. Get performance insights from the learning service
    # Note: In a real app, you might fetch fresh data or use cached insights.
    # Here, we call get_content_recommendations on the existing (potentially empty) history.
    performance_insights = learning_algorithm_service.get_content_recommendations()

    try:
        # 3. Call the AI service with all necessary information
        generated_data = ai_content_service.generate_optimized_post(
            topic=topic,
            brand_voice_example=brand_voice.post_example,
            performance_insights=performance_insights
        )

        if "error" in generated_data:
            return jsonify({"error": f"AI generation failed: {generated_data['error']}"}), 500

        # Return the generated content and hashtags to the frontend
        return jsonify(generated_data), 200

    except Exception as e:
        logging.error(f"Error during AI post generation: {str(e)}")
        return jsonify({"error": "An unexpected error occurred during post generation."}), 500

# --- EXISTING ROUTES (UNMODIFIED) ---

@social_media_bp.route("/social-accounts", methods=["GET"])
def get_accounts():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    accounts = SocialMediaAccount.query.filter_by(user_id=user_id, is_active=True).all()
    return jsonify({"accounts": [account.to_dict() for account in accounts]})

@social_media_bp.route("/posts", methods=["GET"])
def get_posts():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    status = request.args.get("status")
    
    query = db.session.query(SocialMediaPost).join(SocialMediaAccount).filter(
        SocialMediaAccount.user_id == user_id
    )
    if status:
        query = query.filter(SocialMediaPost.status == status)
    posts = query.order_by(SocialMediaPost.created_at.desc()).all()
    return jsonify({"posts": [post.to_dict() for post in posts]})

@social_media_bp.route("/posts", methods=["POST"])
def create_post():
    data = request.get_json()
    if not all(field in data for field in ["account_id", "content"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    account = SocialMediaAccount.query.filter_by(id=data["account_id"], is_active=True).first()
    if not account:
        return jsonify({"error": "Account not found or inactive"}), 404
    
    post = SocialMediaPost(
        account_id=data["account_id"],
        content=data["content"],
        image_prompt=data.get("image_prompt"),
        hashtags=json.dumps(data.get("hashtags", [])),
        scheduled_at=datetime.fromisoformat(data["scheduled_at"]) if data.get("scheduled_at") else None
    )
    
    try:
        db.session.add(post)
        db.session.commit()
        return jsonify({"success": True, "post": post.to_dict()})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating post: {str(e)}")
        return jsonify({"error": "Failed to create post"}), 500

@social_media_bp.route("/posts/<int:post_id>/approve", methods=["POST"])
def approve_post(post_id):
    post = SocialMediaPost.query.get_or_404(post_id)
    if post.status != "draft":
        return jsonify({"error": "Post is not in draft status"}), 400
    
    try:
        post.status = "approved"
        post.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({"success": True, "post": post.to_dict()})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error approving post: {str(e)}")
        return jsonify({"error": "Failed to approve post"}), 500

@social_media_bp.route("/images/generate", methods=["POST"])
def generate_image():
    data = request.get_json()
    if "prompt" not in data:
        return jsonify({"error": "Prompt is required"}), 400
    return jsonify({
        "message": "Image generation not fully implemented.",
        "image_url": "https://via.placeholder.com/1080"
    } ), 501
