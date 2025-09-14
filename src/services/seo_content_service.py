import random
import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import os

from textblob import TextBlob
import textstat
import language_tool_python

class SEOContentService:
    """Service for generating SEO-optimized social media content for real estate"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "seo_keywords.json")
        )
        self._load_config()
        # Hashtag trend scores for weighting selections
        self.trend_scores: Dict[str, float] = {}
        self.refresh_trend_scores()
        # default region used when no specific location is supplied
        self.default_region = "Windsor-Essex, Ontario"

        # Content templates for different post types
        self.content_templates = {
            'property_showcase': {
                'hooks': [
                    "🏡 Just listed in {location}!",
                    "✨ New on the market:",
                    "🔥 Hot property alert!",
                    "💎 Hidden gem discovered:",
                    "🌟 Featured listing:"
                ],
                'structures': [
                    "{hook}\n\n{property_description}\n\n💰 {price_info}\n📍 {location_details}\n\n{call_to_action}",
                    "{hook}\n\n{key_features}\n\n{neighborhood_info}\n\n{call_to_action}",
                    "{hook}\n\n{property_description}\n\n{investment_angle}\n\n{call_to_action}"
                ]
            },
            'market_update': {
                'hooks': [
                    "📊 {location} Market Update:",
                    "📈 What's happening in {location}:",
                    "🏘️ {location} Real Estate Trends:",
                    "💹 Market Insight for {location}:",
                    "📋 Your {location} Market Report:"
                ],
                'structures': [
                    "{hook}\n\n{market_data}\n\n{analysis}\n\n{advice}\n\n{call_to_action}",
                    "{hook}\n\n{trend_summary}\n\n{impact_explanation}\n\n{call_to_action}"
                ]
            },
            'educational': {
                'hooks': [
                    "💡 Home Buying Tip:",
                    "🎓 Real Estate Education:",
                    "📚 Did you know?",
                    "🤔 Wondering about {topic}?",
                    "💭 Common question:"
                ],
                'structures': [
                    "{hook}\n\n{educational_content}\n\n{practical_application}\n\n{call_to_action}",
                    "{hook}\n\n{myth_busting}\n\n{correct_information}\n\n{call_to_action}"
                ]
            },
            'community': {
                'hooks': [
                    "❤️ Love our {location} community!",
                    "🌟 Spotlight on {location}:",
                    "🏘️ Why {location} is special:",
                    "📍 Local favorite in {location}:",
                    "🎉 Celebrating {location}:"
                ],
                'structures': [
                    "{hook}\n\n{community_feature}\n\n{personal_connection}\n\n{call_to_action}",
                    "{hook}\n\n{local_business_spotlight}\n\n{community_value}\n\n{call_to_action}"
                ]
            }
        }
        
        # Call-to-action templates
        self.cta_templates = {
            'property_inquiry': [
                "DM me for more details! 📩",
                "Ready to schedule a viewing? Let's chat! 💬",
                "Questions about this property? I'm here to help! 🤝",
                "Want to know more? Send me a message! 📱",
                "Interested? Let's discuss your options! 💼"
            ],
            'market_consultation': [
                "Want a personalized market analysis? Let's connect! 📊",
                "Curious about your home's value? Let's talk! 🏡",
                "Ready to explore the market? I'm here to guide you! 🗺️",
                "Need market insights for your area? Reach out! 📈",
                "Planning your next move? Let's strategize! 🎯"
            ],
            'general_engagement': [
                "What are your thoughts? Share in the comments! 💭",
                "Have questions? Drop them below! ⬇️",
                "Tag someone who needs to see this! 👥",
                "Save this post for later! 🔖",
                "Share your experience in the comments! 💬"
            ]
        }
        
        # Best posting times by platform (Eastern Time)
        self.optimal_posting_times = {
            'instagram': {
                'weekday': [(11, 13), (18, 20)],  # 11AM-1PM, 6PM-8PM
                'weekend': [(10, 12)]  # 10AM-12PM
            },
            'facebook': {
                'weekday': [(9, 10), (15, 16)],  # 9AM-10AM, 3PM-4PM
                'weekend': [(12, 13)]  # 12PM-1PM
            }
        }

    def _load_config(self) -> None:
        """Load keyword and hashtag configuration from JSON file."""
        with open(self.config_path, "r") as f:
            config = json.load(f)

        self.location_keywords = config.get("location_keywords", {})
        self.real_estate_keywords = config.get("real_estate_keywords", {})
        self.hashtag_strategies = config.get("hashtag_strategies", {})
        self.hashtags = config.get("hashtags", {})

    def reload_config(self) -> None:
        """Reload configuration from disk at runtime."""
        self._load_config()
    
    def generate_seo_optimized_content(self, 
                                     content_type: str,
                                     platform: str = 'instagram',
                                     location: str = None,
                                     custom_data: Dict = None) -> Dict:
        """
        Generate SEO-optimized social media content
        
        Args:
            content_type: Type of content ('property_showcase', 'market_update', 'educational', 'community')
            platform: Target platform ('instagram', 'facebook')
            location: Specific location to focus on
            custom_data: Additional data for content generation
        
        Returns:
            Dict containing optimized content, hashtags, and metadata
        """
        
        # Select location if not provided and ensure Windsor-Essex region context
        if not location:
            location = self.default_region
        elif 'windsor' not in location.lower() and 'essex' not in location.lower():
            location = f"{location}, {self.default_region}"
        
        # Generate main content
        content = self._generate_content_body(content_type, location, custom_data or {})
        
        # Generate SEO-optimized hashtags
        hashtags = self._generate_hashtags(content_type, platform, location)
        
        # Generate image prompt
        image_prompt = self._generate_image_prompt(content_type, location, custom_data or {})
        
        # Calculate optimal posting time
        optimal_time = self._get_optimal_posting_time(platform)
        
        # Generate SEO metadata
        seo_metadata = self._generate_seo_metadata(content, location, content_type)
        
        return {
            'content': content,
            'hashtags': hashtags,
            'image_prompt': image_prompt,
            'platform': platform,
            'content_type': content_type,
            'location': location,
            'optimal_posting_time': optimal_time,
            'seo_metadata': seo_metadata,
            'character_count': len(content),
            'estimated_engagement_score': self._calculate_engagement_score(content, hashtags, platform)
        }
    
    def _generate_content_body(self, content_type: str, location: str, custom_data: Dict) -> str:
        """Generate the main content body based on type and location"""
        
        template = self.content_templates.get(content_type, self.content_templates['community'])
        
        # Select random hook and structure
        hook = random.choice(template['hooks']).format(location=location, **custom_data)
        structure = random.choice(template['structures'])
        
        # Generate content based on type
        if content_type == 'property_showcase':
            content_data = self._generate_property_content(location, custom_data)
        elif content_type == 'market_update':
            content_data = self._generate_market_content(location, custom_data)
        elif content_type == 'educational':
            content_data = self._generate_educational_content(location, custom_data)
        else:  # community
            content_data = self._generate_community_content(location, custom_data)
        
        # Add hook to content data
        content_data['hook'] = hook
        
        # Add appropriate call-to-action
        if content_type == 'property_showcase':
            cta_type = 'property_inquiry'
        elif content_type == 'market_update':
            cta_type = 'market_consultation'
        else:
            cta_type = 'general_engagement'
        
        content_data['call_to_action'] = random.choice(self.cta_templates[cta_type])
        
        # Format the content
        try:
            formatted_content = structure.format(**content_data)
        except KeyError:
            # Fallback if some keys are missing
            formatted_content = f"{hook}\n\n{content_data.get('description', 'Great opportunity in ' + location + '!')}\n\n{content_data['call_to_action']}"
        
        return formatted_content
    
    def _generate_property_content(self, location: str, custom_data: Dict) -> Dict:
        """Generate property showcase content"""
        
        property_types = ['family home', 'condo', 'townhouse', 'luxury home', 'starter home', 'investment property']
        features = ['updated kitchen', 'spacious bedrooms', 'beautiful backyard', 'modern finishes', 'great location', 'move-in ready']
        
        property_type = custom_data.get('property_type', random.choice(property_types))
        
        return {
            'property_description': f"Beautiful {property_type} in the heart of {location}. This property offers everything you're looking for in your next home.",
            'key_features': f"✨ Key features:\n• {random.choice(features).title()}\n• {random.choice(features).title()}\n• {random.choice(features).title()}",
            'price_info': custom_data.get('price', 'Competitively priced'),
            'location_details': f"Located in desirable {location}, close to amenities and transportation.",
            'neighborhood_info': f"{location} offers the perfect blend of community charm and urban convenience.",
            'investment_angle': f"Excellent investment opportunity in {location}'s growing market."
        }
    
    def _generate_market_content(self, location: str, custom_data: Dict) -> Dict:
        """Generate market update content"""
        
        trends = ['steady growth', 'increased activity', 'strong demand', 'balanced market', 'buyer opportunities']
        
        return {
            'market_data': f"Recent data shows {random.choice(trends)} in the {location} real estate market.",
            'trend_summary': f"The {location} market continues to show positive indicators for both buyers and sellers.",
            'analysis': f"What this means: {location} remains an attractive market for real estate investment and homeownership.",
            'impact_explanation': f"These trends indicate continued stability and growth potential in {location}.",
            'advice': "Now is a great time to explore your options in this market."
        }
    
    def _generate_educational_content(self, location: str, custom_data: Dict) -> Dict:
        """Generate educational content"""
        
        topics = ['home inspection', 'mortgage pre-approval', 'market timing', 'property valuation', 'negotiation strategies']
        topic = custom_data.get('topic', random.choice(topics))
        
        return {
            'educational_content': f"Understanding {topic} is crucial for success in the {location} real estate market.",
            'practical_application': f"Here's how this applies to your {location} property search or sale.",
            'myth_busting': f"Common myth: {topic} isn't important in smaller markets like {location}.",
            'correct_information': f"Reality: {topic} is just as important in {location} as anywhere else."
        }
    
    def _generate_community_content(self, location: str, custom_data: Dict) -> Dict:
        """Generate community-focused content"""
        
        community_features = ['local businesses', 'parks and recreation', 'schools', 'cultural events', 'dining scene']
        feature = custom_data.get('feature', random.choice(community_features))
        
        return {
            'community_feature': f"One of the things I love most about {location} is our amazing {feature}.",
            'local_business_spotlight': f"Shoutout to the incredible {feature} that make {location} special!",
            'personal_connection': f"As a local real estate professional, I'm proud to call {location} home.",
            'community_value': f"This is what makes {location} such a desirable place to live and invest."
        }

    def refresh_trend_scores(self, source: Optional[str] = None) -> None:
        """Refresh hashtag trend scores from an API or cached dataset.

        Args:
            source: Optional URL or file path to JSON mapping hashtags to scores.
                   If omitted, attempts to load from the bundled data directory.
        """
        try:
            if source and source.startswith("http"):
                from urllib.request import urlopen
                with urlopen(source) as response:  # nosec B310
                    data = json.loads(response.read().decode())
            else:
                default_path = source or os.path.join(
                    os.path.dirname(__file__), '..', 'data', 'trend_scores.json'
                )
                with open(default_path, 'r') as f:
                    data = json.load(f)
            # normalize keys to maintain consistency
            self.trend_scores = {k: float(v) for k, v in data.items()}
        except Exception:
            # If fetching fails, keep existing scores or fall back to empty
            self.trend_scores = getattr(self, 'trend_scores', {})
    
    def _generate_hashtags(self, content_type: str, platform: str, location: str) -> List[str]:
        """Generate SEO-optimized hashtags for the content"""
        
        strategy = self.hashtag_strategies[platform]
        min_count, max_count = strategy['count']
        target_count = random.randint(min_count, max_count)

        # Calculate distribution
        high_count = int(target_count * strategy['mix']['high_volume'])
        medium_count = int(target_count * strategy['mix']['medium_volume'])
        niche_count = target_count - high_count - medium_count

        def weighted_sample(tags: List[str], count: int) -> List[str]:
            """Sample hashtags without replacement weighted by trend scores."""
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

        # Add high volume hashtags
        selected_hashtags.extend(weighted_sample(self.hashtags['high_volume'], high_count))

        # Add medium volume hashtags
        selected_hashtags.extend(weighted_sample(self.hashtags['medium_volume'], medium_count))

        # Add niche hashtags
        selected_hashtags.extend(weighted_sample(self.hashtags['niche'], niche_count))
        
        # Add location-specific hashtags using only the city portion
        location_clean = location.split(',')[0].replace(' ', '').replace('-', '')
        location_hashtags = [f"#{location_clean}", f"#{location_clean}RealEstate"]

        # Always prioritize Windsor-Essex regional hashtags
        region_hashtags = ['#WindsorEssex', '#WindsorOntario', '#EssexCounty']
        
        # Add content-type specific hashtags
        if content_type == 'property_showcase':
            selected_hashtags.extend(['#JustListed', '#NewListing', '#PropertyShowcase'])
        elif content_type == 'market_update':
            selected_hashtags.extend(['#MarketUpdate', '#RealEstateNews', '#MarketTrends'])
        elif content_type == 'educational':
            selected_hashtags.extend(['#RealEstateTips', '#HomeBuyingTips', '#RealEstateEducation'])
        else:  # community
            selected_hashtags.extend(['#CommunityLove', '#LocalBusiness', '#Neighborhood'])
        
        # Combine, deduplicate, and order by trend score
        all_hashtags = list(dict.fromkeys(selected_hashtags + location_hashtags + region_hashtags))
        all_hashtags.sort(key=lambda tag: self.trend_scores.get(tag, 1.0), reverse=True)

        # Trim to target count
        return all_hashtags[:target_count]
    
    def _generate_image_prompt(self, content_type: str, location: str, custom_data: Dict) -> str:
        """Generate AI image prompt optimized for the content"""
        
        base_prompts = {
            'property_showcase': [
                "Professional real estate photography of a beautiful {property_type} exterior in {location}, Ontario, Canada",
                "High-quality interior shot of a modern {room} with natural lighting, real estate photography style",
                "Stunning curb appeal photo of a well-maintained home in {location}, professional real estate marketing"
            ],
            'market_update': [
                "Professional infographic showing real estate market trends for {location}, clean modern design",
                "Aerial view of {location} neighborhood showing residential properties, professional photography",
                "Modern real estate market analysis chart with {location} data, professional business style"
            ],
            'educational': [
                "Professional real estate consultation scene with agent and clients reviewing documents",
                "Clean, modern infographic explaining {topic} for real estate, educational style",
                "Professional real estate office setting with educational materials and charts"
            ],
            'community': [
                "Beautiful community scene in {location}, Ontario showing local businesses and residents",
                "Scenic view of {location} neighborhood highlighting community features and amenities",
                "Local {location} landmark or community gathering place, professional photography"
            ]
        }
        
        prompt_template = random.choice(base_prompts[content_type])
        
        # Fill in variables
        prompt_data = {
            'location': location,
            'property_type': custom_data.get('property_type', 'family home'),
            'room': custom_data.get('room', 'living room'),
            'topic': custom_data.get('topic', 'home buying process')
        }
        
        base_prompt = prompt_template.format(**prompt_data)
        
        # Add quality enhancers
        quality_enhancers = [
            "professional photography",
            "high resolution",
            "excellent lighting",
            "commercial quality",
            "sharp focus",
            "real estate marketing style"
        ]
        
        enhanced_prompt = f"{base_prompt}, {', '.join(random.sample(quality_enhancers, 3))}"
        
        return enhanced_prompt
    
    def _get_optimal_posting_time(self, platform: str) -> str:
        """Calculate optimal posting time for the platform"""
        
        now = datetime.now()
        is_weekend = now.weekday() >= 5
        
        time_ranges = self.optimal_posting_times[platform]['weekend' if is_weekend else 'weekday']
        
        # Select random time range
        start_hour, end_hour = random.choice(time_ranges)
        
        # Calculate next optimal time
        target_hour = random.randint(start_hour, end_hour - 1)
        target_minute = random.choice([0, 15, 30, 45])
        
        # If the time has passed today, schedule for tomorrow
        target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if target_time <= now:
            target_time += timedelta(days=1)
        
        return target_time.strftime('%Y-%m-%d %H:%M:%S')
    
    def _generate_seo_metadata(self, content: str, location: str, content_type: str) -> Dict:
        """Generate SEO metadata for the content"""

        # Extract keywords from content
        content_lower = content.lower()
        words = content_lower.split()
        total_words = len(words)

        # Calculate keyword density percentages
        keyword_density = {}
        total_keyword_occurrences = 0
        for category, keywords in self.real_estate_keywords.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                count = len(re.findall(pattern, content_lower))
                if count > 0 and total_words > 0:
                    density = (count / total_words) * 100
                    keyword_density[keyword] = round(density, 2)
                    total_keyword_occurrences += count

        # Generate meta description
        meta_description = f"Real estate content for {location}. {content[:100]}..."

        # Calculate SEO score and additional metrics
        seo_score, sentiment, grammar_errors = self._calculate_seo_score(
            content, location, content_type
        )

        return {
            'keyword_density': keyword_density,
            'meta_description': meta_description,
            'primary_keywords': list(keyword_density.keys())[:5],
            'location_mentions': len(re.findall(r'\b' + re.escape(location.lower()) + r'\b', content_lower)),
            'seo_score': seo_score,
            'content_length': len(content),
            'readability_score': self._calculate_readability_score(content),
            'sentiment_polarity': sentiment,
            'grammar_errors': grammar_errors,
            'overall_keyword_density': round((total_keyword_occurrences / total_words) * 100, 2) if total_words > 0 else 0,
        }
    
    def _calculate_seo_score(self, content: str, location: str, content_type: str) -> Tuple[float, float, int]:
        """Calculate SEO score and related metrics for the content."""

        score = 0.0
        content_lower = content.lower()
        words = content_lower.split()
        total_words = len(words)

        # Location mention (20 points)
        if location.lower() in content_lower:
            score += 20

        # Keyword density (30 points) - optimal around 2%
        keyword_occurrences = 0
        for keywords in self.real_estate_keywords.values():
            for keyword in keywords:
                keyword_occurrences += len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', content_lower))
        keyword_density = (keyword_occurrences / total_words) * 100 if total_words > 0 else 0
        score += max(0, 30 - abs(keyword_density - 2) * 15)  # penalize deviation from 2%

        # Readability (20 points) using Flesch Reading Ease
        readability = textstat.flesch_reading_ease(content)
        score += max(min(readability, 100), 0) * 0.2

        # Sentiment impact (-10 to +10)
        polarity = TextBlob(content).sentiment.polarity
        score += polarity * 10

        # Grammar check penalty (up to -20)
        try:
            tool = language_tool_python.LanguageTool('en-US')
            grammar_errors = len(tool.check(content))
        except Exception:
            grammar_errors = 0
        score -= min(grammar_errors * 2, 20)

        # Content length bonus (up to 10)
        content_length = len(content)
        if 50 <= content_length <= 300:
            score += 10

        final_score = max(min(score, 100.0), 0.0)
        return final_score, polarity, grammar_errors
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability using Flesch Reading Ease."""

        try:
            return textstat.flesch_reading_ease(content)
        except Exception:
            return 0.0
    
    def _calculate_engagement_score(self, content: str, hashtags: List[str], platform: str) -> float:
        """Calculate estimated engagement score"""
        
        score = 0.0
        
        # Content quality (40 points)
        seo_score, _, _ = self._calculate_seo_score(content, 'Windsor', 'general')
        score += (seo_score / 100) * 40
        
        # Hashtag optimization (30 points)
        hashtag_count = len(hashtags)
        optimal_range = self.hashtag_strategies[platform]['count']
        
        if optimal_range[0] <= hashtag_count <= optimal_range[1]:
            score += 30
        else:
            # Penalty for too few or too many hashtags
            distance = min(abs(hashtag_count - optimal_range[0]), abs(hashtag_count - optimal_range[1]))
            score += max(30 - (distance * 5), 0)
        
        # Platform optimization (20 points)
        if platform == 'instagram':
            # Instagram favors visual content and stories
            if any(word in content.lower() for word in ['photo', 'image', 'see', 'look', 'view']):
                score += 10
            if len(content) <= 300:  # Optimal length for Instagram
                score += 10
        else:  # Facebook
            # Facebook favors longer, engaging content
            if len(content) >= 100:
                score += 10
            if '?' in content:  # Questions drive engagement
                score += 10
        
        # Call to action (10 points)
        cta_indicators = ['dm', 'message', 'contact', 'comment', 'share', 'tag']
        if any(indicator in content.lower() for indicator in cta_indicators):
            score += 10

        return min(score, 100.0)

    def analyze_keywords(self, keywords: List[str]) -> Dict:
        """Analyze and score provided keywords.

        This normalizes the given keywords, counts their frequency and suggests
        related terms based on the service's internal keyword lists.

        Args:
            keywords: List of raw keyword strings.

        Returns:
            Dictionary with normalized input, frequency scores and suggested
            related keywords.
        """

        if not isinstance(keywords, list):
            raise ValueError("Keywords must be provided as a list")

        normalized = [re.sub(r"\s+", " ", kw).strip().lower()
                      for kw in keywords if isinstance(kw, str) and kw.strip()]
        if not normalized:
            raise ValueError("No valid keywords supplied")

        counts = Counter(normalized)
        unique_input = list(dict.fromkeys(normalized))

        all_known = set(self.real_estate_keywords['primary'] +
                        self.real_estate_keywords['long_tail'] +
                        self.location_keywords['primary'] +
                        self.location_keywords['neighborhoods'])

        suggestions = []
        for kw in unique_input:
            related = [term for term in all_known
                       if kw in term.lower() and term.lower() not in counts]
            suggestions.extend(related)

        suggestions = list(dict.fromkeys(suggestions))

        return {
            'input': unique_input,
            'suggestions': suggestions,
            'scores': dict(counts)
        }

    def keyword_density(self, text: str, keyword: str) -> Dict:
        """Calculate keyword density for given text and keyword.

 codex/create-seo-aware-content-generation-workflow-puwamt
        This helper powers the `/api/seo-tools/keyword-density` endpoint and is
        used by the social media generator to provide real-time SEO feedback.


 main
        Args:
            text: Content to analyze.
            keyword: Target keyword or phrase.

        Returns:
            Dictionary with keyword count, total words, density percentage and
            basic suggestion about the density.
        """

 codex/create-seo-aware-content-generation-workflow-puwamt

 codex/create-seo-aware-content-generation-workflow-begzfl
 main
        if not text or not keyword or not keyword.strip():
            raise ValueError("Text and keyword are required")

        keyword = keyword.strip()
        text_lower = text.lower()
        keyword_lower = keyword.lower()

        words = re.findall(r"\w+", text_lower)
        total_words = len(words)
        pattern = r"\b" + re.escape(keyword_lower) + r"\b"
        keyword_count = len(re.findall(pattern, text_lower))
 codex/create-seo-aware-content-generation-workflow-puwamt


        if not text or not keyword:
            raise ValueError("Text and keyword are required")

        words = re.findall(r"\w+", text.lower())
        total_words = len(words)
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
        keyword_count = len(re.findall(pattern, text.lower()))
 main
 main
        density = (
            round((keyword_count / total_words) * 100, 2)
            if total_words > 0
            else 0.0
        )

        if density < 1:
            suggestion = (
                f"Try including the keyword '{keyword}' one or two more times "
                "naturally in the text."
            )
        elif density > 3:
            suggestion = (
                f"Your keyword density is a bit high. Consider replacing one "
                f"instance of '{keyword}' with a synonym to avoid sounding "
                "repetitive."
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
    
    def generate_content_calendar(self, days: int = 30, platform: str = 'instagram') -> List[Dict]:
        """Generate a content calendar with SEO-optimized posts"""
        
        calendar = []
        content_types = ['property_showcase', 'market_update', 'educational', 'community']
        
        # Content distribution strategy
        type_weights = {
            'property_showcase': 0.4,  # 40% property content
            'market_update': 0.2,      # 20% market updates
            'educational': 0.25,       # 25% educational content
            'community': 0.15          # 15% community content
        }
        
        for day in range(days):
            post_date = datetime.now() + timedelta(days=day)
            
            # Skip some days to avoid over-posting
            if random.random() < 0.3:  # 30% chance to skip a day
                continue
            
            # Select content type based on weights
            content_type = random.choices(
                list(type_weights.keys()),
                weights=list(type_weights.values())
            )[0]
            
            # Generate location
            location = random.choice(self.location_keywords['primary'])
            
            # Generate content
            content_data = self.generate_seo_optimized_content(
                content_type=content_type,
                platform=platform,
                location=location
            )
            
            # Add scheduling information
            content_data['scheduled_date'] = post_date.strftime('%Y-%m-%d')
            content_data['day_of_week'] = post_date.strftime('%A')
            
            calendar.append(content_data)
        
        return calendar
    
    def optimize_existing_content(self, content: str, platform: str = 'instagram') -> Dict:
        """Optimize existing content for better SEO and engagement"""
        
        # Analyze current content
        current_score, _, _ = self._calculate_seo_score(content, 'Windsor', 'general')
        
        # Suggest improvements
        suggestions = []
        content_lower = content.lower()
        
        # Check for location mentions
        location_mentioned = any(loc.lower() in content_lower for loc in self.location_keywords['primary'])
        if not location_mentioned:
            suggestions.append("Add location-specific keywords (Windsor, Essex County, etc.)")
        
        # Check for real estate keywords
        re_keywords_found = any(keyword.lower() in content_lower 
                               for keywords in self.real_estate_keywords.values() 
                               for keyword in keywords)
        if not re_keywords_found:
            suggestions.append("Include real estate-specific keywords")
        
        # Check for call to action
        cta_present = any(cta in content_lower for cta in ['dm', 'message', 'contact', 'call'])
        if not cta_present:
            suggestions.append("Add a clear call-to-action")
        
        # Check content length
        if len(content) < 50:
            suggestions.append("Expand content for better engagement (aim for 100-300 characters)")
        elif len(content) > 500:
            suggestions.append("Consider shortening content for better readability")
        
        # Generate optimized hashtags
        optimized_hashtags = self._generate_hashtags('general', platform, 'Windsor')
        
        return {
            'original_content': content,
            'current_seo_score': current_score,
            'suggestions': suggestions,
            'optimized_hashtags': optimized_hashtags,
            'estimated_improvement': min(100 - current_score, 30)  # Potential improvement
        }

# Global instance
seo_content_service = SEOContentService()

