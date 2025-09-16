"""Learning service that derives lightweight insights from stored content."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from statistics import mean
from typing import Dict, List, Optional

from .manual_content_service import ManualContentService


class LearningAlgorithmService:
    """Analyse previously posted content to surface actionable insights."""

    def __init__(self) -> None:
        self.performance_history: List[Dict] = []
        self.learning_insights: Dict[str, Dict] = {
            "optimal_posting_times": {},
            "best_performing_content_types": {},
            "effective_hashtags": {},
            "successful_hooks": [],
            "high_engagement_patterns": {},
            "audience_preferences": {},
        }
        self._manual_content_service = ManualContentService()

    # ------------------------------------------------------------------
    # Data ingestion helpers
    # ------------------------------------------------------------------
    def fetch_post_performance(
        self,
        access_token: Optional[str] = None,
        platform: str = "manual",
        content_items: Optional[List[Dict]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """Normalise content items into a common performance structure."""

        if content_items is None:
            content_items = self._manual_content_service.get_all_content(limit=limit or 200)

        processed_posts: List[Dict] = []
        for item in content_items:
            processed = self._process_manual_content(item, platform)
            if processed:
                processed_posts.append(processed)
        return processed_posts

    def _process_manual_content(self, content: Dict, default_platform: str) -> Optional[Dict]:
        if not isinstance(content, dict):
            return None

        text_content = content.get("content") or content.get("text") or content.get("caption")
        if not text_content:
            return None

        metrics = content.get("engagement") or content.get("metrics") or {}
        hashtags = content.get("hashtags") or []
        created_raw = content.get("uploaded_at") or content.get("created_at")
        try:
            created_time = datetime.fromisoformat((created_raw or "").replace("Z", "+00:00"))
        except ValueError:
            created_time = datetime.utcnow()

        return {
            "id": content.get("id") or content.get("content_id"),
            "platform": content.get("platform") or default_platform,
            "content_type": content.get("content_type", "text"),
            "text": text_content,
            "hashtags": hashtags,
            "created_time": created_time,
            "metrics": {
                "likes": int(metrics.get("likes", 0) or 0),
                "comments": int(metrics.get("comments", 0) or 0),
                "shares": int(metrics.get("shares", 0) or 0),
                "saves": int(metrics.get("saves", 0) or metrics.get("bookmarks", 0) or 0),
                "impressions": int(metrics.get("impressions", 0) or 0),
                "reach": int(metrics.get("reach", 0) or 0),
            },
        }

    def update_performance_history(self, posts: List[Dict]) -> None:
        if not posts:
            return
        self.performance_history.extend(posts)
        self.performance_history = self.performance_history[-500:]
        self._update_insights()

    # ------------------------------------------------------------------
    # Insight generation
    # ------------------------------------------------------------------
    def _update_insights(self) -> None:
        if not self.performance_history:
            return

        by_hour: Dict[int, List[int]] = defaultdict(list)
        content_scores: Dict[str, List[int]] = defaultdict(list)
        hashtag_counter: Counter = Counter()

        for entry in self.performance_history:
            metrics = entry["metrics"]
            engagement = self._engagement_score(metrics)
            created_time = entry["created_time"]
            by_hour[created_time.hour].append(engagement)
            content_scores[entry.get("content_type", "text")].append(engagement)
            hashtag_counter.update(entry.get("hashtags") or [])

        optimal_hours = {
            hour: round(mean(scores), 2)
            for hour, scores in sorted(by_hour.items(), key=lambda kv: mean(kv[1]), reverse=True)
        }
        best_content_types = {
            ctype: round(mean(scores), 2)
            for ctype, scores in sorted(content_scores.items(), key=lambda kv: mean(kv[1]), reverse=True)
        }

        self.learning_insights.update(
            {
                "optimal_posting_times": optimal_hours,
                "best_performing_content_types": best_content_types,
                "effective_hashtags": dict(hashtag_counter.most_common(10)),
                "high_engagement_patterns": self._summarise_engagement_patterns(),
            }
        )

    def _summarise_engagement_patterns(self) -> Dict[str, float]:
        if not self.performance_history:
            return {}

        last_month = datetime.utcnow() - timedelta(days=30)
        recent = [entry for entry in self.performance_history if entry["created_time"] >= last_month]
        if not recent:
            recent = self.performance_history

        averages = {
            key: round(mean(entry["metrics"].get(key, 0) for entry in recent), 2)
            for key in ["likes", "comments", "shares", "saves", "impressions", "reach"]
        }
        return averages

    @staticmethod
    def _engagement_score(metrics: Dict[str, int]) -> int:
        return (
            metrics.get("likes", 0)
            + metrics.get("comments", 0) * 2
            + metrics.get("shares", 0) * 3
            + metrics.get("saves", 0) * 2
        )

    # ------------------------------------------------------------------
    # Public API consumed by routes
    # ------------------------------------------------------------------
    def analyze_performance_patterns(self) -> Dict:
        if not self.performance_history:
            return {"error": "Not enough data to analyse patterns"}

        last_entry = self.performance_history[-1]
        summary = {
            "total_posts": len(self.performance_history),
            "last_post_analyzed": last_entry["created_time"].isoformat(),
            "average_engagement": round(
                mean(self._engagement_score(entry["metrics"]) for entry in self.performance_history), 2
            ),
        }
        summary.update(self._summarise_engagement_patterns())
        return summary

    def get_content_recommendations(self, content_type: Optional[str] = None) -> Dict:
        if not self.performance_history:
            return {
                "error": "Insufficient data",
                "recommendation": "Start uploading manual content so the learning engine has examples to study.",
            }

        best_hashtags = list(self.learning_insights.get("effective_hashtags", {}).keys())[:5]
        best_content_types = self.learning_insights.get("best_performing_content_types", {})
        recommended_type = content_type or (best_content_types.keys() or ["educational"])[0]

        return {
            "recommended_content_type": recommended_type,
            "recommended_hashtags": best_hashtags,
            "content_style_suggestions": "Highlight local expertise and include a clear CTA.",
            "engagement_optimization_tips": "Post during the top-performing hours and mention Windsor-Essex explicitly.",
        }

    def get_recent_posts(self, limit: int = 20) -> List[Dict]:
        return self.performance_history[-limit:]


learning_algorithm_service = LearningAlgorithmService()

__all__ = ["LearningAlgorithmService", "learning_algorithm_service"]
