from flask import Blueprint, jsonify
import pandas as pd
import requests
import io
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

market_analysis_bp = Blueprint('market_analysis_bp', __name__)

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- CMHC Data Processing (Final, Most Robust Version) ---
@market_analysis_bp.route('/cmhc-rental-market', methods=['GET'])
def get_cmhc_data():
    try:
        print("INFO: Fetching CMHC main data page...")
        # A very stable, high-level URL
        cmhc_page_url = "https://www.cmhc-schl.gc.ca/en/professionals/housing-markets-data-and-research/housing-data"
        page_response = requests.get(cmhc_page_url, headers=REQUEST_HEADERS, timeout=25 )
        page_response.raise_for_status()

        soup = BeautifulSoup(page_response.content, 'html.parser')
        # Find a link that specifically mentions "Rental Market Report data tables"
        data_page_link = soup.find('a', text=re.compile(r'Rental Market Report data tables', re.IGNORECASE))
        
        if not data_page_link or not data_page_link.has_attr('href'):
             print("ERROR: Could not find link to the specific data tables page.")
             return jsonify({"error": "Could not find link to CMHC data tables page."}), 404

        data_page_url = urljoin(cmhc_page_url, data_page_link['href'])
        print(f"INFO: Found data page URL: {data_page_url}")
        
        data_page_response = requests.get(data_page_url, headers=REQUEST_HEADERS, timeout=25)
        data_page_response.raise_for_status()

        soup = BeautifulSoup(data_page_response.content, 'html.parser')
        excel_link = soup.find('a', href=re.compile(r'\.xlsx$', re.IGNORECASE))
        
        if not excel_link:
            print("ERROR: Could not find the CMHC Excel file link on the final data page.")
            return jsonify({"error": "Could not find CMHC Excel file link."}), 404

        file_url = urljoin(data_page_url, excel_link['href'])
        print(f"INFO: Found final CMHC file URL: {file_url}")

        file_response = requests.get(file_url, headers=REQUEST_HEADERS, timeout=25)
        file_response.raise_for_status()
        
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

# --- Jump Realty Data Processing (Final, Most Robust Version) ---
@market_analysis_bp.route('/jumprealty-stats', methods=['GET'])
def get_jumprealty_data():
    try:
        print("INFO: Fetching Jump Realty blog page...")
        # The URL was missing the www.
        updates_page_url = "https://www.jumprealty.ca/blog/category/market-reports"
        response = requests.get(updates_page_url, headers=REQUEST_HEADERS, timeout=25 )
        response.raise_for_status()
        print("INFO: Jump Realty page fetched successfully.")

        soup = BeautifulSoup(response.content, 'html.parser')
        latest_post_link = soup.find('h2', class_='entry-title').find('a')

        if not latest_post_link or not latest_post_link.has_attr('href'):
            return jsonify({"error": "Could not find latest Jump Realty post link."}), 404
        
        post_url = latest_post_link['href']
        print(f"INFO: Found latest post URL: {post_url}")

        post_response = requests.get(post_url, headers=REQUEST_HEADERS, timeout=25)
        post_response.raise_for_status()

        post_soup = BeautifulSoup(post_response.content, 'html.parser')
        # Use a more generic class that is less likely to change
        post_content_div = post_soup.find('div', class_='td-post-content')
        if not post_content_div:
             post_content_div = post_soup.find('div', class_='entry-content') # Fallback
        
        post_text = post_content_div.get_text()

        data = {}
        avg_price_match = re.search(r'average sales price.*?(\$[\d,]+)', post_text, re.IGNORECASE)
        if avg_price_match: data['average_price'] = avg_price_match.group(1)
        sales_match = re.search(r'(\d+)\s+homes sold', post_text, re.IGNORECASE)
        if sales_match: data['total_sales'] = sales_match.group(1)
        listings_match = re.search(r'(\d+)\s+new listings', post_text, re.IGNORECASE)
        if listings_match: data['new_listings'] = listings_match.group(1)
        
        if data:
            data['report_period'] = latest_post_link.get_text()
            return jsonify(data)
        else:
            return jsonify({"error": "Could not parse data from Jump Realty post."}), 500

    except Exception as e:
        print(f"CRITICAL: An exception occurred in get_jumprealty_data: {e}")
        return jsonify({"error": "Failed to fetch or process Jump Realty data."}), 500
