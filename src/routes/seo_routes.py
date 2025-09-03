from flask import Blueprint, request, jsonify
# CORRECTED IMPORTS
from services.seo_content_service import SEOContentService
import logging

seo_bp = Blueprint('seo_bp', __name__)
seo_service = SEOContentService()

@seo_bp.route('/analyze-keywords', methods=['POST'])
def analyze_keywords_route():
    data = request.get_json()
    if not data or 'keywords' not in data:
        return jsonify({"error": "Keywords are required"}), 400
    
    try:
        result = seo_service.analyze_keywords(data['keywords'])
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error in keyword analysis: {e}")
        return jsonify({"error": "Failed to analyze keywords"}), 500

# ... (and so on for the rest of the file)
# The key is that the imports at the top are now correct.
