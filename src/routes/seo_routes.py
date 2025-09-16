from flask import Blueprint, request, jsonify
# --- FIX: Changed relative import to absolute ---
from ..services.seo_content_service import SEOContentService
 codex/fix-syntax-error-in-ab_testing_routes-tnow9p
from ..services.manual_content_service import ManualContentService

 codex/fix-syntax-error-in-ab_testing_routes-s2rdpm
from ..services.manual_content_service import ManualContentService

 main
 main
import logging

seo_bp = Blueprint('seo_bp', __name__)
seo_service = SEOContentService()
 codex/fix-syntax-error-in-ab_testing_routes-tnow9p
manual_content_service = ManualContentService()


 codex/fix-syntax-error-in-ab_testing_routes-s2rdpm
manual_content_service = ManualContentService()

 main

 main
@seo_bp.route('/analyze-keywords', methods=['POST'])
def analyze_keywords_route():
    data = request.get_json()
    if not data or 'keywords' not in data:
        return jsonify({"error": "Keywords are required"}), 400

    keywords = data['keywords']
    if not isinstance(keywords, list):
        return jsonify({"error": "Keywords must be a list"}), 400

    try:
        result = seo_service.analyze_keywords(keywords)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Error in keyword analysis: {e}")
        return jsonify({"error": "Failed to analyze keywords"}), 500

 codex/fix-syntax-error-in-ab_testing_routes-tnow9p

 codex/fix-syntax-error-in-ab_testing_routes-s2rdpm
 main
@seo_bp.route('/evaluate-content', methods=['POST'])
def evaluate_content():
    """Evaluate SEO quality of manual uploads and/or generated posts."""

    data = request.get_json(silent=True) or {}
    include_manual = data.get('include_manual', not bool(data.get('posts')))
    manual_limit = data.get('manual_limit', 50)
    manual_filters = data.get('manual_filters') or {}

    posts_to_evaluate = []

    provided_posts = data.get('posts', [])
    if provided_posts:
        if not isinstance(provided_posts, list):
            return jsonify({'error': 'posts must be a list of content objects'}), 400
        posts_to_evaluate.extend(provided_posts)

    if include_manual:
        manual_posts = manual_content_service.get_all_content(limit=manual_limit)

        content_ids = manual_filters.get('content_ids') or data.get('content_ids')
        if content_ids:
            id_set = {str(content_id) for content_id in content_ids}
            manual_posts = [
                post for post in manual_posts
                if str(post.get('id')) in id_set
            ]

        filter_platform = manual_filters.get('platform')
        if filter_platform:
            manual_posts = [
                post for post in manual_posts
                if (post.get('platform') or 'manual').lower() == filter_platform.lower()
            ]

        for post in manual_posts:
            post['manual_source'] = True

        posts_to_evaluate.extend(manual_posts)

    if not posts_to_evaluate:
        return jsonify({'error': 'No content provided for evaluation'}), 400

    try:
        evaluation = seo_service.evaluate_posts(posts_to_evaluate)
        return jsonify({
            'success': True,
            'data': evaluation,
            'message': 'SEO evaluation completed successfully'
        })
    except Exception as exc:
        logging.error(f'Error evaluating content SEO: {exc}')
        return jsonify({'error': 'Failed to evaluate content'}), 500

# Additional SEO endpoints can be defined below.
 codex/fix-syntax-error-in-ab_testing_routes-tnow9p


# ... (and so on for the rest of the file)
# The key is that the imports at the top are now correct.
 main
 main
