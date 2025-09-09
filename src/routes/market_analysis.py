from flask import Blueprint, jsonify, request
import pandas as pd
import requests
import io
import pdfplumber
from datetime import datetime

market_analysis_bp = Blueprint('market_analysis_bp', __name__)

# --- CMHC Data Processing ---
def process_cmhc_data(df):
    """Extracts and formats CMHC rental market data."""
    try:
        # Find the rows for Windsor and Ontario
        windsor_row = df[df.iloc[:, 0].str.contains('Windsor', na=False)].iloc[0]
        ontario_row = df[df.iloc[:, 0].str.contains('Ontario', na=False)].iloc[0]

        data = {
            'windsor': {
                'vacancy_rate_pct': windsor_row.get('Vacancy Rate (%)'),
                'avg_rent_bachelor': windsor_row.get('Bachelor'),
                'avg_rent_1_bedroom': windsor_row.get('1 Bedroom'),
                'avg_rent_2_bedroom': windsor_row.get('2 Bedroom'),
                'avg_rent_3_bedroom_plus': windsor_row.get('3 Bedroom +'),
                'avg_rent_total': windsor_row.get('Total')
            },
            'ontario': {
                'vacancy_rate_pct': ontario_row.get('Vacancy Rate (%)'),
                'avg_rent_bachelor': ontario_row.get('Bachelor'),
                'avg_rent_1_bedroom': ontario_row.get('1 Bedroom'),
                'avg_rent_2_bedroom': ontario_row.get('2 Bedroom'),
                'avg_rent_3_bedroom_plus': ontario_row.get('3 Bedroom +'),
                'avg_rent_total': ontario_row.get('Total')
            }
        }
        return data
    except (IndexError, KeyError) as e:
        print(f"Error processing CMHC data: {e}")
        return None

@market_analysis_bp.route('/cmhc-rental-market', methods=['GET'])
def get_cmhc_data():
    """API endpoint to fetch and process CMHC rental market data."""
    # URL to the 2023 CMHC Rental Market Report data
    url = "https://assets.cmhc-schl.gc.ca/sites/place-to-call-home/pdfs/data-tables/rental-market-report/2023/rental-market-data-2023.xlsx"
    try:
        response = requests.get(url )
        response.raise_for_status()
        
        # Read the '2023' sheet from the Excel file
        df = pd.read_excel(io.BytesIO(response.content), sheet_name='2023')
        
        # Clean up column names by stripping whitespace
        df.columns = df.columns.str.strip()

        data = process_cmhc_data(df)

        if data:
            return jsonify(data)
        else:
            return jsonify({"error": "Could not find or process data for Windsor or Ontario."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Statistics Canada Data Processing ---
@market_analysis_bp.route('/statcan-housing-starts', methods=['GET'])
def get_statcan_data():
    """API endpoint for Statistics Canada housing starts data."""
    # Table 34-10-0135-01: Housing starts, under construction, and completions
    url = "https://www150.statcan.gc.ca/t1/tbl1/en/dtl!downloadDb-csv.jsp?pid=3410013501&lang=en"
    try:
        response = requests.get(url )
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.text))
        
        # Filter for relevant data
        df_filtered = df[
            (df['GEO'].isin(['Windsor, Ontario', 'Ontario'])) &
            (df['Housing estimates'] == 'Housing starts') &
            (df['UOM'] == 'Units')
        ]
        
        # Pivot the data for easier consumption
        pivot_df = df_filtered.pivot_table(index='REF_DATE', columns='GEO', values='VALUE', aggfunc='sum').reset_index()
        pivot_df.rename(columns={'REF_DATE': 'date', 'Windsor, Ontario': 'windsor_starts', 'Ontario': 'ontario_starts'}, inplace=True)
        
        # Convert to JSON
        data = pivot_df.to_dict(orient='records')
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- WECAR Data Processing ---
def parse_wecar_pdf(pdf_file):
    """Extracts key metrics from a WECAR PDF report."""
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    data = {}
    lines = text.split('\n')
    
    # Find report date
    for line in lines:
        if "Windsor-Essex County" in line and any(month in line for month in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]):
            data['report_period'] = line.strip()
            break

    # Extract metrics
    for i, line in enumerate(lines):
        if "Average Price" in line:
            # The value is often on the same line or the next one
            parts = line.split()
            for part in parts:
                if '$' in part:
                    data['average_price'] = part
                    break
        if "Sales" in line and "Residential" in lines[i-1]: # More specific matching
             parts = line.split()
             if len(parts) > 1:
                data['total_sales'] = parts[1]
        if "New Listings" in line:
             parts = line.split()
             if len(parts) > 2:
                data['new_listings'] = parts[2]

    return data

@market_analysis_bp.route('/wecar-sales', methods=['GET'])
def get_wecar_data():
    """API endpoint to scrape and parse WECAR sales data from PDF."""
    # This is a simplified example. A real implementation would need to find the latest PDF link dynamically.
    # For now, we use a known recent URL.
    pdf_url = "https://windsorrealestate.com/wp-content/uploads/2024/05/May-2024-Stats-Package.pdf" # Example URL
    try:
        response = requests.get(pdf_url )
        response.raise_for_status()
        
        with io.BytesIO(response.content) as pdf_file:
            data = parse_wecar_pdf(pdf_file)

        if not data:
            return jsonify({"error": "Could not parse data from WECAR PDF. The format may have changed."}), 404
            
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch or process WECAR PDF: {str(e)}"}), 500

