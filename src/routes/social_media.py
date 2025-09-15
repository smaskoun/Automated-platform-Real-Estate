# src/routes/social_media.py - UPDATED IMPORT

from flask import Blueprint, request, jsonify
from models import db
from models.social_media import SocialMediaAccount, SocialMediaPost
from models.brand_voice import BrandVoice
# UPDATED: Import both services from the same file
from services.learning_algorithm_service import learning_algorithm_service, meta_automator_service
from services.ai_content_service import ai_content_service
import json
from datetime import datetime
import logging

social_media_bp = Blueprint("social_media", __name__)

# --- NEW: META API TEST ROUTE ---
@social_media_bp.route("/meta-test", methods=["GET"])
def test_meta_integration():
    logging.info("Meta test route triggered.")
    results = meta_automator_service.get_latest_posts_with_insights()
    if results.get("success"):
        return jsonify(results), 200
    else:
        return jsonify(results), 500

# ... (rest of the file is unchanged) ...
# --- Account Management ---
@social_media_bp.route("/social-accounts", methods=["GET"])
def get_accounts():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400
    accounts = SocialMediaAccount.query.filter_by(user_id=user_id).all()
    return jsonify({"accounts": [account.to_dict() for account in accounts]})

@social_media_bp.route("/social-accounts", methods=["POST"])
def create_account():
    data = request.get_json()
    user_id, name, platform = data.get("user_id"), data.get("account_name"), data.get("platform")
    if not all([user_id, name, platform]): return jsonify({"error": "Missing required fields"}), 400
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400
    if SocialMediaAccount.query.filter_by(user_id=user_id, account_name=name).first(): return jsonify({"error": "Account with this name already exists."}), 409
    new_account = SocialMediaAccount(user_id=user_id, account_name=name, platform=platform)
    db.session.add(new_account)
    db.session.commit()
    return jsonify(new_account.to_dict()), 201

@social_media_bp.route("/social-accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    account = SocialMediaAccount.query.get_or_404(account_id)
    data = request.get_json()
    account.account_name = data.get("account_name", account.account_name)
    account.platform = data.get("platform", account.platform)
    account.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(account.to_dict()), 200

@social_media_bp.route("/social-accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    account = SocialMediaAccount.query.get_or_404(account_id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"success": True, "message": "Account deleted"}), 200

# --- AI Generation ---
@social_media_bp.route("/posts/generate", methods=["POST"])
def generate_ai_post():
    data = request.get_json()
    user_id, topic, brand_voice_id = data.get("user_id"), data.get("topic"), data.get("brand_voice_id")
    if not all([user_id, topic, brand_voice_id]): return jsonify({"error": "Missing required fields"}), 400
    brand_voice = BrandVoice.query.filter_by(id=brand_voice_id, user_id=user_id).first()
    if not brand_voice: return jsonify({"error": "BrandVoice not found"}), 404
    insights = learning_algorithm_service.get_content_recommendations()
    insights_used = True
    if not insights or "error" in insights:
        insights_used = False
        insights = {}
    try:
        generated_data = ai_content_service.generate_optimized_post(
            topic=topic,
            brand_voice_example=brand_voice.post_example,
            performance_insights=insights,
        )
        if "error" in generated_data:
            return jsonify({"error": f"AI generation failed: {generated_data['error']}"}), 500
        generated_data["insights_used"] = insights_used
        return jsonify(generated_data), 200
    except Exception as e:
        logging.error(f"Error during AI post generation: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# --- Post Management ---
@social_media_bp.route("/posts", methods=["GET"])
def get_posts():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400
    query = db.session.query(SocialMediaPost).join(SocialMediaAccount).filter(
        SocialMediaAccount.user_id == user_id
    )
    if request.args.get("status"):
        query = query.filter(SocialMediaPost.status == request.args.get("status"))
    posts = query.order_by(SocialMediaPost.created_at.desc()).all()
    return jsonify({"posts": [post.to_dict() for post in posts]})

@social_media_bp.route("/posts", methods=["POST"])
def create_post():
    data = request.get_json()
    # Require user_id, account_id and content
    required_fields = ["account_id", "content", "user_id"]
    if not all(f in data for f in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Ensure the account exists, is active and belongs to the requesting user
    account = SocialMediaAccount.query.filter_by(
        id=data["account_id"],
        user_id=data["user_id"],
        is_active=True,
    ).first()
    if not account:
        return jsonify({"error": "Account not found or unauthorized"}), 403
    scheduled_at = (
        datetime.fromisoformat(data["scheduled_at"]) if data.get("scheduled_at") else None
    )
    post = SocialMediaPost(
        account_id=data["account_id"],
        content=data["content"],
        image_prompt=data.get("image_prompt"),
        hashtags=json.dumps(data.get("hashtags", [])),
        scheduled_at=scheduled_at,
    )
    try:
        db.session.add(post)
        db.session.commit()
        return jsonify({"success": True, "post": post.to_dict()})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating post: {str(e)}")
        return jsonify({"error": "Failed to create post"}), 500

@social_media_bp.route("/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    post = SocialMediaPost.query.get_or_404(post_id)
    data = request.get_json()
    post.content = data.get("content", post.content)
    if "hashtags" in data:
        post.hashtags = json.dumps(data["hashtags"])
    if "scheduled_at" in data:
        post.scheduled_at = datetime.fromisoformat(data["scheduled_at"]) if data["scheduled_at"] else None
    post.updated_at = datetime.utcnow()
    try:
        db.session.commit()
        return jsonify({"success": True, "post": post.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating post: {str(e)}")
        return jsonify({"error": "Failed to update post"}), 500

@social_media_bp.route("/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = SocialMediaPost.query.get_or_404(post_id)
    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"success": True, "message": "Post deleted"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting post: {str(e)}")
        return jsonify({"error": "Failed to delete post"}), 500

@social_media_bp.route("/posts/<int:post_id>/approve", methods=["POST"])
def approve_post(post_id):
    post = SocialMediaPost.query.get_or_404(post_id)
    if post.status != "draft": return jsonify({"error": "Post is not in draft status"}), 400
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
    if "prompt" not in data: return jsonify({"error": "Prompt is required"}), 400
    return (
        jsonify(
            {
                "message": "Image generation not fully implemented.",
                "image_url": "https://via.placeholder.com/1080",
            }
        ),
        501,
    )
