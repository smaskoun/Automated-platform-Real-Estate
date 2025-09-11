from flask import Blueprint, jsonify, current_app, send_file
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import os
import time
import logging
from functools import wraps

# --- PDF Generation Imports ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for servers
import matplotlib.pyplot as plt
import io

# --- Blueprint and Configuration ---
market_analysis_bp = Blueprint('market_analysis_bp', __name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- In-Memory Cache ---
cache = {}
CACHE_DURATION = 3600  # Cache duration in seconds (1 hour)

def cache_result(duration=CACHE_DURATION):
    """Decorator to cache the result of a function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < duration:
                    logging.info(f"Cache HIT for key: {cache_key}")
                    return result
                else:
                    logging.info(f"Cache EXPIRED for key: {cache_key}")
                    del cache[cache_key]
            
            logging.info(f"Cache MISS for key: {cache_key}")
            result = func(*args, **kwargs)
            if result and "error" not in result:
                cache[cache_key] = (result, time.time())
                logging.info(f"Cached new result for key: {cache_key}")
            return result
        return wrapper
    return decorator

# --- Sample Data ---
def get_sample_data():
    """Loads sample market data from a JSON file."""
    try:
        # --- THIS IS THE ONLY LINE THAT HAS BEEN CHANGED ---
        # It now looks for sample_data.json in the same directory as the running script.
        sample_data_path = os.path.join(os.path.dirname(__file__), '..', 'sample_data.json')
        
        with open(sample_data_path, 'r') as f:
            data = json.load(f)
            data['source'] = 'Sample Data'
            data['note'] = 'Live data could not be fetched. This is sample data.'
            return data
    except Exception as e:
        logging.critical(f"Failed to load sample_data.json from path {os.path.abspath(sample_data_path)}. Error: {e}")
        return {"error": "Sample data unavailable.", "status": 503}

# --- Data Fetching Logic ---
@cache_result()
def fetch_latest_wecar_data():
    """
    Fetches the latest available market report from WECAR.
    Tries the last 4 months and falls back to sample data.
    """
    base_url = "https://wecartech.com/wecfiles/stats_new"
    headers = {'User-Agent': 'Mozilla/5.0'}
    today = datetime.now( )

    for i in range(4): # Try current month and 3 previous months
        target_date = today - relativedelta(months=i)
        year = target_date.year
        month_short = target_date.strftime('%b').lower()
        url = f"{base_url}/{year}/{month_short}/summary.json"
        
        logging.info(f"Attempting to fetch data from: {url}")
        try:
            # Removed the inner retry loop for simplicity, the main loop handles retrying months.
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            logging.info(f"Successfully fetched data for {month_short.capitalize()} {year}.")
            data = response.json()
            data['source'] = 'WECAR Live'
            data['period'] = f"{month_short.capitalize()} {year}"
            return data
        except requests.exceptions.RequestException as e:
            logging.warning(f"Failed to fetch data from {url}. Reason: {e}")
            # Continue to the next month
    
    logging.error("All attempts to fetch live WECAR data failed. Using fallback.")
    return get_sample_data()

# --- Chart Generation ---
def create_chart_image(data, title):
    """Creates a bar chart image from data using Matplotlib."""
    try:
        labels = list(data.keys())
        values = list(data.values())
        
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(labels, values, color='#3b82f6')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('Number of Sales')
        ax.tick_params(axis='x', rotation=45, labelsize=10)
        
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom', ha='center')

        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        plt.close(fig)
        buf.seek(0)
        return buf
    except Exception as e:
        logging.error(f"Error creating chart image: {e}")
        return None

# --- PDF Generation ---
def generate_pdf_report(data):
    """Generates a PDF report from the market data."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Windsor-Essex Real Estate Market Report", styles['h1']))
    story.append(Spacer(1, 0.25 * inch))

    source_note = data.get('note', f"Data from {data.get('source', 'N/A')}")
    story.append(Paragraph(f"<b>Period:</b> {data.get('period', 'N/A')}", styles['Normal']))
    story.append(Paragraph(f"<b>Source:</b> {source_note}", styles['Normal']))
    story.append(Spacer(1, 0.25 * inch))

    metrics = data.get('stats', {}).get('latest', {})
    table_data = [
        ['Metric', 'Value'],
        ['Total Sales', f"{metrics.get('total_sales', 0):,}"],
        ['Average Price', f"${metrics.get('average_price', 0):,}"],
        ['Listings', f"{metrics.get('new_listings', 0):,}"],
    ]
    table = Table(table_data, colWidths=[2.5 * inch, 2.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 0.25 * inch))

    property_types = data.get('stats', {}).get('property_type_distribution', {})
    if property_types:
        story.append(Paragraph("Sales by Property Type", styles['h2']))
        chart_image = create_chart_image(property_types, "Property Type Distribution")
        if chart_image:
            story.append(Image(chart_image, width=6*inch, height=3.75*inch))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- API Endpoints ---
@market_analysis_bp.route('/market-analysis', methods=['GET'])
def get_market_analysis():
    """Endpoint to get market analysis data (live or sample)."""
    data = fetch_latest_wecar_data()
    if "error" in data:
        return jsonify(data), data.get("status", 500)
    return jsonify(data)

@market_analysis_bp.route('/download-report', methods=['GET'])
def download_report():
    """Endpoint to generate and download a PDF report."""
    data = fetch_latest_wecar_data()
    if "error" in data:
        return jsonify({"error": "Could not generate report, data unavailable."}), 503

    pdf_buffer = generate_pdf_report(data)
    if not pdf_buffer:
        return jsonify({"error": "Failed to generate PDF."}), 500

    filename = f"Market_Report_{data.get('period', 'latest').replace(' ', '_')}.pdf"
    return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

@market_analysis_bp.route('/cache/status', methods=['GET'])
def get_cache_status():
    """Endpoint to check the status of the in-memory cache."""
    return jsonify({
        "cache_entries": len(cache),
        "keys": list(cache.keys()),
        "cache_duration_seconds": CACHE_DURATION
    })

@market_analysis_bp.route('/cache/clear', methods=['POST'])
def clear_all_cache():
    """Endpoint to manually clear the cache."""
    count = len(cache)
    cache.clear()
    logging.info("Cache cleared manually.")
    return jsonify({"message": f"Cache cleared successfully. {count} items removed."})
