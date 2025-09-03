from flask import Blueprint, request, jsonify
from src.models.social_media import db, SocialMediaAccount, SocialMediaPost, AIImageGeneration
import os
import json
from datetime import datetime, timedelta
import logging
import time

social_media_bp = Blueprint("social_media", __name__)

# Configuration - In production, these should be environment variables
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "your_huggingface_api_key")

@social_media_bp.route("/accounts", methods=["GET"])
def get_accounts():
    """Get user's connected social media accounts"""
    user_id = request.args.get("user_id", "default_user")
    
    accounts = SocialMediaAccount.query.filter_by(user_id=user_id, is_active=True).all()
    
    return jsonify({
        "accounts": [account.to_dict() for account in accounts]
    })

@social_media_bp.route("/posts", methods=["GET"])
def get_posts():
    """Get user's social media posts"""
    user_id = request.args.get("user_id", "default_user")
    status = request.args.get("status")  # Optional filter by status
    
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
    """Create a new social media post"""
    data = request.get_json()
    
    required_fields = ["account_id", "content"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Verify account exists and is active
    account = SocialMediaAccount.query.filter_by(
        id=data["account_id"],
        is_active=True
    ).first()
    
    if not account:
        return jsonify({"error": "Account not found or inactive"}), 404
    
    # Create post record
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
        
        # If image prompt provided, generate image
        if data.get("image_prompt"):
            generate_image_for_post(post.id, data["image_prompt"])
        
        return jsonify({
            "success": True,
            "post": post.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating post: {str(e)}")
        return jsonify({"error": "Failed to create post"}), 500

@social_media_bp.route("/posts/<int:post_id>/approve", methods=["POST"])
def approve_post(post_id):
    """Approve a post for publishing"""
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
        logging.error(f"Error approving post: {str(e)}")
        return jsonify({"error": "Failed to approve post"}), 500

@social_media_bp.route("/images/generate", methods=["POST"])
def generate_image():
    """Generate an AI image from a prompt"""
    data = request.get_json()
    
    if "prompt" not in data:
        return jsonify({"error": "Prompt is required"}), 400
    
    prompt = data["prompt"]
    platform = data.get("platform", "instagram")
    content_type = data.get("content_type", "post")
    model = data.get("model", "stable-diffusion-v1-5")
    provider = data.get("provider", "auto")
    
    # Create image generation record
    image_gen = AIImageGeneration(
        prompt=prompt,
        model_used=f"{provider}:{model}",
        status="pending"
    )
    
    try:
        db.session.add(image_gen)
        db.session.commit()
        
        # Generate image using AI service
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
        
        # Update image generation record
        image_gen.generation_time = generation_time
        
        if result["success"]:
            image_gen.image_url = result["image_url"]
            image_gen.status = "completed"
        image_gen.model_used = f"{result.get('provider', provider)}:{result.get('model', model)}"

        else:
            image_gen.status = "failed"
            image_gen.error_message = result.get("error", "Unknown error")
        
        db.session.commit()
        
        return jsonify({
            "success": result["success"],
            "image": image_gen.to_dict(),
            "generation_details": result if result["success"] else None
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error generating image: {str(e)}")
        return jsonify({"error": "Failed to generate image"}), 500

def generate_image_for_post(post_id, prompt, platform="instagram"):
    """Generate image for a specific post using AI image service"""
    try:
        from src.services.ai_image_service import ai_image_service
        
        # Generate image optimized for the platform
        result = ai_image_service.generate_social_media_image(
            prompt=prompt,
            platform=platform,
            content_type=content_type
        )
        
        if result["success"]:
            post = SocialMediaPost.query.get(post_id)
            if post:
                post.image_url = result["image_url"]
                db.session.commit()
                return result["image_url"]
        else:
            logging.error(f"Failed to generate image for post {post_id}: {result.get("error", "Unknown error")}")
            return None
                
    except Exception as e:
        logging.error(f"Error generating image for post {post_id}: {str(e)}")
        return None



