from flask import Blueprint, request, jsonify
from src.models.social_media import db, SocialMediaAccount, SocialMediaPost, AIImageGeneration
import os
import json
from datetime import datetime
import logging
import time

# Create a Blueprint for social media routes
social_media_bp = Blueprint("social_media", __name__)

# --- Routes for Social Media Accounts ---

@social_media_bp.route("/accounts", methods=["GET"])
def get_accounts():
    """Get user's connected social media accounts."""
    user_id = request.args.get("user_id", "default_user")
    
    accounts = SocialMediaAccount.query.filter_by(user_id=user_id, is_active=True).all()
    
    return jsonify({
        "accounts": [account.to_dict() for account in accounts]
    })

# --- Routes for Social Media Posts ---

@social_media_bp.route("/posts", methods=["GET"])
def get_posts():
    """Get user's social media posts, with an optional filter for status."""
    user_id = request.args.get("user_id", "default_user")
    status = request.args.get("status")
    
    query = db.session.query(SocialMediaPost).join(SocialMediaAccount).filter(
        SocialMediaAccount.user_id == user_id
    )
    
    if status:
        query = query.filter(SocialMediaPost.status == status)
    
    posts = query.order_by(SocialMediaPost.created_at.desc()).all()
    
    return jsonify({
        "posts": [post.to_dict() for post in posts]
    })

@social_media_bp.route("/posts", methods=["POST"])
def create_post():
    """Create a new social media post."""
    data = request.get_json()
    
    if not data or "account_id" not in data or "content" not in data:
        return jsonify({"error": "Missing required fields: 'account_id' and 'content'"}), 400
    
    account = SocialMediaAccount.query.filter_by(id=data["account_id"], is_active=True).first()
    if not account:
        return jsonify({"error": "Account not found or is inactive"}), 404
    
    try:
        post = SocialMediaPost(
            account_id=data["account_id"],
            content=data["content"],
            image_prompt=data.get("image_prompt"),
            hashtags=json.dumps(data.get("hashtags", [])),
            scheduled_at=datetime.fromisoformat(data["scheduled_at"]) if data.get("scheduled_at") else None
        )
        db.session.add(post)
        db.session.commit()
        
        # If an image prompt is provided, trigger the image generation process
        if post.image_prompt:
            # Note: This runs synchronously. For production, consider a background task.
            generate_image_for_post(post.id, post.image_prompt)
        
        return jsonify({
            "success": True,
            "post": post.to_dict()
        }), 201 # Use 201 Created for successful resource creation
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating post: {str(e)}")
        return jsonify({"error": "An internal error occurred while creating the post"}), 500

@social_media_bp.route("/posts/<int:post_id>/approve", methods=["POST"])
def approve_post(post_id):
    """Approve a drafted post for publishing."""
    post = SocialMediaPost.query.get_or_404(post_id)
    
    if post.status != "draft":
        return jsonify({"error": "Post is not in draft status"}), 400
    
    try:
        post.status = "approved"
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "post": post.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error approving post {post_id}: {str(e)}")
        return jsonify({"error": "Failed to approve post"}), 500

# --- Route for AI Image Generation ---

@social_media_bp.route("/images/generate", methods=["POST"])
def generate_image():
    """Generate an AI image from a prompt and store it."""
    data = request.get_json()
    
    if not data or "prompt" not in data:
        return jsonify({"error": "Prompt is required"}), 400
    
    prompt = data["prompt"]
    platform = data.get("platform", "instagram")
    content_type = data.get("content_type", "post")
    model = data.get("model", "stable-diffusion-v1-5")
    provider = data.get("provider", "auto")
    
    image_gen = AIImageGeneration(
        prompt=prompt,
        model_used=f"{provider}:{model}", # Initial model name
        status="pending"
    )
    
    try:
        db.session.add(image_gen)
        db.session.commit()
        
        from src.services.ai_image_service import ai_image_service
        
        start_time = time.time()
        result = ai_image_service.generate_social_media_image(
            prompt=prompt,
            platform=platform,
            content_type=content_type,
            model=model,
            provider=provider
        )
        generation_time = time.time() - start_time
        
        image_gen.generation_time = generation_time
        
        if result and result.get("success"):
            image_gen.image_url = result.get("image_url")
            image_gen.status = "completed"
            # This is the line that was fixed
            image_gen.model_used = f"{result.get('provider', provider)}:{result.get('model', model)}"
        else:
            image_gen.status = "failed"
            image_gen.error_message = result.get("error", "Unknown error during generation")
        
        db.session.commit()
        
        return jsonify({
            "success": image_gen.status == "completed",
            "image": image_gen.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Critical error in image generation endpoint: {str(e)}")
        # If image_gen exists, mark it as failed
        if 'image_gen' in locals() and image_gen.status == "pending":
            image_gen.status = "failed"
            image_gen.error_message = "Server exception occurred."
            db.session.commit()
        return jsonify({"error": "A critical server error occurred"}), 500

# --- Helper Function ---

def generate_image_for_post(post_id, prompt, platform="instagram", content_type="post"):
    """
    Background task to generate an image for a specific post.
    Logs errors but does not return HTTP responses.
    """
    try:
        from src.services.ai_image_service import ai_image_service
        
        result = ai_image_service.generate_social_media_image(
            prompt=prompt,
            platform=platform,
            content_type=content_type
        )
        
        post = SocialMediaPost.query.get(post_id)
        if not post:
            logging.error(f"Post with ID {post_id} not found after image generation.")
            return

        if result and result.get("success"):
            post.image_url = result.get("image_url")
            logging.info(f"Successfully generated image for post {post_id}.")
        else:
            error_msg = result.get("error", "Unknown error")
            logging.error(f"Failed to generate image for post {post_id}: {error_msg}")
        
        db.session.commit()

    except Exception as e:
        logging.error(f"Exception during image generation for post {post_id}: {str(e)}")
        db.session.rollback()

