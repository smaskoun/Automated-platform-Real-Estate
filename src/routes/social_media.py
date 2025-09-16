 codex/fix-syntax-error-in-ab_testing_routes-tnow9p
"""HTTP endpoints for managing social media accounts and posts."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Optional

from flask import Blueprint, jsonify, request

from ..models import db
from ..models.brand_voice import BrandVoice
from ..models.social_media import SocialMediaAccount, SocialMediaPost
from ..services.ai_content_service import ai_content_service
from ..services.ai_image_service import ai_image_service
from ..services.learning_algorithm_service import learning_algorithm_service

LOGGER = logging.getLogger(__name__)
social_media_bp = Blueprint("social_media", __name__)


# ---------------------------------------------------------------------------
# Account management
# ---------------------------------------------------------------------------
@social_media_bp.route("/social-accounts", methods=["GET"])
def get_accounts() -> Any:
    """Return the social accounts that belong to a given user."""

    raw_user_id = request.args.get("user_id")
    if raw_user_id is None:
        return jsonify({"error": "user_id is required"}), 400
    try:
        user_id = int(raw_user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    accounts = SocialMediaAccount.query.filter_by(user_id=user_id).all()
    return jsonify({"accounts": [account.to_dict() for account in accounts]})


@social_media_bp.route("/social-accounts", methods=["POST"])
def create_account() -> Any:
    """Create a social media account owned by the given user."""

    payload = request.get_json(silent=True) or {}
    required_fields = {"user_id", "account_name", "platform"}
    if not required_fields.issubset(payload):
        return jsonify({"error": "user_id, account_name and platform are required"}), 400

    try:
        user_id = int(payload["user_id"])
    except (TypeError, ValueError):
        return jsonify({"error": "user_id must be an integer"}), 400

    existing = SocialMediaAccount.query.filter_by(
        user_id=user_id, account_name=payload["account_name"]
    ).first()
    if existing:
        return jsonify({"error": "Account with this name already exists"}), 409

    account = SocialMediaAccount(
        user_id=user_id,
        account_name=payload["account_name"],
        platform=payload["platform"],
    )
    db.session.add(account)
    db.session.commit()
    return jsonify(account.to_dict()), 201


@social_media_bp.route("/social-accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id: int) -> Any:
    """Update mutable fields for a stored account."""

    account = SocialMediaAccount.query.get_or_404(account_id)
    payload = request.get_json(silent=True) or {}

    account.account_name = payload.get("account_name", account.account_name)
    account.platform = payload.get("platform", account.platform)
    account.updated_at = datetime.utcnow()

    db.session.commit()
    return jsonify(account.to_dict())


@social_media_bp.route("/social-accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id: int) -> Any:
    """Delete the selected social account."""

    account = SocialMediaAccount.query.get_or_404(account_id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"success": True, "message": "Account deleted"})


# ---------------------------------------------------------------------------
# AI content generation
# ---------------------------------------------------------------------------
@social_media_bp.route("/posts/generate", methods=["POST"])
def generate_ai_post() -> Any:
    """Generate a social media post tailored to the stored brand voice."""

    payload = request.get_json(silent=True) or {}
    required = {"user_id", "topic", "brand_voice_id"}
    if not required.issubset(payload):
        return jsonify({"error": "user_id, topic and brand_voice_id are required"}), 400

    try:
        user_id = int(payload["user_id"])
    except (TypeError, ValueError):
        return jsonify({"error": "user_id must be an integer"}), 400

    brand_voice = BrandVoice.query.filter_by(
        id=payload["brand_voice_id"], user_id=user_id
    ).first()
    if not brand_voice:
        return jsonify({"error": "Brand voice not found for this user"}), 404

    insights_used = True
    insights = learning_algorithm_service.get_content_recommendations()
    if isinstance(insights, dict) and insights.get("error"):
        insights_used = False
        insights = {}

    try:
        generated = ai_content_service.generate_optimized_post(
            topic=payload["topic"],
            brand_voice_example=brand_voice.post_example,
            performance_insights=insights,
        )
    except Exception as exc:  # pragma: no cover - network errors happen at runtime
        LOGGER.error("Failed to generate AI post: %s", exc)
        return jsonify({"error": "AI content generation failed"}), 502

    if isinstance(generated, dict) and generated.get("error"):
        return jsonify({"error": f"AI generation failed: {generated['error']}"}), 502

    generated["insights_used"] = insights_used
    return jsonify(generated)


# ---------------------------------------------------------------------------
# Post management
# ---------------------------------------------------------------------------
@social_media_bp.route("/posts", methods=["GET"])
def get_posts() -> Any:
    """Return posts belonging to the requesting user."""

    raw_user_id = request.args.get("user_id")
    if raw_user_id is None:
        return jsonify({"error": "user_id is required"}), 400
    try:
        user_id = int(raw_user_id)
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400

    query = (
        db.session.query(SocialMediaPost)
        .join(SocialMediaAccount)
        .filter(SocialMediaAccount.user_id == user_id)
    )
    status = request.args.get("status")
    if status:
        query = query.filter(SocialMediaPost.status == status)

    posts = query.order_by(SocialMediaPost.created_at.desc()).all()
    return jsonify({"posts": [post.to_dict() for post in posts]})


@social_media_bp.route("/posts", methods=["POST"])
def create_post() -> Any:
    """Persist a manually created post tied to an account."""

    payload = request.get_json(silent=True) or {}
    required = {"account_id", "content", "user_id"}
    if not required.issubset(payload):
        return jsonify({"error": "account_id, content and user_id are required"}), 400

    account = SocialMediaAccount.query.filter_by(
        id=payload["account_id"],
        user_id=payload["user_id"],
        is_active=True,
    ).first()
    if not account:
        return jsonify({"error": "Account not found or inactive"}), 403

    try:
        scheduled_at = _parse_datetime(payload.get("scheduled_at"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    hashtags = _serialise_hashtags(payload.get("hashtags", []))

    post = SocialMediaPost(
        account_id=payload["account_id"],
        content=payload["content"],
        image_prompt=payload.get("image_prompt"),
        hashtags=hashtags,
        scheduled_at=scheduled_at,
    )

    try:
        db.session.add(post)
        db.session.commit()
    except Exception as exc:  # pragma: no cover - DB errors are logged at runtime
        db.session.rollback()
        LOGGER.error("Failed to create post: %s", exc)
        return jsonify({"error": "Failed to create post"}), 500

    return jsonify({"success": True, "post": post.to_dict()}), 201


@social_media_bp.route("/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id: int) -> Any:
    """Update content and scheduling information for a post."""

    post = SocialMediaPost.query.get_or_404(post_id)
    payload = request.get_json(silent=True) or {}

    post.content = payload.get("content", post.content)
    if "hashtags" in payload:
        post.hashtags = _serialise_hashtags(payload.get("hashtags", []))
    if "scheduled_at" in payload:
        try:
            post.scheduled_at = _parse_datetime(payload.get("scheduled_at"))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
    post.updated_at = datetime.utcnow()

    try:
        db.session.commit()
    except Exception as exc:  # pragma: no cover - DB errors are logged at runtime
        db.session.rollback()
        LOGGER.error("Failed to update post: %s", exc)
        return jsonify({"error": "Failed to update post"}), 500

    return jsonify({"success": True, "post": post.to_dict()})


@social_media_bp.route("/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id: int) -> Any:
    """Remove a post permanently."""

=======
# src/routes/social_media.py - CORRECTED VERSION

from flask import Blueprint, request, jsonify
# --- FIX: Changed all relative imports to absolute ---
from ..models import db
from ..models.social_media import SocialMediaAccount, SocialMediaPost
from ..models.brand_voice import BrandVoice
 codex/fix-syntax-error-in-ab_testing_routes-s2rdpm
from ..services.learning_algorithm_service import learning_algorithm_service

from ..services.learning_algorithm_service import learning_algorithm_service, meta_automator_service
 main
from ..services.ai_content_service import ai_content_service
import json
from datetime import datetime
import logging

social_media_bp = Blueprint("social_media", __name__)

 codex/fix-syntax-error-in-ab_testing_routes-s2rdpm

# --- NEW: META API TEST ROUTE ---
@social_media_bp.route("/meta-test", methods=["GET"])
def test_meta_integration():
    logging.info("Meta test route triggered.")
    results = meta_automator_service.get_latest_posts_with_insights()
    if results.get("success"):
        return jsonify(results), 200
    else:
        return jsonify(results), 500

 main
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
 main
    post = SocialMediaPost.query.get_or_404(post_id)
    try:
        db.session.delete(post)
        db.session.commit()
 codex/fix-syntax-error-in-ab_testing_routes-tnow9p
    except Exception as exc:  # pragma: no cover - DB errors are logged at runtime
        db.session.rollback()
        LOGGER.error("Failed to delete post: %s", exc)
        return jsonify({"error": "Failed to delete post"}), 500

    return jsonify({"success": True, "message": "Post deleted"})


@social_media_bp.route("/posts/<int:post_id>/approve", methods=["POST"])
def approve_post(post_id: int) -> Any:
    """Mark a draft as approved."""

    post = SocialMediaPost.query.get_or_404(post_id)
    if post.status != "draft":
        return jsonify({"error": "Post is not in draft status"}), 400

=======
        return jsonify({"success": True, "message": "Post deleted"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting post: {str(e)}")
        return jsonify({"error": "Failed to delete post"}), 500

@social_media_bp.route("/posts/<int:post_id>/approve", methods=["POST"])
def approve_post(post_id):
    post = SocialMediaPost.query.get_or_404(post_id)
    if post.status != "draft": return jsonify({"error": "Post is not in draft status"}), 400
 main
    try:
        post.status = "approved"
        post.updated_at = datetime.utcnow()
        db.session.commit()
 codex/fix-syntax-error-in-ab_testing_routes-tnow9p
    except Exception as exc:  # pragma: no cover
        db.session.rollback()
        LOGGER.error("Failed to approve post: %s", exc)
        return jsonify({"error": "Failed to approve post"}), 500

    return jsonify({"success": True, "post": post.to_dict()})


# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------
@social_media_bp.route("/images/generate", methods=["POST"])
def generate_image() -> Any:
    """Generate a social graphic for the supplied prompt."""

    payload = request.get_json(silent=True) or {}
    prompt = payload.get("prompt")
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    platform = payload.get("platform", "instagram")
    content_type = payload.get("content_type", "post")

    try:
        result = ai_image_service.generate_social_media_image(prompt, platform, content_type)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    status_code = 200 if result.get("success") else 503
    return jsonify(result), status_code


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        cleaned = value.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned)
    except (AttributeError, ValueError):
        raise ValueError("scheduled_at must be an ISO 8601 string")


def _serialise_hashtags(hashtags: Any) -> str:
    if isinstance(hashtags, list):
        cleaned = [tag for tag in hashtags if isinstance(tag, str)]
    elif isinstance(hashtags, str):
        cleaned = [tag.strip() for tag in hashtags.split() if tag.strip()]
    else:
        cleaned = []
    return json.dumps(cleaned)


__all__ = ["social_media_bp"]
=======
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
 main
