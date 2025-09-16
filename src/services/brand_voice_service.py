"""Legacy brand voice analysis utilities."""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Tuple

from .manual_content_service import ManualContentService


class BrandVoiceService:
    """Derive writing traits from a collection of posts."""

    def __init__(self) -> None:
        self.manual_content_service = ManualContentService()

    def fetch_user_posts(
        self,
        access_token: Optional[str] = None,
        platform: str = "manual",
        limit: int = 50,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        filters = filters or {}
        manual_posts = self.manual_content_service.get_all_content(limit=limit)
        if platform != "manual":
            manual_posts = [
                post
                for post in manual_posts
                if (post.get("platform") or "manual").lower() == platform.lower()
            ]
        if filters.get("has_cta") is True:
            manual_posts = [post for post in manual_posts if post.get("has_cta")]
        return manual_posts

    def analyse_posts(self, posts: List[Dict]) -> Dict:
        if not posts:
            return {"error": "No content available for analysis"}

        tones = Counter()
        emoji_count = 0
        sentence_lengths: List[int] = []

        for post in posts:
            text = post.get("text") or post.get("content") or ""
            tones.update(self._detect_tone(text))
            emoji_count += sum(1 for char in text if char in "😀😃😄😁😆😅😂🤣😊😍🥰😘😎✨🔥")
            sentence_lengths.extend(len(sentence.split()) for sentence in text.split(".") if sentence.strip())

        average_sentence_length = round(sum(sentence_lengths) / len(sentence_lengths), 2) if sentence_lengths else 0

        return {
            "dominant_tone": tones.most_common(1)[0][0] if tones else "neutral",
            "emoji_usage": emoji_count,
            "average_sentence_length": average_sentence_length,
            "sample_size": len(posts),
        }

    def _detect_tone(self, text: str) -> Counter:
        tone_keywords: List[Tuple[str, List[str]]] = [
            ("professional", ["expertise", "analysis", "strategy", "guidance"]),
            ("friendly", ["love", "happy", "excited", "amazing"]),
            ("educational", ["tip", "learn", "advice", "guide"]),
            ("motivational", ["achieve", "success", "goal", "dream"]),
        ]
        counts = Counter()
        lowered = text.lower()
        for tone, keywords in tone_keywords:
            if any(keyword in lowered for keyword in keywords):
                counts[tone] += 1
        if not counts:
            counts["neutral"] += 1
        return counts


brand_voice_service = BrandVoiceService()

__all__ = ["BrandVoiceService", "brand_voice_service"]
