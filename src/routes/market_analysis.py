from flask import Blueprint, jsonify
import pandas as pd
import requests
import io
import pdfplumber
import re # Import the regular expressions library

market_analysis_bp = Blueprint('market_analysis_bp', __name__)

# Define a browser-like header to avoid being blocked
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- CMHC Data Processing ---
def process_cmhc_data(df):
    try:
        windsor_row = df[df.iloc[:, 0].str.contains('Windsor', na=False)].iloc[0]
        ontario_row = df[df.iloc[:, 0].str.contains('Ontario', na=False)].iloc[0]
        data = {
            'windsor': {
                'vacancy_rate_pct': windsor_row.get('Vacancy Rate (%)'), 'avg_rent_bachelor': windsor_row.get('Bachelor'),
                'avg_rent_1_bedroom': windsor_row.get('1 Bedroom'), 'avg_rent_2_bedroom': windsor_row.get('2 Bedroom'),
                'avg_rent_3_bedroom_plus': windsor_row.get('3 Bedroom +'), 'avg_rent_total': windsor_row.get('Total')
            },
            'ontario': {
                'vacancy_rate_pct': ontario_row.get('Vacancy Rate (%)'), 'avg_rent_bachelor': ontario_row.get('Bachelor'),
                'avg_rent_1_bedroom': ontario_row.get('1 Bedroom'), 'avg_rent_2_bedroom': ontario_row.get('2 Bedroom'),
                'avg_rent_3_bedroom_plus': ontario_row.get('3 Bedroom +'), 'avg_rent_total': ontario_row.get('Total')
            }
        }
        return data
    except (IndexError, KeyError) as e:
        print(f"ERROR: Could not find required rows/columns in CMHC data. Details: {e}")
        return None

@market_analysis_bp.route('/cmhc-rental-market', methods=['GET'])
def get_cmhc_data():
    url = "https://assets.cmhc-schl.gc.ca/sites/place-to-call-home/pdfs/data-tables/rental-market-report/2023/rental-market-data-2023.xlsx"
    try:
        print("INFO: Fetching CMHC data..." )
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=15)
        response.raise_for_status()
        print("INFO: CMHC data fetched successfully.")
        
        df = pd.read_excel(io.BytesIO(response.content), sheet_name='2023')
        df.columns = df.columns.str.strip()
        
        data = process_cmhc_data(df)
        if data:
            return jsonify(data)
        else:
            return jsonify({"error": "Could not process CMHC data from the file."}), 500
    except Exception as e:
        print(f"CRITICAL: An exception occurred in get_cmhc_data: {e}")
        return jsonify({"error": str(e)}), 500

# --- Statistics Canada Data Processing ---
@market_analysis_bp.route('/statcan-housing-starts', methods=['GET'])
def get_statcan_data():
    url = "https://www150.statcan.gc.ca/t1/tbl1/en/dtl!downloadDb-csv.jsp?pid=3410013501&lang=en"
    try:
        print("INFO: Fetching StatCan data..." )
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=15)
        response.raise_for_status()
        print("INFO: StatCan data fetched successfully.")
        
        df = pd.read_csv(io.StringIO(response.text))
        df_filtered = df[
            (df['GEO'].isin(['Windsor, Ontario', 'Ontario'])) &
            (df['Housing estimates'].isin(['Housing starts', 'Housing completions', 'Housing under construction'])) &
            (df['UOM'] == 'Units')
        ]
        
        pivot_df = df_filtered.pivot_table(index='REF_DATE', columns=['GEO', 'Housing estimates'], values='VALUE', aggfunc='sum').reset_index()
        pivot_df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in pivot_df.columns.values]
        pivot_df.rename(columns={'REF_DATE_': 'date'}, inplace=True)
        
        data = pivot_df.to_dict(orient='records')
        return jsonify(data)
    except Exception as e:
        print(f"CRITICAL: An exception occurred in get_statcan_data: {e}")
        return jsonify({"error": str(e)}), 500

# --- WECAR Data Processing ---
def parse_wecar_pdf(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        data = {}
        lines = text.split('\n')
        for line in lines:
            if "Windsor-Essex County" in line and any(month in line for month in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]):
                data['report_period'] = line.strip()
            if "Average Price" in line:
                price_match = re.search(r'\$\d{1,3}(,\d{3})*', line)
                if price_match:
                    data['average_price'] = price_match.group(0)
            if "Sales" in line and "Residential" in lines[lines.index(line)-1]:
                parts = line.split()
                if len(parts) > 1 and parts[1].replace(',', '').isdigit():
                    data['total_sales'] = parts[1]
            if "New Listings" in line:
                parts = line.split()
                if len(parts) > 2 and parts[2].replace(',', '').isdigit():
                    data['new_listings'] = parts[2]
        return data if 'average_price' in data else None
    except Exception as e:
        print(f"ERROR: Failed to parse WECAR PDF content. Details: {e}")
        return None

@market_analysis_bp.route('/wecar-sales', methods=['GET'])
def get_wecar_data():
    try:
        print("INFO: Fetching WECAR page...")
        stats_page_url = "https://windsorrealestate.com/archives/"
        response = requests.get(stats_page_url, headers=REQUEST_HEADERS, timeout=15 )
        response.raise_for_status()
        print("INFO: WECAR page fetched successfully.")
        
        # Find the first PDF link on the page, which is usually the latest
        match = re.search(r'href="(https?://windsorrealestate\.com/wp-content/uploads/\d{4}/\d{2}/[^"]+\.pdf )"', response.text)
        if not match:
            print("ERROR: Could not find a PDF link on the WECAR archives page.")
            return jsonify({"error": "Could not find the latest WECAR report PDF link."}), 404
            
        pdf_url = match.group(1)
        print(f"INFO: Found WECAR PDF URL: {pdf_url}")
        
        pdf_response = requests.get(pdf_url, headers=REQUEST_HEADERS, timeout=15)
        pdf_response.raise_for_status()
        
        with io.BytesIO(pdf_response.content) as pdf_file:
            data = parse_wecar_pdf(pdf_file)

        if data:
            return jsonify(data)
        else:
            return jsonify({"error": "Could not parse data from WECAR PDF. The format may have changed."}), 500
    except Exception as e:
        print(f"CRITICAL: An exception occurred in get_wecar_data: {e}")
        return jsonify({"error": f"Failed to fetch or process WECAR PDF: {str(e)}"}), 500
