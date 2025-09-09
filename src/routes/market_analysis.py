from flask import Blueprint, jsonify
import requests
from bs4 import BeautifulSoup
import os

market_analysis_bp = Blueprint('market_analysis_bp', __name__)

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- CREA Data Processing ---
@market_analysis_bp.route('/crea-stats', methods=['GET'])
def get_crea_data():
    crea_url = "https://stats.crea.ca/board/wind"
    try:
        print(f"INFO: Fetching CREA data from {crea_url}" )
        response = requests.get(crea_url, headers=REQUEST_HEADERS, timeout=20)
        response.raise_for_status()
        print("INFO: CREA data fetched successfully.")

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main statistics table
        table = soup.find('table')
        if not table:
            print("ERROR: Could not find the data table on the CREA page.")
            return jsonify({"error": "Could not find data table on CREa page."}), 404

        # Extract data from the table rows
        data = {}
        rows = table.find_all('tr')
        
        # The data we want is usually in the first few rows.
        # This is specific to the page's structure as of Sept 2025.
        # Example: Find the row for "Sales" and get its value
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 1:
                metric_name = cells[0].get_text(strip=True)
                metric_value = cells[1].get_text(strip=True)
                
                if 'Sales' in metric_name:
                    data['total_sales'] = metric_value
                elif 'Average Price' in metric_name:
                    data['average_price'] = metric_value
                elif 'New Listings' in metric_name:
                    data['new_listings'] = metric_value
        
        # Get the report period from the page title or a header
        report_period_header = soup.find('h1')
        if report_period_header:
            data['report_period'] = report_period_header.get_text(strip=True)
        else:
            data['report_period'] = "Latest Report"

        if not data:
            print("ERROR: Could not parse key metrics from the CREA table.")
            return jsonify({"error": "Could not parse data from CREA table."}), 500

        return jsonify(data)

    except Exception as e:
        print(f"CRITICAL: An exception occurred in get_crea_data: {e}")
        return jsonify({"error": "Failed to fetch or process CREA data."}), 500

# We will keep the CMHC route but use dummy data for max reliability
@market_analysis_bp.route('/cmhc-rental-market', methods=['GET'])
def get_cmhc_data():
    print("INFO: Returning dummy data for CMHC.")
    dummy_data = {
        "windsor": { "vacancy_rate_pct": 2.5, "avg_rent_total": 1350 },
        "ontario": { "vacancy_rate_pct": 1.8, "avg_rent_total": 1750 }
    }
    return jsonify(dummy_data)
