"""Utilities for storing and analysing manually uploaded social content."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_STORAGE_DIR = BASE_DIR / "data" / "manual"


def _utcnow_iso() -> str:
    """Return the current UTC time in ISO 8601 format with a trailing ``Z``."""

    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _coerce_datetime(value: Optional[str]) -> datetime:
    """Parse the provided timestamp or return ``datetime.min`` when invalid."""

    if not value:
        return datetime.min

    try:
        cleaned = value.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return datetime.min


class ManualContentService:
    """Persist manually uploaded posts and derive lightweight analytics."""

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self._storage_path = Path(storage_path) if storage_path else DEFAULT_STORAGE_DIR
        self._storage_path.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Basic CRUD helpers
    # ------------------------------------------------------------------
    def _content_path(self, content_id: str) -> Path:
        return self._storage_path / f"{content_id}.json"

    def save_content(self, content_data: Dict) -> str:
        """Persist a content payload and return the generated identifier."""

        payload = dict(content_data)
        content_id = payload.get("id") or str(uuid.uuid4())
        payload.update(
            {
                "id": content_id,
                "uploaded_at": payload.get("uploaded_at") or _utcnow_iso(),
                "status": payload.get("status", "active"),
            }
        )

        with self._content_path(content_id).open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)

        return content_id

    def get_content(self, content_id: str) -> Optional[Dict]:
        """Return the stored payload for ``content_id`` if it exists."""

        path = self._content_path(content_id)
        if not path.exists():
            return None

        try:
            with path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, json.JSONDecodeError):
            return None

    def get_all_content(self, limit: int = 50) -> List[Dict]:
        """Return the most recent content items ordered by upload time."""

        items: List[Dict] = []
        for path in sorted(self._storage_path.glob("*.json")):
            try:
                with path.open("r", encoding="utf-8") as fh:
                    payload = json.load(fh)
                    items.append(payload)
            except (OSError, json.JSONDecodeError):
                continue

        items.sort(key=lambda entry: _coerce_datetime(entry.get("uploaded_at")), reverse=True)
        return items[:limit]

    def update_content(self, content_id: str, updates: Dict) -> bool:
        """Apply ``updates`` to the stored content and persist the result."""

        current = self.get_content(content_id)
        if current is None:
            return False

        current.update(dict(updates))
        current["updated_at"] = _utcnow_iso()

        with self._content_path(content_id).open("w", encoding="utf-8") as fh:
            json.dump(current, fh, indent=2, ensure_ascii=False)

        return True

    def delete_content(self, content_id: str) -> bool:
        """Remove the persisted payload associated with ``content_id``."""

        path = self._content_path(content_id)
        try:
            path.unlink()
            return True
        except FileNotFoundError:
            return False
        except OSError:
            return False

    # ------------------------------------------------------------------
    # Query helpers and analytics
    # ------------------------------------------------------------------
    def search_content(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Return items matching ``query`` and the provided ``filters``."""

        filters = filters or {}
        query_lower = query.lower().strip()
        date_from = _coerce_datetime(filters.get("date_from")) if filters.get("date_from") else None
        date_to = _coerce_datetime(filters.get("date_to")) if filters.get("date_to") else None

        results: List[Dict] = []
        for item in self.get_all_content(limit=1000):
            if filters.get("platform") and item.get("platform") != filters["platform"]:
                continue

            uploaded_at = _coerce_datetime(item.get("uploaded_at"))
            if date_from and uploaded_at < date_from:
                continue
            if date_to and uploaded_at > date_to:
                continue

            if query_lower:
                haystack = " ".join(
                    [
                        item.get("text", ""),
                        item.get("caption", ""),
                        item.get("platform", ""),
                        " ".join(item.get("hashtags", [])),
                    ]
                ).lower()
                if query_lower not in haystack:
                    continue

            results.append(item)

        return results

    def get_content_stats(self) -> Dict:
        """Return aggregate statistics for the stored manual content."""

        content_items = self.get_all_content(limit=1000)
        total_posts = len(content_items)
        stats = {
            "total_posts": total_posts,
            "platforms": {},
            "content_types": {},
            "recent_activity": {},
            "hashtag_usage": {},
            "engagement_summary": {},
        }

        for item in content_items:
            platform = item.get("platform", "unknown")
            stats["platforms"][platform] = stats["platforms"].get(platform, 0) + 1

            content_type = item.get("content_type", "text")
            stats["content_types"][content_type] = stats["content_types"].get(content_type, 0) + 1

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent = [i for i in content_items if _coerce_datetime(i.get("uploaded_at")) >= thirty_days_ago]
        stats["recent_activity"] = {
            "posts_last_30_days": len(recent),
            "avg_posts_per_day": (len(recent) / 30) if recent else 0,
        }

        hashtag_counts: Dict[str, int] = {}
        for item in content_items:
            for hashtag in item.get("hashtags", []):
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        stats["hashtag_usage"] = dict(sorted(hashtag_counts.items(), key=lambda kv: kv[1], reverse=True)[:10])

        total_likes = sum(self._safe_metric(item, "likes") for item in content_items)
        total_comments = sum(self._safe_metric(item, "comments") for item in content_items)
        total_shares = sum(self._safe_metric(item, "shares") for item in content_items)
        stats["engagement_summary"] = {
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "avg_likes_per_post": (total_likes / total_posts) if total_posts else 0,
            "avg_comments_per_post": (total_comments / total_posts) if total_posts else 0,
        }

        return stats

    # ------------------------------------------------------------------
    # Content enrichment helpers
    # ------------------------------------------------------------------
    def extract_hashtags(self, text: str) -> List[str]:
        return [match.lower() for match in re.findall(r"#\w+", text or "")]

    def extract_mentions(self, text: str) -> List[str]:
        return [match.lower() for match in re.findall(r"@\w+", text or "")]

    def process_content_upload(self, content_data: Dict) -> Dict:
        """Normalise uploaded content and derive lightweight metadata."""

        text = content_data.get("text") or content_data.get("caption") or ""
        hashtags = self.extract_hashtags(text)
        mentions = self.extract_mentions(text)

        word_count = len(text.split()) if text else 0
        char_count = len(text)

        content_type = "text"
        if content_data.get("image_url") or content_data.get("images"):
            content_type = "image_with_text" if text else "image"
        elif content_data.get("video_url"):
            content_type = "video_with_text" if text else "video"

        enriched = {
            **content_data,
            "hashtags": hashtags,
            "mentions": mentions,
            "content_type": content_type,
            "word_count": word_count,
            "char_count": char_count,
            "has_cta": self._detect_call_to_action(text),
            "sentiment": self._analyze_basic_sentiment(text),
            "processed_at": _utcnow_iso(),
        }
        return enriched

    def _detect_call_to_action(self, text: str) -> bool:
        if not text:
            return False

        phrases = (
            "contact me",
            "call me",
            "dm me",
            "message me",
            "text me",
            "reach out",
            "get in touch",
            "let's talk",
            "let's chat",
            "schedule",
            "book",
            "visit",
            "see more",
            "click here",
            "learn more",
            "find out",
            "discover",
            "explore",
            "sign up",
            "register",
            "subscribe",
            "follow",
            "buy now",
            "shop now",
            "order now",
            "get started",
        )
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in phrases)

    def _analyze_basic_sentiment(self, text: str) -> str:
        if not text:
            return "neutral"

        positive_words = {
            "amazing",
            "awesome",
            "beautiful",
            "best",
            "excellent",
            "fantastic",
            "great",
            "happy",
            "incredible",
            "love",
            "perfect",
            "wonderful",
            "excited",
            "thrilled",
            "delighted",
            "pleased",
            "satisfied",
        }
        negative_words = {
            "bad",
            "terrible",
            "awful",
            "horrible",
            "worst",
            "hate",
            "disappointed",
            "frustrated",
            "angry",
            "sad",
            "upset",
        }

        lowered = text.lower()
        positive_count = sum(1 for word in positive_words if word in lowered)
        negative_count = sum(1 for word in negative_words if word in lowered)

        if positive_count > negative_count:
            return "positive"
        if negative_count > positive_count:
            return "negative"
        return "neutral"

    def export_content(self, format_type: str = "json") -> str:
        items = self.get_all_content(limit=1000)
        if format_type == "json":
            return json.dumps(items, indent=2, ensure_ascii=False)

        if format_type == "csv":
            if not items:
                return ""

            fieldnames = sorted({key for item in items for key in item.keys()})
            rows: List[str] = [",".join(fieldnames)]
            for item in items:
                values: List[str] = []
                for field in fieldnames:
                    value = item.get(field, "")
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value, ensure_ascii=False)
                    escaped = str(value).replace('"', '""')
                    values.append(f'"{escaped}"')
                rows.append(",".join(values))
            return "\n".join(rows)

        raise ValueError("Unsupported export format: expected 'json' or 'csv'.")

    def import_content(self, content_list: Iterable[Dict]) -> Dict:
        results = {"imported": 0, "failed": 0, "errors": []}
        for index, item in enumerate(content_list, start=1):
            try:
                processed = self.process_content_upload(item)
                self.save_content(processed)
                results["imported"] += 1
            except Exception as exc:  # pragma: no cover - defensive catch
                results["failed"] += 1
                results["errors"].append(f"Item {index}: {exc}")
        return results

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _safe_metric(item: Dict, metric: str) -> int:
        metrics = item.get("engagement") or item.get("metrics") or {}
        value = metrics.get(metric) if isinstance(metrics, dict) else 0
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0


__all__ = ["ManualContentService"]
