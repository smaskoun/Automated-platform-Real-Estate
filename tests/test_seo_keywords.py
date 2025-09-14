import os
import sys
from flask import Flask

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from routes.seo_routes import seo_bp
from routes.seo_tools_routes import seo_tools_bp
from services.seo_content_service import SEOContentService

def create_app():
    app = Flask(__name__)
    app.register_blueprint(seo_bp, url_prefix="/seo")
    app.register_blueprint(seo_tools_bp, url_prefix="/seo-tools")
    return app


def test_analyze_keywords_service():
    service = SEOContentService()
    result = service.analyze_keywords(["Home", "home", "Windsor"])
    assert result["scores"]["home"] == 2
    assert "windsor" in result["scores"]
    assert "home" not in result.get("suggestions", [])


def test_analyze_keywords_route_success():
    app = create_app()
    client = app.test_client()
    resp = client.post("/seo/analyze-keywords", json={"keywords": ["Home", "Windsor"]})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["scores"]["home"] == 1


def test_analyze_keywords_route_validation():
    app = create_app()
    client = app.test_client()
    resp = client.post("/seo/analyze-keywords", json={"keywords": "home"})
    assert resp.status_code == 400


def test_keyword_density_service():
    service = SEOContentService()
    text = "keyword test keyword"
    result = service.keyword_density(text, "keyword")
    assert result["keyword_count"] == 2
    assert result["total_words"] == 3
    assert result["keyword_density"] > 3


def test_keyword_density_route():
    app = create_app()
    client = app.test_client()
    resp = client.post(
        "/seo-tools/keyword-density",
        json={"text": "keyword test keyword", "keyword": "keyword"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["keyword_count"] == 2
