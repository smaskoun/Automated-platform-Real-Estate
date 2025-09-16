"""Routes exposing SEO analysis capabilities."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from flask import Blueprint, jsonify, request

from ..services.manual_content_service import ManualContentService
from ..services.seo_content_service import SEOContentService

seo_bp = Blueprint("seo_bp", __name__)
seo_service = SEOContentService()
manual_content_service = ManualContentService()

LOGGER = logging.getLogger(__name__)


@seo_bp.route("/analyze-keywords", methods=["POST"])
def analyze_keywords_route() -> Any:
    data = request.get_json(silent=True) or {}
    keywords = data.get("keywords")
    if not isinstance(keywords, list):
        return jsonify({"error": "Keywords must be provided as a list"}), 400

    try:
        result = seo_service.analyze_keywords(keywords)
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover - defensive logging
        LOGGER.exception("Keyword analysis failed: %%s", exc)
        return jsonify({"error": "Failed to analyze keywords"}), 500


@seo_bp.route("/evaluate-content", methods=["POST"])
def evaluate_content() -> Any:
    """Evaluate SEO for provided posts and optionally recent manual uploads."""

    data = request.get_json(silent=True) or {}
    include_manual = data.get("include_manual", not bool(data.get("posts")))
    manual_limit = data.get("manual_limit", 50)
    manual_filters = data.get("manual_filters") or {}

    posts_to_evaluate: List[Dict] = []
    provided_posts = data.get("posts", [])
    if provided_posts:
        if not isinstance(provided_posts, list):
            return jsonify({"error": "posts must be a list of content objects"}), 400
        posts_to_evaluate.extend(provided_posts)

    if include_manual:
        manual_posts = manual_content_service.get_all_content(limit=manual_limit)
        content_ids = manual_filters.get("content_ids") or data.get("content_ids")
        if content_ids:
            id_set = {str(content_id) for content_id in content_ids}
            manual_posts = [post for post in manual_posts if str(post.get("id")) in id_set]

        filter_platform = manual_filters.get("platform")
        if filter_platform:
            manual_posts = [
                post
                for post in manual_posts
                if (post.get("platform") or "manual").lower() == filter_platform.lower()
            ]

        for post in manual_posts:
            post["manual_source"] = True
        posts_to_evaluate.extend(manual_posts)

    if not posts_to_evaluate:
        return jsonify({"error": "No content provided for evaluation"}), 400

    try:
        evaluation = seo_service.evaluate_posts(posts_to_evaluate)
        return jsonify({
            "success": True,
            "data": evaluation,
            "message": "SEO evaluation completed successfully",
        })
    except Exception as exc:  # pragma: no cover - defensive logging
        LOGGER.exception("Error evaluating content SEO: %%s", exc)
        return jsonify({"error": "Failed to evaluate content"}), 500


@seo_bp.route("/content-calendar", methods=["GET"])
def generate_content_calendar() -> Any:
    days = request.args.get("days", default=30, type=int)
    platform = request.args.get("platform", default="instagram")

    try:
        calendar = seo_service.generate_content_calendar(days=days, platform=platform)
        return jsonify({"success": True, "calendar": calendar})
    except Exception as exc:  # pragma: no cover - defensive logging
        LOGGER.exception("Failed to generate calendar: %%s", exc)
        return jsonify({"error": "Failed to generate content calendar"}), 500
