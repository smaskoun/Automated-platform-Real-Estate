from flask import Blueprint, jsonify
import requests

market_analysis_bp = Blueprint('market_analysis_bp', __name__)

# This is the direct API endpoint the CREA website uses to get its data.
# Calling this is much more reliable than scraping the HTML page.
CREA_API_URL = "https://stats.crea.ca/api/stats/board/wind"

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64 ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://stats.crea.ca/board/wind', # It's good practice to say where the request is coming from
}

@market_analysis_bp.route('/crea-stats', methods=['GET'] )
def get_crea_data():
    try:
        print(f"INFO: Calling CREA API directly at {CREA_API_URL}")
        response = requests.get(CREA_API_URL, headers=REQUEST_HEADERS, timeout=20)
        response.raise_for_status()
        
        api_data = response.json()
        print("INFO: CREA API data received successfully.")

        # The API returns a list of data points. We need to find the ones we want.
        results = api_data.get("Results", [])
        
        processed_data = {}
        for item in results:
            if item.get("key") == "Sales":
                processed_data['total_sales'] = item.get("value")
            elif item.get("key") == "AveragePrice":
                # The API returns the price without a '$', so we add it for display
                price_value = float(item.get("value", 0))
                processed_data['average_price'] = f"${price_value:,.0f}"
            elif item.get("key") == "NewListings":
                processed_data['new_listings'] = item.get("value")

        # The report period is also in the API response
        processed_data['report_period'] = api_data.get("ReportPeriod", "Latest Report")

        if not processed_data:
            print("ERROR: Could not find key metrics in the CREA API response.")
            return jsonify({"error": "Could not parse data from CREA API."}), 500

        return jsonify(processed_data)

    except Exception as e:
        print(f"CRITICAL: An exception occurred in get_crea_data: {e}")
        return jsonify({"error": "Failed to fetch or process CREA API data."}), 500

# The dummy CMHC data for reliability
@market_analysis_bp.route('/cmhc-rental-market', methods=['GET'])
def get_cmhc_data():
    print("INFO: Returning dummy data for CMHC.")
    dummy_data = {
        "windsor": { "vacancy_rate_pct": 2.5, "avg_rent_total": 1350 },
        "ontario": { "vacancy_rate_pct": 1.8, "avg_rent_total": 1750 }
    }
    return jsonify(dummy_data)
