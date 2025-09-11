from flask import Blueprint, jsonify, current_app, send_file, request
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY
import json
import os
import time
import logging
from functools import wraps
import pandas as pd

# --- PDF Generation Imports ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

# --- Blueprint and Configuration ---
market_analysis_bp = Blueprint('market_analysis_bp', __name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- In-Memory Cache ---
cache = {}
CACHE_DURATION = 3600

def cache_result(duration=CACHE_DURATION):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            path = request.path
            args_str = str(sorted(request.args.items()))
            cache_key = f"{path}?{args_str}"
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
            if isinstance(result, tuple) and result[1] == 200:
                 cache[cache_key] = (result, time.time())
            elif isinstance(result, jsonify):
                 cache[cache_key] = (result, time.time())
            return result
        return wrapper
    return decorator

# --- Sample Data ---
def get_sample_data():
    try:
        project_root = current_app.root_path 
        sample_data_path = os.path.join(project_root, 'data', 'market_report_sample.json')
        with open(sample_data_path, 'r') as f:
            data = json.load(f)
            data['source'] = 'Sample Data'
            data['note'] = 'Live data could not be fetched. This is sample data.'
            return data
    except Exception as e:
        abs_path = os.path.abspath(sample_data_path)
        logging.critical(f"Failed to load sample_data.json. Attempted path: {abs_path}. Error: {e}")
        return {"error": "Sample data unavailable.", "status": 503}

# --- Data Fetching Logic ---
def fetch_wecar_data_for_month(target_date):
    base_url = "https://wecartech.com/wecfiles/stats_new"
    headers = {'User-Agent': 'Mozilla/5.0'}
    year = target_date.year
    month_short = target_date.strftime('%b' ).lower()
    url = f"{base_url}/{year}/{month_short}/"
    
    logging.info(f"Attempting to fetch data from directory: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logging.info(f"Successfully fetched data for {month_short.capitalize()} {year}.")
        data = response.json()
        data['source'] = 'WECAR Live'
        data['period'] = f"{month_short.capitalize()} {year}"
        return data
    except requests.exceptions.RequestException as e:
        logging.warning(f"Failed to fetch data from {url}. Reason: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Response from {url} was not valid JSON. Reason: {e}")
        return None

# --- THIS IS THE NEW, SMARTER LOGIC ---
def fetch_latest_wecar_data():
    """
    Fetches the latest available data based on the day of the month.
    """
    today = datetime.now()
    
    # If it's after the 10th, we know the previous month's data is the most recent.
    # Start searching from the previous month.
    if today.day > 10:
        start_month_offset = 1
        logging.info("Day is after 10th, starting search from previous month.")
    # If it's early in the month, the previous month's data might just have been released.
    # Start searching from the previous month, but be prepared to go back further.
    else:
        start_month_offset = 1
        logging.info("Day is before 10th, starting search from previous month (most likely target).")

    # Try the last 3 relevant months (e.g., previous, 2 months ago, 3 months ago)
    for i in range(3):
        target_date = today - relativedelta(months=start_month_offset + i)
        data = fetch_wecar_data_for_month(target_date)
        if data:
            return data
    
    logging.error("All attempts to fetch live WECAR data failed. Using fallback.")
    return get_sample_data()

# --- PDF Generation (remains unchanged) ---
def create_chart_image(data, title):
    labels = [item['name'] for item in data]
    values = [item['sales'] for item in data]
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

def generate_pdf_report(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("Windsor-Essex Real Estate Market Report", styles['h1']))
    story.append(Spacer(1, 0.25 * inch))
    source_note = data.get('note', f"Data from {data.get('source', 'N/A')}")
    story.append(Paragraph(f"<b>Period:</b> {data.get('report_period', 'N/A')}", styles['Normal']))
    story.append(Paragraph(f"<b>Source:</b> {source_note}", styles['Normal']))
    story.append(Spacer(1, 0.25 * inch))
    metrics = data.get('key_metrics', {})
    table_data = [['Metric', 'Value'], ['Total Sales', f"{metrics.get('total_sales', 0):,}"], ['Average Price', f"${metrics.get('average_price', 0):,}"], ['Listings', f"{metrics.get('new_listings', 0):,}"],]
    table = Table(table_data, colWidths=[2.5 * inch, 2.5 * inch])
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('BOTTOMPADDING', (0, 0), (-1, 0), 12), ('BACKGROUND', (0, 1), (-1, -1), colors.beige), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    story.append(table)
    story.append(Spacer(1, 0.25 * inch))
    property_types = data.get('sales_by_type', [])
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
    data = fetch_latest_wecar_data()
    if "error" in data:
        return jsonify(data), data.get("status", 500)
    return jsonify(data)

@market_analysis_bp.route('/historical', methods=['GET'])
@cache_result()
def get_historical_data():
    start_str = request.args.get('start_date')
    end_str = request.args.get('end_date')
    if not start_str or not end_str:
        return jsonify({"error": "Please provide both 'start_date' and 'end_date' in YYYY-MM format."}), 400
    try:
        start_date = datetime.strptime(start_str, '%Y-%m')
        end_date = datetime.strptime(end_str, '%Y-%m')
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM."}), 400
    monthly_data = []
    successful_months = []
    failed_months = []
    for dt in rrule(MONTHLY, dtstart=start_date, until=end_date):
        month_str = dt.strftime('%Y-%m')
        data = fetch_wecar_data_for_month(dt)
        if data:
            monthly_data.append(data)
            successful_months.append(month_str)
        else:
            failed_months.append(month_str)
    if not monthly_data:
        return jsonify({"error": "No data found for the selected period.", "successful_months": [], "failed_months": failed_months}), 404
    df = pd.json_normalize(monthly_data, record_path='sales_by_type', meta=[['key_metrics', 'total_sales'], ['key_metrics', 'average_price'], ['key_metrics', 'new_listings']])
    total_sales = df['key_metrics.total_sales'].sum()
    total_listings = df['key_metrics.new_listings'].sum()
    weighted_avg_price = (df['key_metrics.average_price'] * df['key_metrics.total_sales']).sum() / total_sales if total_sales > 0 else 0
    sales_by_type_agg = df.groupby('name')['sales'].sum().reset_index().to_dict('records')
    aggregated_result = {"report_period": f"{start_str} to {end_str}", "source": "WECAR Live (Aggregated)", "key_metrics": {"total_sales": int(total_sales), "average_price": int(weighted_avg_price), "new_listings": int(total_listings),}, "sales_by_type": sales_by_type_agg, "monthly_breakdown": monthly_data, "successful_months": successful_months, "failed_months": failed_months}
    return jsonify(aggregated_result), 200

@market_analysis_bp.route('/download-report', methods=['GET'])
def download_report():
    data = fetch_latest_wecar_data()
    if "error" in data:
        return jsonify({"error": "Could not generate report, data unavailable."}), 503
    pdf_buffer = generate_pdf_report(data)
    if not pdf_buffer:
        return jsonify({"error": "Failed to generate PDF."}), 500
    filename = f"Market_Report_{data.get('report_period', 'latest').replace(' ', '_')}.pdf"
    return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

@market_analysis_bp.route('/cache/status', methods=['GET'])
def get_cache_status():
    return jsonify({"cache_entries": len(cache), "keys": list(cache.keys()), "cache_duration_seconds": CACHE_DURATION})

@market_analysis_bp.route('/cache/clear', methods=['POST'])
def clear_all_cache():
    count = len(cache)
    cache.clear()
    logging.info("Cache cleared manually.")
    return jsonify({"message": f"Cache cleared successfully. {count} items removed."})
