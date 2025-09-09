from flask import Blueprint, jsonify
import requests
from datetime import datetime, timedelta # <<< THIS IS THE FIX

market_analysis_bp = Blueprint('market_analysis_bp', __name__)

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- WECAR Tech API Data Processing ---
@market_analysis_bp.route('/wecar-stats', methods=['GET'])
def get_wecar_data():
    try:
        # Get the current year and month to build the URL dynamically
        now = datetime.now()
        year = now.year
        # Get the 3-letter, lowercase month (e.g., 'sep', 'aug')
        month_abbr = now.strftime('%b').lower()

        # Build the URL to the summary.json file for the current month
        wecar_api_url = f"https://wecartech.com/wecfiles/stats_new/{year}/{month_abbr}/summary.json"
        
        print(f"INFO: Calling WECAR API at: {wecar_api_url}" )
        response = requests.get(wecar_api_url, headers=REQUEST_HEADERS, timeout=20)
        
        # If the current month's data isn't up yet, try last month
        if response.status_code == 404:
            print(f"INFO: Current month '{month_abbr}' not found. Trying previous month.")
            # A simple way to get last month's year and month abbreviation
            last_month_date = now.replace(day=1) - timedelta(days=1)
            year = last_month_date.year
            month_abbr = last_month_date.strftime('%b').lower()
            wecar_api_url = f"https://wecartech.com/wecfiles/stats_new/{year}/{month_abbr}/summary.json"
            print(f"INFO: Trying WECAR API at: {wecar_api_url}" )
            response = requests.get(wecar_api_url, headers=REQUEST_HEADERS, timeout=20)

        response.raise_for_status()
        api_data = response.json()
        print("INFO: WECAR API data received successfully.")

        # The JSON structure is straightforward. We just need to format it for the frontend.
        processed_data = {
            'report_period': api_data.get('Date', 'Latest Report'),
            'average_price': f"${int(api_data.get('AveragePrice', 0)):,}", # Format as currency
            'total_sales': api_data.get('Sales', 'N/A'),
            'new_listings': api_data.get('NewListings', 'N/A')
        }

        return jsonify(processed_data)

    except Exception as e:
        print(f"CRITICAL: An exception occurred in get_wecar_data: {e}")
        return jsonify({"error": "Failed to fetch or process WECAR data."}), 500

# We will keep the CMHC route but use dummy data for max reliability
@market_analysis_bp.route('/cmhc-rental-market', methods=['GET'])
def get_cmhc_data():
    print("INFO: Returning dummy data for CMHC.")
    dummy_data = {
        "windsor": { "vacancy_rate_pct": 2.5, "avg_rent_total": 1350 },
        "ontario": { "vacancy_rate_pct": 1.8, "avg_rent_total": 1750 }
    }
    return jsonify(dummy_data)
