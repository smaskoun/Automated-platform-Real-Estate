# src/routes/social_media.py - FULL REPLACEMENT (with Account Creation)

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

# --- Social Account Management ---

@social_media_bp.route("/social-accounts", methods=["GET"])
def get_accounts():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    accounts = SocialMediaAccount.query.filter_by(user_id=user_id, is_active=True).all()
    return jsonify({"accounts": [account.to_dict() for account in accounts]})

# --- NEW: Route to create a social account ---
@social_media_bp.route("/social-accounts", methods=["POST"])
def create_account():
    data = request.get_json()
    user_id = data.get("user_id")
    account_name = data.get("account_name")
    platform = data.get("platform")

    if not all([user_id, account_name, platform]):
        return jsonify({"error": "user_id, account_name, and platform are required"}), 400

    # Check for duplicate account name for the same user
    existing_account = SocialMediaAccount.query.filter_by(user_id=user_id, account_name=account_name).first()
    if existing_account:
        return jsonify({"error": "An account with this name already exists."}), 409

    new_account = SocialMediaAccount(
        user_id=user_id,
        account_name=account_name,
        platform=platform,
        is_active=True # Default to active
    )
    try:
        db.session.add(new_account)
        db.session.commit()
        return jsonify({"success": True, "account": new_account.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating social account: {str(e)}")
        return jsonify({"error": "Failed to create account"}), 500

# --- AI Post Generation ---

@social_media_bp.route("/posts/generate", methods=["POST"])
def generate_ai_post():
    data = request.get_json()
    user_id = data.get("user_id")
    topic = data.get("topic")
    brand_voice_id = data.get("brand_voice_id")

    if not all([user_id, topic, brand_voice_id]):
        return jsonify({"error": "user_id, topic, and brand_voice_id are required"}), 400

    brand_voice = BrandVoice.query.filter_by(id=brand_voice_id, user_id=user_id).first()
    if not brand_voice:
        return jsonify({"error": "BrandVoice not found"}), 404

    performance_insights = learning_algorithm_service.get_content_recommendations()

    try:
        generated_data = ai_content_service.generate_optimized_post(
            topic=topic,
            brand_voice_example=brand_voice.post_example,
            performance_insights=performance_insights
        )
        if "error" in generated_data:
            return jsonify({"error": f"AI generation failed: {generated_data['error']}"}), 500
        return jsonify(generated_data), 200
    except Exception as e:
        logging.error(f"Error during AI post generation: {str(e)}")
        return jsonify({"error": "An unexpected error occurred during post generation."}), 500

# --- Post Management ---

@social_media_bp.route("/posts", methods=["GET"])
def get_posts():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    # Join with SocialMediaAccount to get the account name
    posts = db.session.query(SocialMediaPost, SocialMediaAccount.account_name)\
        .join(SocialMediaAccount, SocialMediaPost.account_id == SocialMediaAccount.id)\
        .filter(SocialMediaAccount.user_id == user_id)\
        .order_by(SocialMediaPost.created_at.desc())\
        .all()

    # Format the response to include the account name
    posts_data = []
    for post, account_name in posts:
        post_dict = post.to_dict()
        post_dict['account_name'] = account_name
        posts_data.append(post_dict)

    return jsonify({"posts": posts_data})

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
        status=data.get("status", "draft")
    )
    
    try:
        db.session.add(post)
        db.session.commit()
        return jsonify({"success": True, "post": post.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating post: {str(e)}")
        return jsonify({"error": "Failed to create post"}), 500
