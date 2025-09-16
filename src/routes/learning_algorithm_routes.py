"""Routes exposing learning algorithm insights."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..services.learning_algorithm_service import learning_algorithm_service
from ..services.manual_content_service import ManualContentService

learning_algorithm_bp = Blueprint("learning_algorithm", __name__)
manual_content_service = ManualContentService()


@learning_algorithm_bp.route("/fetch-performance", methods=["POST"])
def fetch_post_performance() -> tuple:
    data = request.get_json(silent=True) or {}
    platform = data.get("platform", "manual")
    limit = data.get("limit", 100)
    filters = data.get("filters") or {}

    manual_posts = manual_content_service.get_all_content(limit=limit)

    content_ids = data.get("content_ids")
    if content_ids:
        id_set = {str(content_id) for content_id in content_ids}
        manual_posts = [post for post in manual_posts if str(post.get("id")) in id_set]

    filter_platform = filters.get("platform")
    if filter_platform:
        manual_posts = [
            post
            for post in manual_posts
            if (post.get("platform") or "manual").lower() == filter_platform.lower()
        ]

    posts_data = learning_algorithm_service.fetch_post_performance(
        platform=platform,
        content_items=manual_posts,
        limit=limit,
    )

    if not posts_data:
        return jsonify({"error": "No manual content available for analysis"}), 404

    learning_algorithm_service.update_performance_history(posts_data)
    return jsonify(
        {
            "success": True,
            "posts_fetched": len(posts_data),
            "platform": platform,
            "source": "manual_content",
        }
    )


@learning_algorithm_bp.route("/analyze-patterns", methods=["POST"])
def analyze_performance_patterns() -> tuple:
    insights = learning_algorithm_service.analyze_performance_patterns()
    if "error" in insights:
        return jsonify(insights), 400
    return jsonify({"success": True, "insights": insights})


@learning_algorithm_bp.route("/recommendations", methods=["GET"])
def get_content_recommendations() -> tuple:
    content_type = request.args.get("content_type")
    recommendations = learning_algorithm_service.get_content_recommendations(content_type)
    status = 200 if "error" not in recommendations else 400
    return jsonify(recommendations), status


@learning_algorithm_bp.route("/insights", methods=["GET"])
def get_learning_insights() -> tuple:
    insights = learning_algorithm_service.learning_insights
    summary = {
        "total_posts_analyzed": len(learning_algorithm_service.performance_history),
        "insights_available": len([key for key, value in insights.items() if value]),
        "last_analysis": learning_algorithm_service.performance_history[-1]["created_time"].isoformat()
        if learning_algorithm_service.performance_history
        else None,
    }
    return jsonify({"success": True, "insights": insights, "summary": summary})
