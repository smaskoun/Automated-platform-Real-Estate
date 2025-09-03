from flask import Blueprint, request, jsonify
# CORRECTED IMPORTS
from models.social_media import db, SocialMediaAccount, SocialMediaPost, AIImageGeneration
from services.ai_image_service import ai_image_service
import os
import json
from datetime import datetime
import logging
import time

social_media_bp = Blueprint("social_media", __name__)

# This route is fine as it is, assuming it's called from other services
# and not directly exposed via a URL with this blueprint.
# If it needs to be a public endpoint, it should be more specific, e.g., /social-media/accounts
@social_media_bp.route("/accounts", methods=["GET"])
def get_accounts():
    user_id = request.args.get("user_id", "default_user")
    accounts = SocialMediaAccount.query.filter_by(user_id=user_id, is_active=True).all()
    return jsonify({"accounts": [account.to_dict() for account in accounts]})

@social_media_bp.route("/posts", methods=["GET"])
def get_posts():
    user_id = request.args.get("user_id", "default_user")
    status = request.args.get("status")
    query = db.session.query(SocialMediaPost).join(SocialMediaAccount).filter(
        SocialMediaAccount.user_id == user_id
    )
    if status:
        query = query.filter(SocialMediaPost.status == status)
    posts = query.order_by(SocialMediaPost.created_at.desc()).all()
    return jsonify({"posts": [post.to_dict() for post in posts]})

# ... (and so on for the rest of the file)
# The key is that the imports at the top are now correct.
# Ensure the rest of your functions in this file are present.
