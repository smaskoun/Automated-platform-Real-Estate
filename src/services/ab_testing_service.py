import random
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

@dataclass
class ABTestVariation:
    """Represents a single variation in an A/B test"""
    id: str
    content: str
    hashtags: List[str]
    image_prompt: str
    post_id: Optional[str] = None
    engagement_data: Optional[Dict] = None
    created_at: Optional[str] = None

@dataclass
class ABTest:
    """Represents an A/B test with multiple variations"""
    id: str
    name: str
    content_type: str
    platform: str
    variations: List[ABTestVariation]
    status: str  # 'draft', 'running', 'completed', 'paused'
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    winner_variation_id: Optional[str] = None
    confidence_level: Optional[float] = None
    created_at: Optional[str] = None

class ABTestingService:
    """Service for creating and managing A/B tests for social media content"""
    
    def __init__(self):
        self.active_tests = {}  # In production, this would be a database
        self.completed_tests = {}
        
        # Variation strategies for different content elements
        self.variation_strategies = {
            'hooks': {
                'property_showcase': [
                    "🏡 Just listed in {location}!",
                    "✨ New on the market:",
                    "🔥 Hot property alert!",
                    "💎 Hidden gem discovered:",
                    "🌟 Featured listing:",
                    "📍 Prime location available:",
                    "🏠 Dream home opportunity:",
                    "⭐ Exclusive listing:"
                ],
                'market_update': [
                    "📊 {location} Market Update:",
                    "📈 What's happening in {location}:",
                    "🏘️ {location} Real Estate Trends:",
                    "💹 Market Insight for {location}:",
                    "📋 Your {location} Market Report:",
                    "🔍 {location} Market Analysis:",
                    "📊 Latest {location} Data:",
                    "💼 {location} Investment Update:"
                ],
                'educational': [
                    "💡 Home Buying Tip:",
                    "🎓 Real Estate Education:",
                    "📚 Did you know?",
                    "🤔 Wondering about {topic}?",
                    "💭 Common question:",
                    "🧠 Pro tip:",
                    "📖 Real Estate 101:",
                    "💪 Expert advice:"
                ]
            },
            'cta_styles': {
                'direct': [
                    "DM me for more details! 📩",
                    "Call me today! 📞",
                    "Send me a message! 💬",
                    "Contact me now! 📱"
                ],
                'soft': [
                    "Questions? I'm here to help! 🤝",
                    "Want to know more? Let's chat! ☕",
                    "Curious? Reach out anytime! 😊",
                    "Happy to discuss your options! 💭"
                ],
                'urgent': [
                    "Don't miss out - contact me today! ⏰",
                    "Limited time - call now! 🚨",
                    "Act fast - message me! ⚡",
                    "Hurry - this won't last! 🏃‍♂️"
                ]
            },
            'emoji_styles': {
                'high': 0.8,  # High emoji usage
                'medium': 0.4,  # Medium emoji usage
                'low': 0.1,   # Low emoji usage
                'none': 0.0   # No emojis
            },
            'hashtag_strategies': {
                'focused': (5, 8),    # Fewer, more targeted hashtags
                'broad': (10, 15),    # More hashtags for wider reach
                'niche': (3, 6),      # Very specific, niche hashtags
                'trending': (8, 12)   # Mix of trending and specific
            }
        }
        
        # Performance metrics to track
        self.metrics = [
            'likes', 'comments', 'shares', 'saves', 'reach', 'impressions',
            'engagement_rate', 'click_through_rate'
        ]
    
    def create_ab_test(self, 
                      test_name: str,
                      base_content: Dict,
                      variation_types: List[str],
                      platform: str = 'instagram') -> ABTest:
        """
        Create a new A/B test with multiple variations
        
        Args:
            test_name: Name for the test
            base_content: Base content to create variations from
            variation_types: Types of variations to test (e.g., ['hooks', 'cta_styles'])
            platform: Target platform
        
        Returns:
            ABTest object with generated variations
        """
        test_id = str(uuid.uuid4())
        variations = []
        
        # Generate variations based on specified types
        if 'hooks' in variation_types:
            variations.extend(self._create_hook_variations(base_content, platform))
        
        if 'cta_styles' in variation_types:
            variations.extend(self._create_cta_variations(base_content, platform))
        
        if 'emoji_styles' in variation_types:
            variations.extend(self._create_emoji_variations(base_content, platform))
        
        if 'hashtag_strategies' in variation_types:
            variations.extend(self._create_hashtag_variations(base_content, platform))
        
        # If no specific variations requested, create default variations
        if not variations:
            variations = self._create_default_variations(base_content, platform)
        
        # Ensure we have at least 2 variations for A/B testing
        if len(variations) < 2:
            variations.extend(self._create_default_variations(base_content, platform))
        
        # Limit to maximum 4 variations for manageable testing
        variations = variations[:4]
        
        ab_test = ABTest(
            id=test_id,
            name=test_name,
            content_type=base_content.get('content_type', 'general'),
            platform=platform,
            variations=variations,
            status='draft',
            created_at=datetime.now().isoformat()
        )
        
        self.active_tests[test_id] = ab_test
        return ab_test
    
    def _create_hook_variations(self, base_content: Dict, platform: str) -> List[ABTestVariation]:
        """Create variations with different hooks/openings"""
        variations = []
        content_type = base_content.get('content_type', 'general')
        location = base_content.get('location', 'Windsor')
        
        hooks = self.variation_strategies['hooks'].get(content_type, 
                self.variation_strategies['hooks']['educational'])
        
        # Select 2-3 different hooks
        selected_hooks = random.sample(hooks, min(3, len(hooks)))
        
        for i, hook in enumerate(selected_hooks):
            variation_content = base_content['content'].replace(
                base_content['content'].split('\n')[0],  # Replace first line
                hook.format(location=location, topic=base_content.get('topic', 'real estate'))
            )
            
            variation = ABTestVariation(
                id=f"hook_var_{i+1}",
                content=variation_content,
                hashtags=base_content.get('hashtags', []),
                image_prompt=base_content.get('image_prompt', ''),
                created_at=datetime.now().isoformat()
            )
            variations.append(variation)
        
        return variations
    
    def _create_cta_variations(self, base_content: Dict, platform: str) -> List[ABTestVariation]:
        """Create variations with different call-to-action styles"""
        variations = []
        
        for cta_style, cta_options in self.variation_strategies['cta_styles'].items():
            # Replace the last line (assumed to be CTA) with new style
            content_lines = base_content['content'].split('\n')
            content_lines[-1] = random.choice(cta_options)
            
            variation_content = '\n'.join(content_lines)
            
            variation = ABTestVariation(
                id=f"cta_{cta_style}",
                content=variation_content,
                hashtags=base_content.get('hashtags', []),
                image_prompt=base_content.get('image_prompt', ''),
                created_at=datetime.now().isoformat()
            )
            variations.append(variation)
        
        return variations
    
    def _create_emoji_variations(self, base_content: Dict, platform: str) -> List[ABTestVariation]:
        """Create variations with different emoji usage levels"""
        variations = []
        base_text = base_content['content']
        
        for emoji_level, emoji_ratio in self.variation_strategies['emoji_styles'].items():
            if emoji_level == 'none':
                # Remove all emojis
                import re
                emoji_pattern = re.compile(
                    "["
                    "\U0001F600-\U0001F64F"
                    "\U0001F300-\U0001F5FF"
                    "\U0001F680-\U0001F6FF"
                    "\U0001F1E0-\U0001F1FF"
                    "\U00002702-\U000027B0"
                    "\U000024C2-\U0001F251"
                    "]+", flags=re.UNICODE
                )
                variation_content = emoji_pattern.sub('', base_text)
            else:
                # Adjust emoji density (simplified implementation)
                variation_content = base_text
            
            variation = ABTestVariation(
                id=f"emoji_{emoji_level}",
                content=variation_content,
                hashtags=base_content.get('hashtags', []),
                image_prompt=base_content.get('image_prompt', ''),
                created_at=datetime.now().isoformat()
            )
            variations.append(variation)
        
        return variations
    
    def _create_hashtag_variations(self, base_content: Dict, platform: str) -> List[ABTestVariation]:
        """Create variations with different hashtag strategies"""
        variations = []
        base_hashtags = base_content.get('hashtags', [])
        
        for strategy, (min_count, max_count) in self.variation_strategies['hashtag_strategies'].items():
            if strategy == 'focused':
                # Use fewer, more specific hashtags
                variation_hashtags = base_hashtags[:min_count]
            elif strategy == 'broad':
                # Use more hashtags, add general ones
                variation_hashtags = base_hashtags + ['#RealEstate', '#Property', '#Investment']
                variation_hashtags = variation_hashtags[:max_count]
            elif strategy == 'niche':
                # Use very specific local hashtags
                niche_tags = ['#WindsorRealtor', '#EssexCountyHomes', '#LocalRealEstate']
                variation_hashtags = niche_tags + base_hashtags[:3]
            else:  # trending
                # Mix of trending and specific
                trending_tags = ['#RealEstate', '#HomeBuying', '#PropertyInvestment']
                variation_hashtags = trending_tags + base_hashtags
                variation_hashtags = variation_hashtags[:max_count]
            
            variation = ABTestVariation(
                id=f"hashtag_{strategy}",
                content=base_content['content'],
                hashtags=variation_hashtags,
                image_prompt=base_content.get('image_prompt', ''),
                created_at=datetime.now().isoformat()
            )
            variations.append(variation)
        
        return variations
    
    def _create_default_variations(self, base_content: Dict, platform: str) -> List[ABTestVariation]:
        """Create default A/B variations when no specific type is requested"""
        variations = []
        
        # Variation A: Original content
        variation_a = ABTestVariation(
            id="variation_a",
            content=base_content['content'],
            hashtags=base_content.get('hashtags', []),
            image_prompt=base_content.get('image_prompt', ''),
            created_at=datetime.now().isoformat()
        )
        variations.append(variation_a)
        
        # Variation B: Modified hook and CTA
        content_lines = base_content['content'].split('\n')
        if len(content_lines) > 1:
            # Change first line (hook)
            content_lines[0] = "🌟 Exciting opportunity in Windsor-Essex!"
            # Change last line (CTA)
            content_lines[-1] = "Ready to learn more? Let's connect! 💬"
        
        variation_b = ABTestVariation(
            id="variation_b",
            content='\n'.join(content_lines),
            hashtags=base_content.get('hashtags', [])[:8],  # Fewer hashtags
            image_prompt=base_content.get('image_prompt', ''),
            created_at=datetime.now().isoformat()
        )
        variations.append(variation_b)
        
        return variations
    
    def start_ab_test(self, test_id: str) -> bool:
        """Start an A/B test"""
        if test_id in self.active_tests:
            test = self.active_tests[test_id]
            test.status = 'running'
            test.start_date = datetime.now().isoformat()
            return True
        return False
    
    def update_variation_performance(self, 
                                   test_id: str, 
                                   variation_id: str, 
                                   post_id: str,
                                   engagement_data: Dict) -> bool:
        """Update performance data for a variation"""
        if test_id in self.active_tests:
            test = self.active_tests[test_id]
            for variation in test.variations:
                if variation.id == variation_id:
                    variation.post_id = post_id
                    variation.engagement_data = engagement_data
                    return True
        return False
    
    def analyze_test_results(self, test_id: str) -> Dict:
        """Analyze A/B test results and determine winner"""
        if test_id not in self.active_tests:
            return {'error': 'Test not found'}
        
        test = self.active_tests[test_id]
        
        # Check if all variations have engagement data
        variations_with_data = [v for v in test.variations if v.engagement_data]
        
        if len(variations_with_data) < 2:
            return {'error': 'Insufficient data for analysis'}
        
        # Calculate engagement scores for each variation
        variation_scores = []
        
        for variation in variations_with_data:
            engagement = variation.engagement_data
            
            # Calculate composite engagement score
            likes = engagement.get('likes', 0)
            comments = engagement.get('comments', 0)
            shares = engagement.get('shares', 0)
            saves = engagement.get('saves', 0)
            reach = engagement.get('reach', 1)  # Avoid division by zero
            
            # Weighted engagement score
            engagement_score = (likes + (comments * 2) + (shares * 3) + (saves * 2)) / reach * 100
            
            variation_scores.append({
                'variation_id': variation.id,
                'engagement_score': engagement_score,
                'raw_data': engagement
            })
        
        # Sort by engagement score
        variation_scores.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        # Determine winner and confidence level
        if len(variation_scores) >= 2:
            winner_score = variation_scores[0]['engagement_score']
            runner_up_score = variation_scores[1]['engagement_score']
            
            # Simple confidence calculation (in practice, would use statistical significance)
            if runner_up_score > 0:
                confidence = min(((winner_score - runner_up_score) / runner_up_score) * 100, 99)
            else:
                confidence = 99
            
            # Update test with winner
            test.winner_variation_id = variation_scores[0]['variation_id']
            test.confidence_level = confidence
            
            if confidence > 80:  # High confidence threshold
                test.status = 'completed'
                test.end_date = datetime.now().isoformat()
                self.completed_tests[test_id] = test
        
        return {
            'test_id': test_id,
            'status': test.status,
            'winner': variation_scores[0] if variation_scores else None,
            'all_results': variation_scores,
            'confidence_level': test.confidence_level,
            'recommendations': self._generate_recommendations(variation_scores)
        }
    
    def _generate_recommendations(self, variation_scores: List[Dict]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if not variation_scores:
            return recommendations
        
        winner = variation_scores[0]
        
        # Analyze what made the winner successful
        winner_data = winner['raw_data']
        
        if winner_data.get('comments', 0) > winner_data.get('likes', 0) * 0.1:
            recommendations.append("High comment rate suggests engaging, conversation-starting content works well")
        
        if winner_data.get('shares', 0) > 0:
            recommendations.append("Content was shareable - consider similar value-driven posts")
        
        if winner_data.get('saves', 0) > 0:
            recommendations.append("Content was saved - informational/educational content performs well")
        
        # Compare with other variations
        if len(variation_scores) > 1:
            winner_score = winner['engagement_score']
            avg_other_scores = statistics.mean([v['engagement_score'] for v in variation_scores[1:]])
            
            if winner_score > avg_other_scores * 1.5:
                recommendations.append("Clear winner - replicate this content style for future posts")
            elif winner_score > avg_other_scores * 1.2:
                recommendations.append("Moderate improvement - test similar variations to optimize further")
            else:
                recommendations.append("Close results - consider testing with larger audience or longer duration")
        
        return recommendations
    
    def get_test_summary(self, test_id: str) -> Dict:
        """Get a summary of an A/B test"""
        test = self.active_tests.get(test_id) or self.completed_tests.get(test_id)
        
        if not test:
            return {'error': 'Test not found'}
        
        return {
            'id': test.id,
            'name': test.name,
            'status': test.status,
            'platform': test.platform,
            'variation_count': len(test.variations),
            'start_date': test.start_date,
            'end_date': test.end_date,
            'winner_variation_id': test.winner_variation_id,
            'confidence_level': test.confidence_level
        }
    
    def get_all_tests(self) -> Dict:
        """Get all A/B tests"""
        return {
            'active_tests': [self.get_test_summary(test_id) for test_id in self.active_tests.keys()],
            'completed_tests': [self.get_test_summary(test_id) for test_id in self.completed_tests.keys()]
        }
    
    def delete_test(self, test_id: str) -> bool:
        """Delete an A/B test"""
        if test_id in self.active_tests:
            del self.active_tests[test_id]
            return True
        elif test_id in self.completed_tests:
            del self.completed_tests[test_id]
            return True
        return False

# Global instance
ab_testing_service = ABTestingService()

