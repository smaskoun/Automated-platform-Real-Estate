from flask import Blueprint, jsonify, current_app, send_file, request, Response, has_request_context
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
from werkzeug.utils import secure_filename

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

# Cache decorator reused across endpoints to avoid redundant remote calls
def cache_result(duration=CACHE_DURATION):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if has_request_context():
                path = request.full_path.rstrip('?')
                cache_key = f"{request.method}:{path}"
            else:
                cache_key = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
            if cache_key in cache:
                cached_result, timestamp = cache[cache_key]
                if time.time() - timestamp < duration:
                    logging.info(f"Cache HIT for key: {cache_key}")
                    return cached_result
                logging.info(f"Cache EXPIRED for key: {cache_key}")
                del cache[cache_key]
            logging.info(f"Cache MISS for key: {cache_key}")
            result = func(*args, **kwargs)
            to_cache = None
            if isinstance(result, Response):
                to_cache = result
            elif isinstance(result, tuple) and isinstance(result[0], Response):
                to_cache = result
            if to_cache is not None:
                cache[cache_key] = (to_cache, time.time())
            return result
        return wrapper
    return decorator

# --- Sample Data ---
def get_sample_data():
    """Return bundled sample data for offline or failed lookups.

    The helper first tries to resolve the file relative to the Flask
    application's root path.  In some execution contexts (tests or one-off
    scripts) this may point at the project root instead of the ``src``
    directory where the file actually lives.  We therefore attempt a second
    resolution relative to this module if the first lookup fails.
    """

    possible_paths = []
    if current_app:
        project_root = current_app.root_path
        possible_paths.append(
            os.path.join(project_root, 'data', 'market_report_sample.json')
        )
    # Fallback: path relative to this file for environments where the app
    # root is the repository root rather than ``src``
    module_dir = os.path.dirname(__file__)
    possible_paths.append(
        os.path.join(module_dir, '..', 'data', 'market_report_sample.json')
    )

    for sample_data_path in possible_paths:
        try:
            with open(sample_data_path, 'r') as f:
                data = json.load(f)
                data['source'] = 'Sample Data'
                data['note'] = (
                    'Live data could not be fetched. This is sample data.'
                )
                return data
        except Exception as e:
            abs_path = os.path.abspath(sample_data_path)
            logging.warning(
                f"Failed to load sample_data.json. Attempted path: {abs_path}. Error: {e}"
            )

    return {"error": "Sample data unavailable.", "status": 503}

# --- Data Fetching Logic ---
def get_latest_available_month():
 codex/implement-get_latest_available_month-and-adjust-end_date-6171yg
    """Return a timestamp for the first day of the previous month at midnight.

    WECAR statistics are released with a one-month delay, so only months up to
    the start of the previous month are expected to have complete data. The
    helper normalises the current timestamp to the first of this month at
    midnight and then subtracts one month to obtain the last fully published
    period.

    Returns:
        datetime: naive ``datetime`` pointing to midnight on the first day of
        the latest month with complete statistics.

 codex/implement-get_latest_available_month-and-adjust-end_date-485sai
    """Return the first day of the previous month at midnight.

    WECAR statistics are released with a one-month delay, so only months up to
    the start of the previous month are expected to have complete data.  The
    helper normalises the current timestamp to the first of this month at
    midnight and then subtracts one month to obtain the last fully published
    period.

    """Return the first day of the previous month.

    The WECAR statistics are published monthly with a lag, so the most
    recent reliable data set corresponds to the previous month.  This helper
    normalises the current date to midnight on the first of the current month
    and then steps back one month, ensuring any time component is removed.
 main
 main
    """

    first_of_this_month = datetime.now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    return first_of_this_month - relativedelta(months=1)
 codex/implement-get_latest_available_month-and-adjust-end_date-6171yg

 codex/implement-get_latest_available_month-and-adjust-end_date-485sai

 codex/implement-get_latest_available_month-and-adjust-end_date-qq96x3

codex/implement-get_latest_available_month-and-adjust-end_date-ti3qe7
 main
 main
 main

def load_manual_data_for_month(target_date):
    """Load manually uploaded stats for the given month if available.

    Admins can upload ``summary.json`` or ``summary.csv`` files into the
    ``data/manual`` directory.  Files are named ``YYYY-MM.json`` or
    ``YYYY-MM.csv``.  CSV files are expected to contain columns ``name`` and
    ``sales`` with optional ``average_price`` and ``new_listings`` columns.
    """

    year_month = target_date.strftime('%Y-%m')
    base_dir = None
    if current_app:
        base_dir = os.path.join(current_app.root_path, 'data', 'manual')
    else:
        module_dir = os.path.dirname(__file__)
        base_dir = os.path.abspath(os.path.join(module_dir, '..', 'data', 'manual'))
    possible_files = [
        os.path.join(base_dir, f'{year_month}.json'),
        os.path.join(base_dir, f'{year_month}.csv'),
    ]
    for path in possible_files:
        if not os.path.exists(path):
            continue
        try:
            if path.endswith('.json'):
                with open(path, 'r') as f:
                    data = json.load(f)
            else:
                df = pd.read_csv(path)
                sales_by_type = (
                    df[['name', 'sales']].to_dict('records')
                    if {'name', 'sales'}.issubset(df.columns)
                    else []
                )
                total_sales = int(df.get('sales', pd.Series(dtype=float)).sum())
                weighted_avg_price = (
                    df.get('average_price', pd.Series(dtype=float))
                    .mul(df.get('sales', pd.Series(dtype=float)))
                    .sum()
                    / total_sales
                    if total_sales > 0
                    else 0
                )
                new_listings = int(df.get('new_listings', pd.Series(dtype=float)).sum())
                data = {
                    'key_metrics': {
                        'total_sales': total_sales,
                        'average_price': int(weighted_avg_price),
                        'new_listings': new_listings,
                    },
                    'sales_by_type': sales_by_type,
                }
            data['source'] = 'Manual Upload'
            data['period'] = target_date.strftime('%b %Y')
            return data
        except Exception as e:
            logging.warning(f"Failed to parse manual data {path}: {e}")
    return None
codex/implement-get_latest_available_month-and-adjust-end_date-6171yg

 codex/implement-get_latest_available_month-and-adjust-end_date-485sai

 codex/implement-get_latest_available_month-and-adjust-end_date-qq96x3


 main
 main
 main
 main

def fetch_wecar_data_for_month(target_date):
    manual = load_manual_data_for_month(target_date)
    if manual:
        return manual
    base_url = "https://wecartech.com/wecfiles/stats_new"
    headers = {'User-Agent': 'Mozilla/5.0'}
    year = target_date.year
    month_short = target_date.strftime('%b').lower()
    month_num = target_date.strftime('%m')
    urls = [
        f"{base_url}/{year}/{month_short}/summary.json",
        f"{base_url}/{year}/{month_num}/summary.json",
    ]
    for url in urls:
        logging.info(f"Attempting to fetch data from: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            logging.info(
                f"Successfully fetched and parsed JSON for {target_date.strftime('%b %Y')}"
            )
            data['source'] = 'WECAR Live'
            data['period'] = target_date.strftime('%b %Y')
            return data
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logging.warning(f"Failed to fetch data from {url}. Reason: {e}")

    # Attempt scraping when summary.json is missing
    attempted = list(urls)
    try:
        from src.services import wecar_scraper
        scraped = wecar_scraper.scrape_month(target_date)
        scraped['source'] = 'WECAR Live (scraped)'
        scraped['period'] = target_date.strftime('%b %Y')
        return scraped
    except Exception as e:
        page_url = f"{base_url}/{year}/{month_short}/"
        attempted.append(page_url)
        logging.warning(f"Scraping failed for {page_url}: {e}")
    return {"error": "missing", "attempted": attempted}

@cache_result()
def fetch_latest_wecar_data():
    latest_available = get_latest_available_month()
    logging.info("Searching for latest available WECAR data starting from %s", latest_available)
    for i in range(3):
        target_date = latest_available - relativedelta(months=i)
        data = fetch_wecar_data_for_month(target_date)
        if data and 'error' not in data:
            return data
    logging.error("All attempts to fetch live WECAR data failed. Using fallback.")
    sample = get_sample_data()
    sample.setdefault('note', 'Live market data unavailable.')
    sample['error'] = 'Market data unavailable'
    sample['status'] = 503
    return sample

# --- PDF Generation (unchanged) ---
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
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
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
    if 'error' in data:
        return jsonify(data), data.get('status', 500)
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
    if start_date > end_date:
        return jsonify({"error": "'start_date' must not be after 'end_date'."}), 400
    latest_available = get_latest_available_month()
    excluded_months = []
    if end_date > latest_available:
        excluded_months = [
            dt.strftime('%Y-%m')
            for dt in rrule(MONTHLY, dtstart=latest_available + relativedelta(months=1), until=end_date)
        ]
        end_date = latest_available
        end_str = end_date.strftime('%Y-%m')
    monthly_data = []
    successful_months = []
    failed_months = []
    for dt in rrule(MONTHLY, dtstart=start_date, until=end_date):
        month_str = dt.strftime('%Y-%m')
        data = fetch_wecar_data_for_month(dt)
        if data and 'error' not in data:
            monthly_data.append(data)
            successful_months.append(month_str)
        else:
            failed_months.append(month_str)
    if not monthly_data:
        message = "No live data found for the selected period."
        if excluded_months:
            message += " Recent months were excluded due to publication lag."
        sample = get_sample_data()
        return jsonify({
            "error": message,
            "successful_months": [],
            "failed_months": failed_months,
            "excluded_months": excluded_months,
            "sample": sample,
        }), 404
    try:
        df = pd.json_normalize(
            monthly_data,
            record_path='sales_by_type',
            meta=[
                ['key_metrics', 'total_sales'],
                ['key_metrics', 'average_price'],
                ['key_metrics', 'new_listings'],
            ],
        )
    except KeyError:
        df = pd.DataFrame()

    if df.empty:
        total_sales = sum(
            m.get('key_metrics', {}).get('total_sales', 0) for m in monthly_data
        )
        total_listings = sum(
            m.get('key_metrics', {}).get('new_listings', 0) for m in monthly_data
        )
        weighted_avg_price = (
            sum(
                m.get('key_metrics', {}).get('average_price', 0)
                * m.get('key_metrics', {}).get('total_sales', 0)
                for m in monthly_data
            )
            / total_sales
            if total_sales > 0
            else 0
        )
        sales_by_type_agg = []
    else:
        total_sales = df.get('key_metrics.total_sales', pd.Series(dtype=float)).sum()
        total_listings = df.get('key_metrics.new_listings', pd.Series(dtype=float)).sum()
        weighted_avg_price = (
            df.get('key_metrics.average_price', pd.Series(dtype=float))
            .mul(df.get('key_metrics.total_sales', pd.Series(dtype=float)))
            .sum()
            / total_sales
            if total_sales > 0
            else 0
        )
        if {'name', 'sales'}.issubset(df.columns):
            sales_by_type_agg = (
                df.groupby('name')['sales'].sum().reset_index().to_dict('records')
            )
        else:
            sales_by_type_agg = []
    aggregated_result = {
        "report_period": f"{start_str} to {end_str}",
        "source": "WECAR Live (Aggregated)",
        "key_metrics": {
            "total_sales": int(total_sales),
            "average_price": int(weighted_avg_price),
            "new_listings": int(total_listings),
        },
        "sales_by_type": sales_by_type_agg,
        "monthly_breakdown": monthly_data,
        "successful_months": successful_months,
        "failed_months": failed_months,
        "excluded_months": excluded_months,
    }
    if excluded_months:
        aggregated_result["message"] = "Recent months were excluded due to publication lag."
    if failed_months:
        aggregated_result.setdefault(
            "message",
            "Some months were unavailable and omitted from results.",
        )
    return jsonify(aggregated_result), 200


@market_analysis_bp.route('/manual-upload', methods=['POST'])
def upload_manual_month():
    """Upload a manual ``summary`` file for a given month.

    Expects a multipart/form-data POST with fields:
    - ``month``: the target month in ``YYYY-MM`` format
    - ``file``: a JSON or CSV file containing market stats
    """

    file = request.files.get('file')
    month = request.form.get('month')
    if not file or not month:
        return jsonify({"error": "Both 'file' and 'month' fields are required."}), 400
    try:
        target_date = datetime.strptime(month, '%Y-%m')
    except ValueError:
        return jsonify({"error": "Invalid 'month' format. Use YYYY-MM."}), 400
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {'.json', '.csv'}:
        return jsonify({"error": "Only .json or .csv files are allowed."}), 400
    base_dir = os.path.join(current_app.root_path, 'data', 'manual')
    os.makedirs(base_dir, exist_ok=True)
    save_name = secure_filename(f"{month}{ext}")
    save_path = os.path.join(base_dir, save_name)
    file.save(save_path)
    logging.info("Manual stats uploaded for %s saved to %s", month, save_path)
    return jsonify({"message": "File uploaded successfully.", "saved_as": save_name}), 201

@market_analysis_bp.route('/download-report', methods=['GET'])
def download_report():
    data = fetch_latest_wecar_data()
    if 'error' in data:
        return jsonify({"error": "Could not generate report, data unavailable."}), 503
    pdf_buffer = generate_pdf_report(data)
    if not pdf_buffer:
        return jsonify({"error": "Failed to generate PDF."}), 500
    filename = f"Market_Report_{data.get('report_period', 'latest').replace(' ', '_')}.pdf"
    return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

@market_analysis_bp.route('/cache/status', methods=['GET'])
def get_cache_status():
    return jsonify({
        "cache_entries": len(cache),
        "keys": list(cache.keys()),
        "cache_duration_seconds": CACHE_DURATION,
    })

@market_analysis_bp.route('/cache/clear', methods=['POST'])
def clear_all_cache():
    count = len(cache)
    cache.clear()
    logging.info("Cache cleared manually.")
    return jsonify({"message": f"Cache cleared successfully. {count} items removed."})
