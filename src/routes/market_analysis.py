from flask import Blueprint, jsonify
import json
import os # <-- We still need the 'os' module

market_analysis_bp = Blueprint('market_analysis_bp', __name__)

@market_analysis_bp.route('/local-market-report', methods=['GET'])
def get_local_market_report():
    """
    API endpoint to fetch the local market report from a JSON file.
    This method uses an absolute path to ensure file is found on any server.
    """
    try:
        # --- THIS IS THE FINAL, ROBUST FIX ---
        # Get the absolute directory of the current file (e.g., /.../src/routes)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Navigate up one level to the 'src' directory, then into the 'data' directory
        # This creates a foolproof path: /.../src/data/market_report_sample.json
        file_path = os.path.join(current_dir, '..', 'data', 'market_report_sample.json')
        
        # The 'normpath' function cleans up the path (e.g., handles the '..')
        file_path = os.path.normpath(file_path)

        print(f"Attempting to open file at absolute path: {file_path}") # Add logging

        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
        
    except FileNotFoundError:
        print(f"ERROR: market_report_sample.json not found at path: {file_path}")
        return jsonify({"error": "Market report data file not found on the server."}), 404
    except Exception as e:
        print(f"CRITICAL: An error occurred loading the local market report: {e}")
        return jsonify({"error": "An unexpected error occurred on the server."}), 500
