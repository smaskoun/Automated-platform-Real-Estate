from flask import Blueprint, request, jsonify
# --- FIX: Changed relative import to absolute ---
from ..services.seo_content_service import SEOContentService
import logging

seo_tools_bp = Blueprint('seo_tools_bp', __name__)
seo_service = SEOContentService()


@seo_tools_bp.route('/keyword-density', methods=['POST'])
def keyword_density_route():
    data = request.get_json()
    if not data or 'text' not in data or 'keyword' not in data:
        return jsonify({'error': 'text and keyword are required'}), 400

    text = data['text']
    keyword = data['keyword']
    try:
        result = seo_service.keyword_density(text, keyword)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f'Error in keyword density analysis: {e}')
        return jsonify({'error': 'Failed to analyze keyword density'}), 500
