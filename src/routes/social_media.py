# src/routes/social_media.py - CORRECTED VERSION

from flask import Blueprint, request, jsonify
from models import db  # Corrected: Import db from the models package
from models.social_media import SocialMediaAccount, SocialMediaPost, AIImageGeneration
import json
from datetime import datetime
import logging

social_media_bp = Blueprint("social_media", __name__)

# This route will be at /api/social-media/social-accounts
@social_media_bp.route("/social-accounts", methods=["GET"])
def get_accounts():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    accounts = SocialMediaAccount.query.filter_by(user_id=user_id, is_active=True).all()
    return jsonify({"accounts": [account.to_dict() for account in accounts]})

# This route will be at /api/social-media/posts
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

# This route will be at /api/social-media/posts
@social_media_bp.route("/posts", methods=["POST"])
def create_post():
    data = request.get_json()
    required_fields = ["account_id", "content"]
    if not all(field in data for field in required_fields):
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

# This route will be at /api/social-media/posts/<id>/approve
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

# This route will be at /api/social-media/images/generate
@social_media_bp.route("/images/generate", methods=["POST"])
def generate_image():
    data = request.get_json()
    if "prompt" not in data:
        return jsonify({"error": "Prompt is required"}), 400
    return jsonify({
        "message": "Image generation not fully implemented.",
        "image_url": "https://via.placeholder.com/1080" # Placeholder image
    }  ), 501
