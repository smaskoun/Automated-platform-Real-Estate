from flask import Blueprint, jsonify
import requests
from datetime import datetime, timedelta

market_analysis_bp = Blueprint('market_analysis_bp', __name__)

# --- WECAR Automated Data Fetching ---
@market_analysis_bp.route('/wecar-market-report', methods=['GET'])
def get_wecar_market_report():
    """
    API endpoint to fetch the latest available market report from WECAR's data source.
    It tries the current month first, then falls back to the previous month.
    """
    base_url = "https://wecartech.com/wecfiles/stats_new"
    headers = {'User-Agent': 'Mozilla/5.0'} # Act like a browser
    
    today = datetime.now( )
    
    # --- Attempt 1: Try the current month ---
    current_year = today.year
    current_month_short = today.strftime('%b').lower() # e.g., 'sep'
    url_current = f"{base_url}/{current_year}/{current_month_short}/summary.json"
    
    print(f"INFO: Attempting to fetch data for current month from: {url_current}")
    
    try:
        response = requests.get(url_current, headers=headers, timeout=10)
        response.raise_for_status() # This will raise an error for 4xx or 5xx status
        print("INFO: Current month data found and fetched successfully.")
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print(f"INFO: Could not fetch data for current month ({e}). Trying previous month.")

    # --- Attempt 2: Fallback to the previous month ---
    # Calculate the previous month
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    
    prev_year = last_day_of_previous_month.year
    prev_month_short = last_day_of_previous_month.strftime('%b').lower()
    url_previous = f"{base_url}/{prev_year}/{prev_month_short}/summary.json"

    print(f"INFO: Attempting to fetch data for previous month from: {url_previous}")

    try:
        response = requests.get(url_previous, headers=headers, timeout=10)
        response.raise_for_status()
        print("INFO: Previous month data found and fetched successfully.")
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print(f"CRITICAL: Could not fetch data for previous month either ({e}).")
        return jsonify({"error": "Failed to fetch the latest market report from WECAR."}), 500

