"""Server-side scraper for Realtor.ca Windsor-Essex listings."""

from __future__ import annotations

import logging
import math
import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from apify_client import ApifyClient

BASE_REALTOR_URL = "https://www.realtor.ca"

WINDSOR_ESSEX_START_URLS = [
    "https://www.realtor.ca/on/windsor/real-estate",
    "https://www.realtor.ca/on/tecumseh/real-estate",
    "https://www.realtor.ca/on/lasalle/real-estate",
    "https://www.realtor.ca/on/amherstburg/real-estate",
    "https://www.realtor.ca/on/lakeshore/real-estate",
    "https://www.realtor.ca/on/kingsville/real-estate",
    "https://www.realtor.ca/on/leamington/real-estate",
    "https://www.realtor.ca/on/essex/real-estate",
    "https://www.realtor.ca/on/belle-river/real-estate",
]

WINDSOR_ESSEX_CITIES = [
    "windsor",
    "tecumseh",
    "lasalle",
    "amherstburg",
    "lakeshore",
    "kingsville",
    "leamington",
    "essex",
    "belle river",
    "harrow",
    "maidstone",
    "mcgregor",
    "cottam",
    "stoney point",
    "staples",
]


class RealtorScraperService:
    """High-level interface responsible for orchestrating the Realtor.ca scrape."""

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        token = os.getenv("APIFY_API_KEY") or os.getenv("VITE_APIFY_API_KEY") or ""
        self._apify_token = token.strip()
        self.logger = logger or logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def scrape_windsor_essex_properties(
        self,
        *,
        max_items: int = 500,
        dataset_timeout_ms: int = 120_000,
    ) -> List[Dict[str, Any]]:
        """Scrape Realtor.ca for Windsor-Essex listings via Apify."""

        if not self._apify_token:
            raise RuntimeError("APIFY_API_KEY is not configured for the scraper service.")

        client = ApifyClient(self._apify_token)
        run_input = {
            "startUrls": [{"url": url} for url in WINDSOR_ESSEX_START_URLS],
            "maxItems": max_items,
            "proxyConfig": {"useApifyProxy": True},
            "includeCondos": True,
        }

        try:
            run = client.actor("apify/realtor-ca-scraper").call(run_input)
        except Exception as exc:  # pragma: no cover - network failures
            self.logger.exception("Apify scraping run failed: %%s", exc)
            raise RuntimeError("Unable to execute Apify actor for Realtor.ca scrape") from exc

        dataset_id = run.get("defaultDatasetId") if isinstance(run, dict) else None
        if not dataset_id:
            raise RuntimeError("Apify run completed without providing a dataset id")

        self._wait_for_dataset_ready(client, dataset_id, dataset_timeout_ms)
        raw_items = self._collect_dataset_items(client, dataset_id)

        normalized_listings: List[Dict[str, Any]] = []
        for record in raw_items:
            listing = self._normalize_listing(record)
            if not listing:
                continue
            city = listing.get("city")
            if city and city.lower() in WINDSOR_ESSEX_CITIES:
                normalized_listings.append(listing)

        return self._deduplicate_listings(normalized_listings)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _wait_for_dataset_ready(
        self,
        client: ApifyClient,
        dataset_id: str,
        timeout_ms: int,
        poll_interval_sec: int = 5,
    ) -> None:
        deadline = time.time() + (timeout_ms / 1000)
        dataset_client = client.dataset(dataset_id)

        while time.time() < deadline:
            try:
                response = dataset_client.list_items(limit=1, clean=True)
            except Exception as exc:  # pragma: no cover - network failures
                self.logger.warning("Waiting for dataset readiness failed: %%s", exc)
                time.sleep(poll_interval_sec)
                continue

            total = response.get("total")
            items = response.get("items")
            if (isinstance(total, int) and total > 0) or (isinstance(items, list) and items):
                return

            time.sleep(poll_interval_sec)

        self.logger.warning("Timed out waiting for Apify dataset %s to become ready", dataset_id)

    def _collect_dataset_items(
        self,
        client: ApifyClient,
        dataset_id: str,
        page_limit: int = 500,
    ) -> List[Dict[str, Any]]:
        dataset_client = client.dataset(dataset_id)
        items: List[Dict[str, Any]] = []
        offset = 0

        while True:
            response = dataset_client.list_items(limit=page_limit, offset=offset, clean=True)
            page_items = response.get("items")
            if not page_items:
                break

            items.extend(page_items)
            offset += len(page_items)

            total = response.get("total")
            if isinstance(total, int) and offset >= total:
                break

        return items

    # ------------------------------------------------------------------
    # Normalisation helpers
    # ------------------------------------------------------------------
    def _normalize_listing(self, raw: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(raw, dict):
            return None

        location = self._first_dict(
            raw.get("location"),
            raw.get("address"),
            raw.get("property", {}).get("address"),
            raw.get("property", {}).get("location"),
            raw.get("propertyLocation"),
        )
        location = location or {}

        city = self._clean_string(
            location.get("city")
            or location.get("municipality")
            or raw.get("city")
            or raw.get("municipality")
        )
        province = self._clean_string(location.get("province") or location.get("state") or "ON")
        postal_code = self._clean_string(location.get("postalCode") or location.get("postal_code"))
        price_value = self._parse_price(
            raw.get("price")
            or raw.get("priceValue")
            or raw.get("property", {}).get("price")
            or raw.get("property", {}).get("priceValue")
        )
        price_formatted = (
            self._format_price(price_value)
            if price_value is not None
            else self._clean_string(
                raw.get("displayPrice") or raw.get("priceFormatted") or raw.get("priceLabel")
            )
        )

        features = self._extract_features(raw)
        images = self._extract_images(raw)
        agents = self._extract_agents(raw)
        coordinates = self._extract_coordinates(raw)

        listing = {
            "id": raw.get("id")
            or raw.get("listingId")
            or raw.get("mlsId")
            or raw.get("mlsNumber")
            or raw.get("property", {}).get("mlsNumber")
            or raw.get("property", {}).get("id"),
            "mlsNumber": self._clean_string(
                raw.get("mlsNumber")
                or raw.get("mlsId")
                or raw.get("property", {}).get("mlsNumber")
                or raw.get("property", {}).get("mlsId")
                or raw.get("listingId")
            ),
            "address": self._format_address(location, raw),
            "city": city,
            "province": province,
            "postalCode": postal_code,
            "country": self._clean_string(location.get("country") or "Canada"),
            "price": price_value,
            "priceFormatted": price_formatted,
            "priceText": self._clean_string(
                raw.get("price") or raw.get("priceLabel") or raw.get("displayPrice")
            ),
            "propertyType": self._clean_string(
                raw.get("propertyType")
                or raw.get("type")
                or raw.get("property", {}).get("type")
                or raw.get("category")
                or raw.get("building", {}).get("type")
            ),
            "description": self._clean_string(
                raw.get("description")
                or raw.get("publicRemarks")
                or raw.get("remarks")
                or raw.get("property", {}).get("description")
                or raw.get("property", {}).get("remarks")
            ),
            "bedrooms": features.get("bedrooms"),
            "bathrooms": features.get("bathrooms"),
            "squareFeet": features.get("squareFeet"),
            "lotSize": features.get("lotSize"),
            "lotSizeText": features.get("lotSizeText"),
            "yearBuilt": features.get("yearBuilt"),
            "listingUrl": self._ensure_absolute_url(
                raw.get("url")
                or raw.get("detailUrl")
                or raw.get("detailPageUrl")
                or raw.get("permalink")
                or raw.get("property", {}).get("url")
            ),
            "images": images,
            "agents": agents,
            "brokerage": self._clean_string(
                raw.get("brokerage") or raw.get("officeName") or raw.get("office") or raw.get("broker")
            ),
            "coordinates": coordinates,
            "lastUpdated": raw.get("lastUpdated")
            or raw.get("updated")
            or raw.get("lastUpdatedAt"),
        }

        return listing

    def _format_address(self, location: Dict[str, Any], raw: Dict[str, Any]) -> Optional[str]:
        if isinstance(raw.get("addressText"), str):
            return self._clean_string(raw.get("addressText"))

        parts: List[str] = []
        candidates = [
            location.get("addressLine1")
            or location.get("address1")
            or location.get("streetAddress")
            or location.get("line1"),
            location.get("addressLine2")
            or location.get("address2")
            or location.get("streetAddress2")
            or location.get("line2"),
            location.get("city") or location.get("municipality"),
            location.get("province") or location.get("state"),
            location.get("postalCode") or location.get("postal_code"),
        ]

        for entry in candidates:
            cleaned = self._clean_string(entry)
            if cleaned:
                parts.append(cleaned)

        return ", ".join(parts) if parts else None

    def _extract_features(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        normalized_details = self._normalize_details(listing)

        def get_detail_value(*keywords: str) -> Optional[Any]:
            keyword_set = {keyword.lower() for keyword in keywords}
            for detail in normalized_details:
                label = detail.get("label", "").lower()
                if any(keyword in label for keyword in keyword_set):
                    return detail.get("value") or detail.get("text")
            return None

        bedrooms = self._extract_number(
            self._value_from_paths(
                listing,
                [
                    "bedrooms",
                    "bedroomsTotal",
                    "bedroomsAboveGround",
                    "property.bedrooms",
                    "property.building.bedrooms",
                    "building.bedrooms",
                    "building.bedroomsTotal",
                    "summary.bedrooms",
                ],
            )
        )
        if bedrooms is None:
            bedrooms = self._extract_number(get_detail_value("bedroom", "bed"))

        bathrooms = self._extract_number(
            self._value_from_paths(
                listing,
                [
                    "bathrooms",
                    "bathroomsTotal",
                    "property.bathrooms",
                    "property.building.bathrooms",
                    "building.bathrooms",
                    "summary.bathrooms",
                ],
            )
        )
        if bathrooms is None:
            bathrooms = self._extract_number(get_detail_value("bathroom", "bath"))

        square_feet = self._extract_number(
            self._value_from_paths(
                listing,
                [
                    "sizeInterior",
                    "building.sizeInterior",
                    "building.totalFinishedArea",
                    "property.building.sizeInterior",
                    "property.squareFeet",
                    "squareFootage",
                    "area",
                ],
            )
        )
        if square_feet is None:
            square_feet = self._extract_number(get_detail_value("square feet", "sqft", "interior"))

        lot_size_raw = self._value_from_paths(
            listing,
            [
                "land.sizeTotal",
                "land.sizeTotalText",
                "land.sizeFrontage",
                "property.land.sizeTotal",
                "lotSize",
                "lotSizeArea",
                "property.landSize",
            ],
        )
        if lot_size_raw is None:
            lot_size_raw = get_detail_value("lot size", "size total", "land size")

        year_built = self._extract_number(
            self._value_from_paths(
                listing,
                [
                    "building.builtYear",
                    "building.constructedDate",
                    "property.building.builtYear",
                    "property.building.constructedDate",
                ],
            )
        )
        if year_built is None:
            year_built = self._extract_number(get_detail_value("built", "constructed", "year"))

        return {
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "squareFeet": square_feet,
            "lotSize": self._extract_number(lot_size_raw),
            "lotSizeText": self._clean_string(lot_size_raw),
            "yearBuilt": year_built,
        }

    def _normalize_details(self, listing: Dict[str, Any]) -> List[Dict[str, Any]]:
        collections: List[Iterable[Any]] = []
        for path in ("details", "property.details", "propertyDetails", "building.details"):
            value = self._get_path(listing, path)
            if isinstance(value, list):
                collections.append(value)

        normalized: List[Dict[str, Any]] = []
        for collection in collections:
            for detail in collection:
                if detail is None:
                    continue
                if isinstance(detail, str):
                    normalized.append({"label": detail, "value": detail})
                elif isinstance(detail, dict):
                    label = detail.get("label") or detail.get("name")
                    value = (
                        detail.get("value")
                        if detail.get("value") is not None
                        else detail.get("text")
                        if detail.get("text") is not None
                        else detail.get("display")
                    )
                    normalized.append({"label": label or "", "value": value})
                elif isinstance(detail, (list, tuple)) and len(detail) >= 2:
                    normalized.append({"label": detail[0], "value": detail[1]})

        return normalized

    def _value_from_paths(self, data: Dict[str, Any], paths: List[str]) -> Any:
        for path in paths:
            value = self._get_path(data, path)
            if value not in (None, ""):
                return value
        return None

    def _get_path(self, data: Any, path: str) -> Any:
        current = data
        for segment in path.split("."):
            if isinstance(current, dict) and segment in current:
                current = current[segment]
            else:
                return None
        return current

    def _extract_number(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return value if math.isfinite(float(value)) else None
        if isinstance(value, str):
            normalized = re.sub(r"[^0-9.,-]+", "", value)
            match = re.search(r"-?\d+(?:[.,]\d+)?", normalized)
            if match:
                try:
                    return float(match.group(0).replace(",", ""))
                except ValueError:
                    return None
        return None

    def _extract_images(self, listing: Dict[str, Any]) -> List[str]:
        image_set: "set[str]" = set()

        def add_image(url: Any) -> None:
            cleaned = self._clean_string(url)
            if not cleaned:
                return
            if cleaned.startswith("http://") or cleaned.startswith("https://"):
                image_set.add(cleaned)
            else:
                prefix = "" if cleaned.startswith("/") else "/"
                image_set.add(f"{BASE_REALTOR_URL}{prefix}{cleaned}")

        candidate_arrays = [
            listing.get("images"),
            listing.get("photos"),
            listing.get("media"),
            listing.get("gallery"),
            self._get_path(listing, "property.photos"),
            self._get_path(listing, "property.images"),
            self._get_path(listing, "property.media"),
            self._get_path(listing, "property.photo.highResPaths"),
            self._get_path(listing, "property.photo.lowResPaths"),
            self._get_path(listing, "property.photo.url"),
        ]

        for candidate in candidate_arrays:
            if isinstance(candidate, str):
                add_image(candidate)
            elif isinstance(candidate, (list, tuple)):
                for item in candidate:
                    add_image(item)
            elif isinstance(candidate, dict):
                for item in candidate.values():
                    add_image(item)

        return list(image_set)

    def _extract_agents(self, listing: Dict[str, Any]) -> List[Dict[str, Optional[str]]]:
        agents: List[Dict[str, Optional[str]]] = []

        def push_agent(agent: Any) -> None:
            if not isinstance(agent, dict):
                return
            name = self._clean_string(
                agent.get("name")
                or agent.get("fullName")
                or agent.get("agentName")
                or agent.get("agent")
                or agent.get("contactName")
            )
            phone = self._clean_string(
                agent.get("phone")
                or agent.get("telephone")
                or agent.get("phoneNumber")
                or agent.get("contactPhone")
            )
            email = self._clean_string(agent.get("email") or agent.get("contactEmail"))
            brokerage = self._clean_string(
                agent.get("brokerage")
                or agent.get("office")
                or agent.get("officeName")
                or agent.get("company")
                or agent.get("broker")
            )
            title = self._clean_string(agent.get("title") or agent.get("position") or agent.get("role"))

            if name or phone or email or brokerage:
                agents.append(
                    {"name": name, "phone": phone, "email": email, "brokerage": brokerage, "title": title}
                )

        candidate_collections = [
            listing.get("agents"),
            listing.get("agent"),
            self._get_path(listing, "property.agents"),
            self._get_path(listing, "property.agent"),
            self._get_path(listing, "property.representatives"),
            listing.get("contact"),
            listing.get("representatives"),
            self._get_path(listing, "brokerage.agents"),
            self._get_path(listing, "office.agents"),
        ]

        for collection in candidate_collections:
            if isinstance(collection, list):
                for item in collection:
                    push_agent(item)
            elif isinstance(collection, dict):
                push_agent(collection)

        if not agents:
            fallback_brokerage = self._clean_string(
                listing.get("brokerage")
                or listing.get("office")
                or listing.get("officeName")
                or listing.get("company")
            )
            if fallback_brokerage:
                agents.append(
                    {
                        "name": None,
                        "phone": None,
                        "email": None,
                        "brokerage": fallback_brokerage,
                        "title": None,
                    }
                )

        return self._deduplicate_agents(agents)

    def _deduplicate_agents(self, agents: List[Dict[str, Optional[str]]]) -> List[Dict[str, Optional[str]]]:
        unique: Dict[str, Dict[str, Optional[str]]] = {}
        for agent in agents:
            key_parts = [agent.get("name"), agent.get("email"), agent.get("phone"), agent.get("brokerage")]
            key = "|".join(part.lower() for part in key_parts if isinstance(part, str))
            if key not in unique:
                unique[key] = agent
        return list(unique.values())

    def _extract_coordinates(self, listing: Dict[str, Any]) -> Optional[Dict[str, float]]:
        lat = self._extract_number(
            self._value_from_paths(
                listing,
                [
                    "coordinates.lat",
                    "coordinates.latitude",
                    "location.lat",
                    "location.latitude",
                    "property.location.lat",
                    "property.location.latitude",
                    "geo.lat",
                    "geo.latitude",
                ],
            )
        )
        lng = self._extract_number(
            self._value_from_paths(
                listing,
                [
                    "coordinates.lng",
                    "coordinates.lon",
                    "coordinates.longitude",
                    "location.lng",
                    "location.lon",
                    "location.longitude",
                    "property.location.lng",
                    "property.location.lon",
                    "property.location.longitude",
                    "geo.lng",
                    "geo.lon",
                    "geo.longitude",
                ],
            )
        )

        if lat is not None and lng is not None:
            return {"lat": float(lat), "lng": float(lng)}
        return None

    def _ensure_absolute_url(self, url: Optional[str]) -> Optional[str]:
        cleaned = self._clean_string(url)
        if not cleaned:
            return None
        if re.match(r"^https?://", cleaned, flags=re.IGNORECASE):
            return cleaned
        prefix = "" if cleaned.startswith("/") else "/"
        return f"{BASE_REALTOR_URL}{prefix}{cleaned}"

    def _deduplicate_listings(self, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unique: Dict[str, Dict[str, Any]] = {}
        for listing in listings:
            key_candidates = [
                listing.get("mlsNumber"),
                listing.get("listingUrl"),
                listing.get("address"),
            ]
            key = next((str(candidate).lower() for candidate in key_candidates if candidate), None)
            if key and key not in unique:
                unique[key] = listing
        return list(unique.values())

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _clean_string(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = " ".join(value.replace("\xa0", " ").split())
            return cleaned or None
        if isinstance(value, (int, float)):
            if isinstance(value, float) and not math.isfinite(value):
                return None
            return str(value)
        try:
            cleaned = str(value).strip()
            return cleaned or None
        except Exception:  # pragma: no cover - defensive
            return None

    @staticmethod
    def _parse_price(value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value) if math.isfinite(float(value)) else None
        if isinstance(value, dict):
            for key in ("amount", "value", "price"):
                if key in value:
                    return RealtorScraperService._parse_price(value[key])
            return None
        if isinstance(value, str):
            normalized = re.sub(r"[^0-9.,-]+", "", value)
            match = re.search(r"-?\d+(?:[.,]\d+)?", normalized)
            if match:
                try:
                    return float(match.group(0).replace(",", ""))
                except ValueError:
                    return None
        return None

    @staticmethod
    def _format_price(value: Optional[float]) -> Optional[str]:
        if value is None:
            return None
        try:
            return f"${value:,.0f}"
        except (ValueError, TypeError):  # pragma: no cover - defensive
            return str(value)

    @staticmethod
    def _first_dict(*values: Any) -> Optional[Dict[str, Any]]:
        for value in values:
            if isinstance(value, dict):
                return value
        return None


def serialize_scrape_response(properties: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a JSON serialisable response payload for the API."""

    return {
        "properties": properties,
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        "source": "apify",
    }

