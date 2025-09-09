from flask import Blueprint, jsonify
import pandas as pd
import requests
import io
import pdfplumber
import re

market_analysis_bp = Blueprint('market_analysis_bp', __name__)

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- CMHC Data Processing ---
@market_analysis_bp.route('/cmhc-rental-market', methods=['GET'])
def get_cmhc_data():
    # This is a more stable landing page URL
    landing_url = "https://www.cmhc-schl.gc.ca/en/professionals/housing-markets-data-and-research/housing-data/data-tables/rental-market/rental-market-report-data-tables"
    try:
        print("INFO: Fetching CMHC landing page..." )
        response = requests.get(landing_url, headers=REQUEST_HEADERS, timeout=20)
        response.raise_for_status()
        print("INFO: CMHC landing page fetched.")

        # Find the latest .xlsx file link on the page
        match = re.search(r'href="([^"]+rental-market-data-2023\.xlsx)"', response.text)
        if not match:
            print("ERROR: Could not find the CMHC Excel file link on the landing page.")
            return jsonify({"error": "Could not find CMHC data file link."}), 404
        
        file_url = match.group(1)
        if not file_url.startswith('http' ):
            file_url = "https://www.cmhc-schl.gc.ca" + file_url

        print(f"INFO: Found CMHC file URL: {file_url}" )
        file_response = requests.get(file_url, headers=REQUEST_HEADERS, timeout=20)
        file_response.raise_for_status()
        
        df = pd.read_excel(io.BytesIO(file_response.content), sheet_name='2023')
        df.columns = df.columns.str.strip()
        
        # (Rest of the processing logic is the same)
        windsor_row = df[df.iloc[:, 0].str.contains('Windsor', na=False)].iloc[0]
        ontario_row = df[df.iloc[:, 0].str.contains('Ontario', na=False)].iloc[0]
        data = {
            'windsor': {'vacancy_rate_pct': windsor_row.get('Vacancy Rate (%)'), 'avg_rent_total': windsor_row.get('Total')},
            'ontario': {'vacancy_rate_pct': ontario_row.get('Vacancy Rate (%)'), 'avg_rent_total': ontario_row.get('Total')}
        }
        return jsonify(data)

    except Exception as e:
        print(f"CRITICAL: An exception occurred in get_cmhc_data: {e}")
        return jsonify({"error": str(e)}), 500

# --- WECAR Data Processing ---
@market_analysis_bp.route('/wecar-sales', methods=['GET'])
def get_wecar_data():
    # Corrected URL for market updates
    stats_page_url = "https://windsorrealestate.com/news/category/market-updates/"
    try:
        print("INFO: Fetching WECAR page..." )
        response = requests.get(stats_page_url, headers=REQUEST_HEADERS, timeout=20)
        response.raise_for_status()
        print("INFO: WECAR page fetched successfully.")
        
        match = re.search(r'href="(https?://windsorrealestate\.com/wp-content/uploads/[^"]+\.pdf )"', response.text)
        if not match:
            print("ERROR: Could not find a PDF link on the WECAR market updates page.")
            return jsonify({"error": "Could not find the latest WECAR report PDF link."}), 404
            
        pdf_url = match.group(1)
        print(f"INFO: Found WECAR PDF URL: {pdf_url}")
        
        pdf_response = requests.get(pdf_url, headers=REQUEST_HEADERS, timeout=20)
        pdf_response.raise_for_status()
        
        with io.BytesIO(pdf_response.content) as pdf_file:
            # (Parsing logic is the same)
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
            data = {}
            # ... (rest of parsing logic)
            return jsonify({"report_period": "Latest", "average_price": "$550,000 (dummy)", "total_sales": "500 (dummy)"}) # Dummy data for now

    except Exception as e:
        print(f"CRITICAL: An exception occurred in get_wecar_data: {e}")
        return jsonify({"error": f"Failed to fetch or process WECAR PDF: {str(e)}"}), 500

# --- Statistics Canada Data Processing ---
@market_analysis_bp.route('/statcan-housing-starts', methods=['GET'])
def get_statcan_data():
    # This is a dummy implementation because the StatCan site is very difficult to scrape reliably.
    # In a real project, we would use their official API or a saved data file.
    print("INFO: Returning dummy data for StatCan.")
    dummy_data = [
        {"date": "2023-01", "windsor_starts": 50, "ontario_starts": 5000},
        {"date": "2023-02", "windsor_starts": 60, "ontario_starts": 5500},
        {"date": "2023-03", "windsor_starts": 70, "ontario_starts": 6000},
    ]
    return jsonify(dummy_data)
