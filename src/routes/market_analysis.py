from flask import Blueprint, jsonify
import json
import os

market_analysis_bp = Blueprint('market_analysis_bp', __name__)

def get_data_file_path(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, '..', 'data', filename)

@market_analysis_bp.route('/full-market-report', methods=['GET'])
def get_full_market_report():
    try:
        data_file = get_data_file_path('market_report_sample.json')
        print(f"INFO: Reading local market report from: {data_file}")
        with open(data_file, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print(f"CRITICAL: Could not read local market report file. Error: {e}")
        return jsonify({"error": "Could not read local market report file."}), 500
