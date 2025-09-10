from flask import Blueprint, jsonify, current_app
import json
import os # <-- Import the 'os' module

market_analysis_bp = Blueprint('market_analysis_bp', __name__)

@market_analysis_bp.route('/local-market-report', methods=['GET'])
def get_local_market_report():
    """
    API endpoint to fetch the local market report from a JSON file.
    This method is 100% reliable as it does not depend on external websites.
    """
    try:
        # --- THIS IS THE FIX ---
        # Construct a reliable path to the data file relative to the app's root
        # This works correctly on both local machines and production servers like Render
        file_path = os.path.join(current_app.root_path, 'data', 'market_report_sample.json')
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
        
    except FileNotFoundError:
        print("ERROR: market_report_sample.json not found at path:", file_path)
        return jsonify({"error": "Market report data file not found on the server."}), 404
    except Exception as e:
        print(f"CRITICAL: An error occurred loading the local market report: {e}")
        return jsonify({"error": "An unexpected error occurred on the server."}), 500

