import re
import json
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://wecartech.com/wecfiles/stats_new"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def _get(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.text

def _parse_data_provider(js_text: str) -> List[Dict]:
    match = re.search(r'dataProvider"\s*:\s*(\[[^\]]*\])', js_text, re.DOTALL)
    if not match:
        return []
    data = match.group(1)
    # remove trailing commas
    data = re.sub(r",\s*([}\]])", r"\1", data)
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return []

def _find_month_entry(data: List[Dict], month_key: str) -> Dict:
    for entry in data:
        month = entry.get("month") or entry.get("category")
        if isinstance(month, str) and month.lower().startswith(month_key):
            return entry
    return {}

def scrape_month(target_date: datetime) -> Dict:
    """Scrape WECAR stats page for the given month."""
    year = target_date.year
    month_dir = target_date.strftime("%b").lower()
    page_url = f"{BASE_URL}/{year}/{month_dir}/"

    # Fetch HTML page and gather JS references
    html = _get(page_url)
    soup = BeautifulSoup(html, "html.parser")
    script_srcs = [s.get("src") for s in soup.find_all("script") if s.get("src")]

    month_key = target_date.strftime("%b").lower()
    year_key = str(year)

    # Helper to fetch and parse a specific JS file if referenced
    def get_data_from_js(name: str):
        if name not in script_srcs:
            return [], ""
        js_text = _get(page_url + name)
        return _parse_data_provider(js_text), js_text

    # --- Average Price ---
    avg_data, _ = get_data_from_js("js/avgprice.js")
    avg_entry = _find_month_entry(avg_data, month_key)
    avg_price = int(avg_entry.get(year_key, "0").replace(",", "")) if avg_entry else 0

    # --- Total Sales ---
    sales_data, _ = get_data_from_js("js/sales.js")
    sales_entry = _find_month_entry(sales_data, month_key)
    total_sales = int(sales_entry.get(year_key, "0").replace(",", "")) if sales_entry else 0

    # --- New Listings and Available Listings ---
    listings_data, listings_js = get_data_from_js("js/mamonth.js")
    listings_entry = _find_month_entry(listings_data, month_key)
    new_listings = int(listings_entry.get(year_key, "0").replace(",", "")) if listings_entry else 0
    avail_match = re.search(r"Available Listings[^:]*:\s*([0-9,]+)", listings_js)
    available_listings = int(avail_match.group(1).replace(",", "")) if avail_match else 0
    months_of_supply = round(available_listings / total_sales, 2) if total_sales else 0

    # --- Sales by Type (price range) ---
    res_data, _ = get_data_from_js("js/resmonth.js")
    sales_by_type = []
    for entry in res_data:
        name = entry.get("category")
        sales_val = entry.get("units sold", "0")
        try:
            sales = int(str(sales_val).replace(",", ""))
        except ValueError:
            sales = 0
        sales_by_type.append({"name": name, "sales": sales})

    return {
        "key_metrics": {
            "average_price": avg_price,
            "total_sales": total_sales,
            "new_listings": new_listings,
            "months_of_supply": months_of_supply,
        },
        "sales_by_type": sales_by_type,
    }
