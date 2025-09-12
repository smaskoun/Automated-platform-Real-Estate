from datetime import datetime
from unittest.mock import patch, Mock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.services import wecar_scraper


def mocked_get_factory(responses):
    def _mocked_get(url, headers=None, timeout=10):
        text = responses.get(url)
        if text is None:
            raise AssertionError(f"Unexpected URL {url}")
        response = Mock()
        response.status_code = 200
        response.text = text
        response.raise_for_status = lambda: None
        return response
    return _mocked_get


def test_scrape_month_parses_metrics_and_sales():
    base = "https://wecartech.com/wecfiles/stats_new/2024/may/"
    html = """
    <html><body>
    <script src="js/avgprice.js"></script>
    <script src="js/sales.js"></script>
    <script src="js/mamonth.js"></script>
    <script src="js/resmonth.js"></script>
    </body></html>
    """
    avg_js = """
var chart = AmCharts.makeChart('avgprice', {
  "dataProvider": [
    {"month": "May", "2023": "100", "2024": "200",}
  ]
});
"""
    sales_js = """
var chart = AmCharts.makeChart('sales', {
  "dataProvider": [
    {"month": "May", "2023": "10", "2024": "20",}
  ]
});
"""
    listings_js = """
var chart = AmCharts.makeChart('mamonth', {
  "dataProvider": [
    {"month": "May", "2023": "30", "2024": "40",}
  ],
  "categoryAxis": {"title": "Available Listings (at time of report): 100"}
});
"""
    res_js = """
var chart = AmCharts.makeChart('resmonth', {
  "dataProvider": [
    {"category": "Single Family", "units sold": "15"},
    {"category": "Townhouse/Condo", "units sold": "5"}
  ]
});
"""

    responses = {
        base: html,
        base + "js/avgprice.js": avg_js,
        base + "js/sales.js": sales_js,
        base + "js/mamonth.js": listings_js,
        base + "js/resmonth.js": res_js,
    }

    with patch('requests.get', side_effect=mocked_get_factory(responses)):
        result = wecar_scraper.scrape_month(datetime(2024, 5, 1))

    assert result['key_metrics']['average_price'] == 200
    assert result['key_metrics']['total_sales'] == 20
    assert result['key_metrics']['new_listings'] == 40
    assert result['key_metrics']['months_of_supply'] == 5.0
    assert result['sales_by_type'] == [
        {'name': 'Single Family', 'sales': 15},
        {'name': 'Townhouse/Condo', 'sales': 5},
    ]
