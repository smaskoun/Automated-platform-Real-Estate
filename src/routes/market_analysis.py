from flask import Blueprint, jsonify
import pandas as pd
import requests
import io
import re
from bs4 import BeautifulSoup # We need a new library for parsing HTML

market_analysis_bp = Blueprint('market_analysis_bp', __name__)

# Define a browser-like header to avoid being blocked
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- CMHC Data Processing (More Robust) ---
@market_analysis_bp.route('/cmhc-rental-market', methods=['GET'])
def get_cmhc_data():
    try:
        print("INFO: Fetching CMHC data...")
        # This is a more stable URL to the main data page
        cmhc_page_url = "https://www.cmhc-schl.gc.ca/en/professionals/housing-markets-data-and-research/housing-data/data-tables/rental-market/rental-market-report-data-tables"
        page_response = requests.get(cmhc_page_url, headers=REQUEST_HEADERS, timeout=20 )
        page_response.raise_for_status()

        # Find the link to the most recent Excel file on the page
        soup = BeautifulSoup(page_response.content, 'html.parser')
        excel_link = soup.find('a', href=re.compile(r'\.xlsx$', re.IGNORECASE))
        
        if not excel_link:
            print("ERROR: Could not find the CMHC Excel file link on the page.")
            return jsonify({"error": "Could not find CMHC data file link."}), 404

        file_url = excel_link['href']
        if not file_url.startswith('http' ):
            # Handle relative URLs if necessary
            from urllib.parse import urljoin
            file_url = urljoin(cmhc_page_url, file_url)

        print(f"INFO: Found CMHC file URL: {file_url}")
        file_response = requests.get(file_url, headers=REQUEST_HEADERS, timeout=20)
        file_response.raise_for_status()
        
        # Use the first sheet as it's usually the most recent summary
        df = pd.read_excel(io.BytesIO(file_response.content), sheet_name=0)
        df.columns = df.columns.str.strip()
        
        windsor_row = df[df.iloc[:, 0].str.contains('Windsor', na=False)].iloc[0]
        ontario_row = df[df.iloc[:, 0].str.contains('Ontario', na=False)].iloc[0]
        
        data = {
            'windsor': { 'vacancy_rate_pct': windsor_row.get('Vacancy Rate (%)'), 'avg_rent_total': windsor_row.get('Total') },
            'ontario': { 'vacancy_rate_pct': ontario_row.get('Vacancy Rate (%)'), 'avg_rent_total': ontario_row.get('Total') }
        }
        return jsonify(data)

    except Exception as e:
        print(f"CRITICAL: An exception occurred in get_cmhc_data: {e}")
        return jsonify({"error": "Failed to fetch or process CMHC data."}), 500

# --- Jump Realty Data Processing ---
def parse_jumprealty_text(text):
    data = {}
    avg_price_match = re.search(r'average sales price.*?was (\$[\d,]+)', text, re.IGNORECASE)
    if avg_price_match: data['average_price'] = avg_price_match.group(1)
    sales_match = re.search(r'(\d+)\s+homes were sold', text, re.IGNORECASE)
    if sales_match: data['total_sales'] = sales_match.group(1)
    listings_match = re.search(r'(\d+)\s+new listings', text, re.IGNORECASE)
    if not listings_match: listings_match = re.search(r'(\d+)\s+listings were available', text, re.IGNORECASE)
    if listings_match: data['new_listings'] = listings_match.group(1)
    return data if data else None

@market_analysis_bp.route('/jumprealty-stats', methods=['GET'])
def get_jumprealty_data():
    try:
        print("INFO: Fetching Jump Realty market updates page...")
        updates_page_url = "https://jumprealty.ca/blog/category/market-reports"
        response = requests.get(updates_page_url, headers=REQUEST_HEADERS, timeout=20 )
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        latest_post_link = soup.find('h2', class_='entry-title').find('a')

        if not latest_post_link or not latest_post_link.has_attr('href'):
            return jsonify({"error": "Could not find latest Jump Realty post."}), 404
        
        post_url = latest_post_link['href']
        print(f"INFO: Found latest post URL: {post_url}")

        post_response = requests.get(post_url, headers=REQUEST_HEADERS, timeout=20)
        post_response.raise_for_status()

        post_soup = BeautifulSoup(post_response.content, 'html.parser')
        post_content = post_soup.find('div', class_='entry-content').get_text()

        data = parse_jumprealty_text(post_content)
        
        if data:
            data['report_period'] = latest_post_link.get_text()
            return jsonify(data)
        else:
            return jsonify({"error": "Could not parse data from Jump Realty post."}), 500

    except Exception as e:
        print(f"CRITICAL: An exception occurred in get_jumprealty_data: {e}")
        return jsonify({"error": "Failed to fetch or process Jump Realty data."}), 500
