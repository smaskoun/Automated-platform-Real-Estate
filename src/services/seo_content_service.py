"""SEO content generation and analysis utilities."""

from __future__ import annotations

import json
import logging
import os
import random
import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import textstat
from textblob import TextBlob

try:  # language_tool_python may require a remote server – only load when available
    import language_tool_python  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    language_tool_python = None

LOGGER = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")


class SEOContentService:
    """Service for generating and analysing SEO friendly social media content."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(DATA_DIR, "seo_keywords.json")
        self._load_config()
        self.trend_scores: Dict[str, float] = {}
        self.refresh_trend_scores()
        self.default_region = "Windsor-Essex, Ontario"

        self._grammar_tool = None
        self._grammar_check_enabled = False
        if (
            os.getenv("ENABLE_GRAMMAR_CHECK", "").lower() in {"1", "true", "yes"}
            and language_tool_python is not None
        ):
            try:
                tool_url = os.getenv("LANGUAGETOOL_URL")
                if tool_url:
                    self._grammar_tool = language_tool_python.LanguageTool(
                        "en-US", config={"url": tool_url}
                    )
                else:
                    self._grammar_tool = language_tool_python.LanguageTool("en-US")
                self._grammar_check_enabled = True
            except Exception as exc:  # pragma: no cover - depends on environment
                LOGGER.warning("Grammar checking disabled: %s", exc)
                self._grammar_tool = None
                self._grammar_check_enabled = False

        self.content_templates = {
            "property_showcase": {
                "hooks": [
                    "🏡 Just listed in {location}!",
                    "✨ New on the market:",
                    "🔥 Hot property alert!",
                    "💎 Hidden gem discovered:",
                    "🌟 Featured listing:",
                ],
                "structures": [
                    "{hook}\n\n{property_description}\n\n💰 {price_info}\n📍 {location_details}\n\n{call_to_action}",
                    "{hook}\n\n{key_features}\n\n{neighborhood_info}\n\n{call_to_action}",
                    "{hook}\n\n{property_description}\n\n{investment_angle}\n\n{call_to_action}",
                ],
            },
            "market_update": {
                "hooks": [
                    "📊 {location} Market Update:",
                    "📈 What's happening in {location}:",
                    "🏘️ {location} Real Estate Trends:",
                    "💹 Market Insight for {location}:",
                    "📋 Your {location} Market Report:",
                ],
                "structures": [
                    "{hook}\n\n{market_data}\n\n{analysis}\n\n{advice}\n\n{call_to_action}",
                    "{hook}\n\n{trend_summary}\n\n{impact_explanation}\n\n{call_to_action}",
                ],
            },
            "educational": {
                "hooks": [
                    "💡 Home Buying Tip:",
                    "🎓 Real Estate Education:",
                    "📚 Did you know?",
                    "🤔 Wondering about {topic}?",
                    "💭 Common question:",
                ],
                "structures": [
                    "{hook}\n\n{educational_content}\n\n{practical_application}\n\n{call_to_action}",
                    "{hook}\n\n{myth_busting}\n\n{correct_information}\n\n{call_to_action}",
                ],
            },
            "community": {
                "hooks": [
                    "❤️ Love our {location} community!",
                    "🌟 Spotlight on {location}:",
                    "🏘️ Why {location} is special:",
                    "📍 Local favorite in {location}:",
                    "🎉 Celebrating {location}:",
                ],
                "structures": [
                    "{hook}\n\n{community_feature}\n\n{personal_connection}\n\n{call_to_action}",
                    "{hook}\n\n{local_business_spotlight}\n\n{community_value}\n\n{call_to_action}",
                ],
            },
        }

        self.cta_templates = {
            "property_inquiry": [
                "DM me for more details! 📩",
                "Ready to schedule a viewing? Let's chat! 💬",
                "Questions about this property? I'm here to help! 🤝",
                "Want to know more? Send me a message! 📱",
                "Interested? Let's discuss your options! 💼",
            ],
            "market_consultation": [
                "Want a personalized market analysis? Let's connect! 📊",
                "Curious about your home's value? Let's talk! 🏡",
                "Ready to explore the market? I'm here to guide you! 🗺️",
                "Need market insights for your area? Reach out! 📈",
                "Planning your next move? Let's strategize! 🎯",
            ],
            "general_engagement": [
                "What are your thoughts? Share in the comments! 💭",
                "Have questions? Drop them below! ⬇️",
                "Tag someone who needs to see this! 👥",
                "Save this post for later! 🔖",
                "Share your experience in the comments! 💬",
            ],
        }

        self.optimal_posting_times = {
            "instagram": {
                "weekday": [(11, 13), (18, 20)],
                "weekend": [(10, 12)],
            },
            "facebook": {
                "weekday": [(9, 10), (15, 16)],
                "weekend": [(12, 13)],
            },
        }

    # ------------------------------------------------------------------
    # Configuration and content generation helpers
    # ------------------------------------------------------------------
    def _load_config(self) -> None:
        with open(self.config_path, "r", encoding="utf-8") as fh:
            config = json.load(fh)

        self.location_keywords = config.get("location_keywords", {})
        self.real_estate_keywords = config.get("real_estate_keywords", {})
        self.hashtag_strategies = config.get("hashtag_strategies", {})
        self.hashtags = config.get("hashtags", {})

    def reload_config(self) -> None:
        self._load_config()

    def refresh_trend_scores(self, source: Optional[str] = None) -> None:
        try:
            if source and source.startswith("http"):
                from urllib.request import urlopen

                with urlopen(source) as response:  # nosec B310
                    data = json.loads(response.read().decode())
            else:
                default_path = source or os.path.join(DATA_DIR, "trend_scores.json")
                with open(default_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            self.trend_scores = {k: float(v) for k, v in data.items()}
        except Exception:
            self.trend_scores = getattr(self, "trend_scores", {})

    def generate_seo_optimized_content(
        self,
        content_type: str,
        platform: str = "instagram",
        location: Optional[str] = None,
        custom_data: Optional[Dict] = None,
    ) -> Dict:
        if not location:
            location = self.default_region
        elif "windsor" not in location.lower() and "essex" not in location.lower():
            location = f"{location}, {self.default_region}"

        custom_data = custom_data or {}

        content = self._generate_content_body(content_type, location, custom_data)
        hashtags = self._generate_hashtags(content_type, platform, location)
        image_prompt = self._generate_image_prompt(content_type, location, custom_data)
        optimal_time = self._get_optimal_posting_time(platform)
        seo_metadata = self._generate_seo_metadata(content, location, content_type)

        return {
            "content": content,
            "hashtags": hashtags,
            "image_prompt": image_prompt,
            "platform": platform,
            "content_type": content_type,
            "location": location,
            "optimal_posting_time": optimal_time,
            "seo_metadata": seo_metadata,
            "character_count": len(content),
            "estimated_engagement_score": self._calculate_engagement_score(content, hashtags, platform),
        }

    def _generate_content_body(self, content_type: str, location: str, custom_data: Dict) -> str:
        template = self.content_templates.get(content_type, self.content_templates["community"])
        hook = random.choice(template["hooks"]).format(location=location, **custom_data)
        structure = random.choice(template["structures"])

        if content_type == "property_showcase":
            content_data = self._generate_property_content(location, custom_data)
            cta_type = "property_inquiry"
        elif content_type == "market_update":
            content_data = self._generate_market_content(location, custom_data)
            cta_type = "market_consultation"
        elif content_type == "educational":
            content_data = self._generate_educational_content(location, custom_data)
            cta_type = "general_engagement"
        else:
            content_data = self._generate_community_content(location, custom_data)
            cta_type = "general_engagement"

        content_data["hook"] = hook
        content_data["call_to_action"] = random.choice(self.cta_templates[cta_type])

        try:
            formatted_content = structure.format(**content_data)
        except KeyError:
            fallback = content_data.get("description") or f"Great opportunity in {location}!"
            formatted_content = f"{hook}\n\n{fallback}\n\n{content_data['call_to_action']}"
        return formatted_content

    def _generate_property_content(self, location: str, custom_data: Dict) -> Dict:
        property_types = [
            "family home",
            "condo",
            "townhouse",
            "luxury home",
            "starter home",
            "investment property",
        ]
        features = [
            "updated kitchen",
            "spacious bedrooms",
            "beautiful backyard",
            "modern finishes",
            "great location",
            "move-in ready",
        ]
        property_type = custom_data.get("property_type", random.choice(property_types))
        return {
            "property_description": (
                f"Beautiful {property_type} in the heart of {location}. "
                "This property offers everything you're looking for in your next home."
            ),
            "key_features": (
                "✨ Key features:\n"
                f"• {random.choice(features).title()}\n"
                f"• {random.choice(features).title()}\n"
                f"• {random.choice(features).title()}"
            ),
            "price_info": custom_data.get("price", "Competitively priced"),
            "location_details": f"Located in desirable {location}, close to amenities and transportation.",
            "neighborhood_info": f"{location} offers the perfect blend of community charm and urban convenience.",
            "investment_angle": f"Excellent investment opportunity in {location}'s growing market.",
        }

    def _generate_market_content(self, location: str, custom_data: Dict) -> Dict:
        trends = [
            "steady growth",
            "increased activity",
            "strong demand",
            "balanced market",
            "buyer opportunities",
        ]
        return {
            "market_data": f"Recent data shows {random.choice(trends)} in the {location} real estate market.",
            "trend_summary": f"The {location} market continues to show positive indicators for both buyers and sellers.",
            "analysis": (
                f"What this means: {location} remains an attractive market for real estate investment and homeownership."
            ),
            "impact_explanation": f"These trends indicate continued stability and growth potential in {location}.",
            "advice": "Now is a great time to explore your options in this market.",
        }

    def _generate_educational_content(self, location: str, custom_data: Dict) -> Dict:
        topics = [
            "home inspection",
            "mortgage pre-approval",
            "market timing",
            "property valuation",
            "negotiation strategies",
        ]
        topic = custom_data.get("topic", random.choice(topics))
        return {
            "educational_content": (
                f"Understanding {topic} is crucial for success in the {location} real estate market."
            ),
            "practical_application": (
                f"Here's how this applies to your {location} property search or sale."
            ),
            "myth_busting": f"Common myth: {topic} isn't important in smaller markets like {location}.",
            "correct_information": f"Reality: {topic} is just as important in {location} as anywhere else.",
        }

    def _generate_community_content(self, location: str, custom_data: Dict) -> Dict:
        community_features = [
            "local businesses",
            "parks and recreation",
            "schools",
            "cultural events",
            "dining scene",
        ]
        feature = custom_data.get("feature", random.choice(community_features))
        return {
            "community_feature": f"One of the things I love most about {location} is our amazing {feature}.",
            "local_business_spotlight": f"Shoutout to the incredible {feature} that make {location} special!",
            "personal_connection": f"As a local real estate professional, I'm proud to call {location} home.",
            "community_value": f"This is what makes {location} such a desirable place to live and invest.",
        }

    # ------------------------------------------------------------------
    # Analysis helpers
    # ------------------------------------------------------------------
    def _generate_hashtags(self, content_type: str, platform: str, location: str) -> List[str]:
        strategy = self.hashtag_strategies.get(platform, self.hashtag_strategies.get("instagram", {}))
        min_count, max_count = strategy.get("count", (8, 12))
        target_count = random.randint(min_count, max_count)

        def weighted_sample(tags: List[str], count: int) -> List[str]:
            available = tags[:]
            weights = [self.trend_scores.get(tag, 1.0) for tag in available]
            chosen: List[str] = []
            for _ in range(min(count, len(available))):
                selection = random.choices(available, weights=weights, k=1)[0]
                idx = available.index(selection)
                chosen.append(selection)
                del available[idx]
                del weights[idx]
            return chosen

        selected_hashtags: List[str] = []
        selected_hashtags.extend(weighted_sample(self.hashtags.get("high_volume", []), target_count // 3))
        selected_hashtags.extend(weighted_sample(self.hashtags.get("medium_volume", []), target_count // 3))
        selected_hashtags.extend(weighted_sample(self.hashtags.get("niche", []), target_count - len(selected_hashtags)))

        location_clean = location.split(",")[0].replace(" ", "").replace("-", "")
        location_hashtags = [f"#{location_clean}", f"#{location_clean}RealEstate"]
        region_hashtags = ["#WindsorEssex", "#WindsorOntario", "#EssexCounty"]

        if content_type == "property_showcase":
            selected_hashtags.extend(["#JustListed", "#NewListing", "#PropertyShowcase"])
        elif content_type == "market_update":
            selected_hashtags.extend(["#MarketUpdate", "#RealEstateNews", "#MarketTrends"])
        elif content_type == "educational":
            selected_hashtags.extend(["#RealEstateTips", "#HomeBuyingTips", "#RealEstateEducation"])
        else:
            selected_hashtags.extend(["#CommunityLove", "#LocalBusiness", "#Neighborhood"])

        all_hashtags = list(dict.fromkeys(selected_hashtags + location_hashtags + region_hashtags))
        all_hashtags.sort(key=lambda tag: self.trend_scores.get(tag, 1.0), reverse=True)
        return all_hashtags[:target_count]

    def _generate_image_prompt(self, content_type: str, location: str, custom_data: Dict) -> str:
        base_prompts = {
            "property_showcase": [
                "Professional real estate photography of a beautiful {property_type} exterior in {location}, Ontario, Canada",
                "High-quality interior shot of a modern {room} with natural lighting, real estate photography style",
                "Stunning curb appeal photo of a well-maintained home in {location}, professional real estate marketing",
            ],
            "market_update": [
                "Professional infographic showing real estate market trends for {location}, clean modern design",
                "Aerial view of {location} neighborhood showing residential properties, professional photography",
                "Modern real estate market analysis chart with {location} data, professional business style",
            ],
            "educational": [
                "Professional real estate consultation scene with agent and clients reviewing documents",
                "Clean, modern infographic explaining {topic} for real estate, educational style",
                "Professional real estate office setting with educational materials and charts",
            ],
            "community": [
                "Beautiful community scene in {location}, Ontario showing local businesses and residents",
                "Scenic view of {location} neighborhood highlighting community features and amenities",
                "Local {location} landmark or community gathering place, professional photography",
            ],
        }
        prompt_template = random.choice(base_prompts[content_type])
        prompt_data = {
            "location": location,
            "property_type": custom_data.get("property_type", "family home"),
            "room": custom_data.get("room", "living room"),
            "topic": custom_data.get("topic", "home buying process"),
        }
        base_prompt = prompt_template.format(**prompt_data)
        quality_enhancers = [
            "professional photography",
            "high resolution",
            "excellent lighting",
            "commercial quality",
            "sharp focus",
            "real estate marketing style",
        ]
        return f"{base_prompt}, {', '.join(random.sample(quality_enhancers, 3))}"

    def _get_optimal_posting_time(self, platform: str) -> str:
        now = datetime.now()
        is_weekend = now.weekday() >= 5
        time_ranges = self.optimal_posting_times.get(platform, self.optimal_posting_times["instagram"])
        ranges = time_ranges["weekend" if is_weekend else "weekday"]
        start_hour, end_hour = random.choice(ranges)
        target_hour = random.randint(start_hour, max(start_hour, end_hour - 1))
        target_minute = random.choice([0, 15, 30, 45])
        target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if target_time <= now:
            target_time += timedelta(days=1)
        return target_time.strftime("%Y-%m-%d %H:%M:%S")

    def _generate_seo_metadata(self, content: str, location: str, content_type: str) -> Dict:
        content_lower = content.lower()
        words = content_lower.split()
        total_words = len(words)

        keyword_density: Dict[str, float] = {}
        total_keyword_occurrences = 0
        for category, keywords in self.real_estate_keywords.items():
            for keyword in keywords:
                pattern = r"\\b" + re.escape(keyword.lower()) + r"\\b"
                count = len(re.findall(pattern, content_lower))
                if count > 0 and total_words > 0:
                    density = (count / total_words) * 100
                    keyword_density[keyword] = round(density, 2)
                    total_keyword_occurrences += count

        meta_description = f"Real estate content for {location}. {content[:100]}..."
        seo_score, sentiment, grammar_errors = self._calculate_seo_score(content, location, content_type)

        return {
            "keyword_density": keyword_density,
            "meta_description": meta_description,
            "primary_keywords": list(keyword_density.keys())[:5],
            "location_mentions": len(re.findall(r"\\b" + re.escape(location.lower()) + r"\\b", content_lower)),
            "seo_score": seo_score,
            "content_length": len(content),
            "readability_score": self._calculate_readability_score(content),
            "sentiment_polarity": sentiment,
            "grammar_errors": grammar_errors,
            "overall_keyword_density": round((total_keyword_occurrences / total_words) * 100, 2) if total_words else 0,
        }

    def _calculate_seo_score(self, content: str, location: str, content_type: str) -> Tuple[float, float, int]:
        score = 0.0
        content_lower = content.lower()
        words = content_lower.split()
        total_words = len(words)

        if location.lower() in content_lower:
            score += 20

        keyword_occurrences = 0
        for keywords in self.real_estate_keywords.values():
            for keyword in keywords:
                keyword_occurrences += len(re.findall(r"\\b" + re.escape(keyword.lower()) + r"\\b", content_lower))
        keyword_density = (keyword_occurrences / total_words) * 100 if total_words else 0
        score += max(0, 30 - abs(keyword_density - 2) * 15)

        readability = textstat.flesch_reading_ease(content)
        score += max(min(readability, 100), 0) * 0.2

        polarity = TextBlob(content).sentiment.polarity
        score += polarity * 10

        grammar_errors = self._count_grammar_errors(content)
        score -= min(grammar_errors * 2, 20)

        content_length = len(content)
        if 50 <= content_length <= 300:
            score += 10

        final_score = max(min(score, 100.0), 0.0)
        return final_score, polarity, grammar_errors

    def _count_grammar_errors(self, content: str) -> int:
        if not self._grammar_check_enabled or self._grammar_tool is None:
            return 0
        try:
            return len(self._grammar_tool.check(content))
        except Exception as exc:  # pragma: no cover - relies on external service
            LOGGER.warning("Disabling grammar checking after failure: %s", exc)
            self._grammar_tool = None
            self._grammar_check_enabled = False
            return 0

    @staticmethod
    def _calculate_readability_score(content: str) -> float:
        try:
            return textstat.flesch_reading_ease(content)
        except Exception:
            return 0.0

    def _calculate_engagement_score(self, content: str, hashtags: List[str], platform: str) -> float:
        score = 0.0
        seo_score, _, _ = self._calculate_seo_score(content, self.default_region, "general")
        score += (seo_score / 100) * 40

        hashtag_count = len(hashtags)
        optimal_range = self.hashtag_strategies.get(platform, {}).get("count", (8, 12))
        if optimal_range[0] <= hashtag_count <= optimal_range[1]:
            score += 30
        else:
            distance = min(
                abs(hashtag_count - optimal_range[0]),
                abs(hashtag_count - optimal_range[1]),
            )
            score += max(30 - (distance * 5), 0)

        if platform == "instagram":
            if any(word in content.lower() for word in ["photo", "image", "see", "look", "view"]):
                score += 10
            if len(content) <= 300:
                score += 10
        else:
            if len(content) >= 100:
                score += 10
            if "?" in content:
                score += 10

        if any(cta in content.lower() for cta in ["dm", "message", "contact", "comment", "share", "tag"]):
            score += 10

        return min(score, 100.0)

    # ------------------------------------------------------------------
    # Public analysis API used by routes and tests
    # ------------------------------------------------------------------
    def analyze_keywords(self, keywords: List[str]) -> Dict:
        if not isinstance(keywords, list):
            raise ValueError("Keywords must be provided as a list")

        normalized = [
            re.sub(r"\s+", " ", kw).strip().lower()
            for kw in keywords
            if isinstance(kw, str) and kw.strip()
        ]
        if not normalized:
            raise ValueError("No valid keywords supplied")

        counts = Counter(normalized)
        unique_input = list(dict.fromkeys(normalized))

        all_known = set(
            self.real_estate_keywords.get("primary", [])
            + self.real_estate_keywords.get("long_tail", [])
            + self.location_keywords.get("primary", [])
            + self.location_keywords.get("neighborhoods", [])
        )

        suggestions: List[str] = []
        for kw in unique_input:
            related = [term for term in all_known if kw in term.lower() and term.lower() not in counts]
            suggestions.extend(related)
        suggestions = list(dict.fromkeys(suggestions))

        return {
            "input": unique_input,
            "suggestions": suggestions,
            "scores": dict(counts),
        }

    def keyword_density(self, text: str, keyword: str) -> Dict:
        if not text or not keyword or not keyword.strip():
            raise ValueError("Text and keyword are required")

        keyword = keyword.strip()
        text_lower = text.lower()
        keyword_lower = keyword.lower()

        words = re.findall(r"\w+", text_lower)
        total_words = len(words)
        pattern = r"\b" + re.escape(keyword_lower) + r"\b"
        keyword_count = len(re.findall(pattern, text_lower))

        density = round((keyword_count / total_words) * 100, 2) if total_words else 0.0
        if density < 1:
            suggestion = (
                f"Try including the keyword '{keyword}' one or two more times naturally in the text."
            )
        elif density > 3:
            suggestion = (
                f"Your keyword density is a bit high. Consider replacing one instance of '{keyword}' with a synonym."
            )
        else:
            suggestion = "Good keyword usage!"

        return {
            "keyword": keyword,
            "keyword_count": keyword_count,
            "total_words": total_words,
            "keyword_density": density,
            "suggestion": suggestion,
        }

    def evaluate_posts(self, posts: List[Dict], default_platform: str = "instagram") -> Dict:
        evaluations: List[Dict] = []
        suggestion_counter: Counter = Counter()

        for post in posts:
            if not isinstance(post, dict):
                continue
            text = post.get("content") or post.get("text") or post.get("caption")
            if not text:
                continue

            platform = post.get("platform", default_platform)
            location = post.get("location") or self.default_region
            content_type = post.get("content_type", "general")

            seo_metadata = self._generate_seo_metadata(text, location, content_type)
            optimization = self.optimize_existing_content(text, platform)

            evaluation = {
                "post_id": post.get("id") or post.get("post_id"),
                "platform": platform,
                "seo_score": seo_metadata["seo_score"],
                "readability_score": seo_metadata["readability_score"],
                "sentiment_polarity": seo_metadata["sentiment_polarity"],
                "grammar_errors": seo_metadata["grammar_errors"],
                "keyword_density": seo_metadata["keyword_density"],
                "overall_keyword_density": seo_metadata["overall_keyword_density"],
                "suggestions": optimization["suggestions"],
                "optimized_hashtags": optimization["optimized_hashtags"],
                "estimated_improvement": optimization["estimated_improvement"],
                "character_count": len(text),
                "manual_source": post.get("manual_source", False),
            }
            evaluations.append(evaluation)
            for suggestion in evaluation["suggestions"]:
                suggestion_counter[suggestion] += 1

        if not evaluations:
            return {
                "evaluations": [],
                "summary": {
                    "evaluated_posts": 0,
                    "average_seo_score": 0.0,
                    "average_readability": 0.0,
                    "common_suggestions": [],
                },
            }

        average_score = sum(e["seo_score"] for e in evaluations) / len(evaluations)
        average_readability = sum(e["readability_score"] for e in evaluations) / len(evaluations)
        top_post = max(evaluations, key=lambda item: item["seo_score"])
        lowest_post = min(evaluations, key=lambda item: item["seo_score"])

        summary = {
            "evaluated_posts": len(evaluations),
            "average_seo_score": round(average_score, 2),
            "average_readability": round(average_readability, 2),
            "top_post": {
                "post_id": top_post.get("post_id"),
                "seo_score": top_post.get("seo_score"),
                "platform": top_post.get("platform"),
            },
            "lowest_post": {
                "post_id": lowest_post.get("post_id"),
                "seo_score": lowest_post.get("seo_score"),
                "platform": lowest_post.get("platform"),
            },
            "common_suggestions": [
                {"suggestion": suggestion, "count": count}
                for suggestion, count in suggestion_counter.most_common(5)
            ],
        }

        return {"evaluations": evaluations, "summary": summary}

    def generate_content_calendar(self, days: int = 30, platform: str = "instagram") -> List[Dict]:
        calendar = []
        content_types = ["property_showcase", "market_update", "educational", "community"]
        type_weights = {
            "property_showcase": 0.4,
            "market_update": 0.2,
            "educational": 0.25,
            "community": 0.15,
        }

        for day in range(days):
            post_date = datetime.now() + timedelta(days=day)
            if random.random() < 0.3:
                continue
            content_type = random.choices(list(type_weights.keys()), weights=list(type_weights.values()))[0]
            location = random.choice(self.location_keywords.get("primary", [self.default_region]))
            content_data = self.generate_seo_optimized_content(
                content_type=content_type,
                platform=platform,
                location=location,
            )
            content_data["scheduled_date"] = post_date.strftime("%Y-%m-%d")
            content_data["day_of_week"] = post_date.strftime("%A")
            calendar.append(content_data)

        return calendar

    def optimize_existing_content(self, content: str, platform: str = "instagram") -> Dict:
        current_score, _, _ = self._calculate_seo_score(content, self.default_region, "general")
        suggestions: List[str] = []
        content_lower = content.lower()

        location_mentioned = any(loc.lower() in content_lower for loc in self.location_keywords.get("primary", []))
        if not location_mentioned:
            suggestions.append("Add location-specific keywords (Windsor, Essex County, etc.)")

        re_keywords_found = any(
            keyword.lower() in content_lower
            for keywords in self.real_estate_keywords.values()
            for keyword in keywords
        )
        if not re_keywords_found:
            suggestions.append("Include real estate-specific keywords")

        cta_present = any(cta in content_lower for cta in ["dm", "message", "contact", "call"])
        if not cta_present:
            suggestions.append("Add a clear call-to-action")

        if len(content) < 50:
            suggestions.append("Expand content for better engagement (aim for 100-300 characters)")
        elif len(content) > 500:
            suggestions.append("Consider shortening content for better readability")

        optimized_hashtags = self._generate_hashtags("general", platform, self.default_region)

        return {
            "original_content": content,
            "current_seo_score": current_score,
            "suggestions": suggestions,
            "optimized_hashtags": optimized_hashtags,
            "estimated_improvement": min(100 - current_score, 30),
        }


seo_content_service = SEOContentService()

__all__ = ["SEOContentService", "seo_content_service"]
