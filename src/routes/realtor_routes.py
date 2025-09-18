"""API routes for Realtor.ca scraping utilities."""

from http import HTTPStatus

from flask import Blueprint, current_app, jsonify

from ..services.realtor_scraper_service import (
    RealtorScraperService,
    serialize_scrape_response,
)

realtor_bp = Blueprint("realtor", __name__)
_scraper_service = RealtorScraperService()


@realtor_bp.get("/properties")
def get_windsor_essex_properties():
    """Run the server-side scraper and return normalized property data."""

    try:
        properties = _scraper_service.scrape_windsor_essex_properties()
    except RuntimeError as exc:
        current_app.logger.warning("Realtor scraper request failed: %s", exc)
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_REQUEST
    except Exception as exc:  # pragma: no cover - defensive logging
        current_app.logger.exception("Unexpected Realtor scraper failure: %s", exc)
        return (
            jsonify({"error": "Failed to fetch Realtor.ca property data."}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    return jsonify(serialize_scrape_response(properties))

