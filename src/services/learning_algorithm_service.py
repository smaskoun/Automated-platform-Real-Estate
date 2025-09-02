import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
import statistics
import math

class LearningAlgorithmService:
    """Service for learning from engagement data and optimizing content generation"""
    
    def __init__(self):
        self.performance_history = []  # In production, this would be a database
        self.learning_insights = {
            'optimal_posting_times': {},
            'best_performing_content_types': {},
            'effective_hashtags': {},
            'successful_hooks': [],
            'high_engagement_patterns': {},
            'audience_preferences': {}
        }
        
        # Minimum data points needed for reliable insights
        self.min_data_points = 10
        
        # Learning weights for different metrics
        self.metric_weights = {
            'likes': 1.0,
            'comments': 2.0,  # Comments are more valuable
            'shares': 3.0,    # Shares are most valuable
            'saves': 2.5,     # Saves indicate high value content
            'reach': 0.1,     # Reach is important but less weighted
            'impressions': 0.05
        }
    
    def fetch_post_performance(self, access_token: str, platform: str = 'facebook') -> List[Dict]:
        """
        Fetch performance data for recent posts
        
        Args:
            access_token: User's social media access token
            platform: 'facebook' or 'instagram'
        
        Returns:
            List of post performance data
        """
        posts_data = []
        
        try:
            if platform == 'facebook':
                # Facebook Graph API for post insights
                url = "https://graph.facebook.com/v18.0/me/posts"
                params = {
                    'access_token': access_token,
                    'fields': 'id,message,created_time,insights.metric(post_impressions,post_engaged_users,post_clicks,post_reactions_like_total,post_comments,post_shares)',
                    'limit': 50
                }
                
            elif platform == 'instagram':
                # Instagram Basic Display API for media insights
                url = "https://graph.instagram.com/me/media"
                params = {
                    'access_token': access_token,
                    'fields': 'id,caption,timestamp,insights.metric(impressions,reach,likes,comments,saves,shares)',
                    'limit': 50
                }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                for post in data.get('data', []):
                    post_data = self._process_post_data(post, platform)
                    if post_data:
                        posts_data.append(post_data)
            
        except Exception as e:
            print(f"Error fetching post performance: {str(e)}")
        
        return posts_data
    
    def _process_post_data(self, post: Dict, platform: str) -> Optional[Dict]:
        """Process raw post data into standardized format"""
        try:
            if platform == 'facebook':
                content = post.get('message', '')
                post_id = post.get('id')
                created_time = post.get('created_time')
                
                # Extract insights data
                insights = post.get('insights', {}).get('data', [])
                metrics = {}
                
                for insight in insights:
                    metric_name = insight.get('name')
                    metric_value = insight.get('values', [{}])[0].get('value', 0)
                    
                    if metric_name == 'post_impressions':
                        metrics['impressions'] = metric_value
                    elif metric_name == 'post_engaged_users':
                        metrics['engaged_users'] = metric_value
                    elif metric_name == 'post_reactions_like_total':
                        metrics['likes'] = metric_value
                    elif metric_name == 'post_comments':
                        metrics['comments'] = metric_value
                    elif metric_name == 'post_shares':
                        metrics['shares'] = metric_value
                    elif metric_name == 'post_clicks':
                        metrics['clicks'] = metric_value
                
            elif platform == 'instagram':
                content = post.get('caption', '')
                post_id = post.get('id')
                created_time = post.get('timestamp')
                
                # Extract insights data
                insights = post.get('insights', {}).get('data', [])
                metrics = {}
                
                for insight in insights:
                    metric_name = insight.get('name')
                    metric_value = insight.get('values', [{}])[0].get('value', 0)
                    metrics[metric_name] = metric_value
            
            if not content or not post_id:
                return None
            
            # Calculate engagement rate
            impressions = metrics.get('impressions', 1)
            total_engagement = (
                metrics.get('likes', 0) + 
                metrics.get('comments', 0) + 
                metrics.get('shares', 0) + 
                metrics.get('saves', 0)
            )
            engagement_rate = (total_engagement / impressions) * 100 if impressions > 0 else 0
            
            return {
                'post_id': post_id,
                'content': content,
                'platform': platform,
                'created_time': created_time,
                'metrics': metrics,
                'engagement_rate': engagement_rate,
                'total_engagement': total_engagement
            }
            
        except Exception as e:
            print(f"Error processing post data: {str(e)}")
            return None
    
    def update_performance_history(self, posts_data: List[Dict]):
        """Update the performance history with new data"""
        for post_data in posts_data:
            # Check if post already exists in history
            existing_post = next(
                (p for p in self.performance_history if p['post_id'] == post_data['post_id']), 
                None
            )
            
            if existing_post:
                # Update existing post data
                existing_post.update(post_data)
            else:
                # Add new post data
                self.performance_history.append(post_data)
        
        # Keep only recent data (last 6 months)
        cutoff_date = datetime.now() - timedelta(days=180)
        self.performance_history = [
            post for post in self.performance_history 
            if datetime.fromisoformat(post['created_time'].replace('Z', '+00:00')) > cutoff_date
        ]
    
    def analyze_performance_patterns(self) -> Dict:
        """Analyze performance patterns and generate insights"""
        if len(self.performance_history) < self.min_data_points:
            return {'error': 'Insufficient data for analysis', 'data_points': len(self.performance_history)}
        
        insights = {
            'optimal_posting_times': self._analyze_posting_times(),
            'content_type_performance': self._analyze_content_types(),
            'hashtag_effectiveness': self._analyze_hashtags(),
            'content_length_optimization': self._analyze_content_length(),
            'engagement_patterns': self._analyze_engagement_patterns(),
            'seasonal_trends': self._analyze_seasonal_trends(),
            'audience_behavior': self._analyze_audience_behavior()
        }
        
        # Update learning insights
        self.learning_insights.update(insights)
        
        return insights
    
    def _analyze_posting_times(self) -> Dict:
        """Analyze optimal posting times"""
        time_performance = defaultdict(list)
        
        for post in self.performance_history:
            created_time = datetime.fromisoformat(post['created_time'].replace('Z', '+00:00'))
            hour = created_time.hour
            day_of_week = created_time.weekday()  # 0 = Monday
            
            engagement_score = self._calculate_engagement_score(post)
            
            time_performance[f"hour_{hour}"].append(engagement_score)
            time_performance[f"day_{day_of_week}"].append(engagement_score)
        
        # Calculate average performance for each time slot
        optimal_times = {}
        
        for time_slot, scores in time_performance.items():
            if len(scores) >= 3:  # Minimum data points
                optimal_times[time_slot] = {
                    'avg_engagement': statistics.mean(scores),
                    'post_count': len(scores),
                    'consistency': 1 - (statistics.stdev(scores) / statistics.mean(scores)) if statistics.mean(scores) > 0 else 0
                }
        
        # Find best hours and days
        best_hours = sorted(
            [(k, v) for k, v in optimal_times.items() if k.startswith('hour_')],
            key=lambda x: x[1]['avg_engagement'],
            reverse=True
        )[:3]
        
        best_days = sorted(
            [(k, v) for k, v in optimal_times.items() if k.startswith('day_')],
            key=lambda x: x[1]['avg_engagement'],
            reverse=True
        )[:3]
        
        return {
            'best_hours': [int(h[0].split('_')[1]) for h, _ in best_hours],
            'best_days': [int(d[0].split('_')[1]) for d, _ in best_days],
            'detailed_analysis': optimal_times
        }
    
    def _analyze_content_types(self) -> Dict:
        """Analyze performance by content type"""
        content_performance = defaultdict(list)
        
        for post in self.performance_history:
            content = post['content'].lower()
            engagement_score = self._calculate_engagement_score(post)
            
            # Classify content type based on keywords
            if any(keyword in content for keyword in ['just listed', 'new listing', 'for sale']):
                content_performance['property_listing'].append(engagement_score)
            elif any(keyword in content for keyword in ['market update', 'market report', 'trends']):
                content_performance['market_update'].append(engagement_score)
            elif any(keyword in content for keyword in ['tip', 'advice', 'guide', 'how to']):
                content_performance['educational'].append(engagement_score)
            elif any(keyword in content for keyword in ['community', 'local', 'neighborhood']):
                content_performance['community'].append(engagement_score)
            else:
                content_performance['general'].append(engagement_score)
        
        # Calculate performance metrics for each type
        type_analysis = {}
        for content_type, scores in content_performance.items():
            if scores:
                type_analysis[content_type] = {
                    'avg_engagement': statistics.mean(scores),
                    'post_count': len(scores),
                    'best_performance': max(scores),
                    'consistency': 1 - (statistics.stdev(scores) / statistics.mean(scores)) if len(scores) > 1 and statistics.mean(scores) > 0 else 0
                }
        
        return type_analysis
    
    def _analyze_hashtags(self) -> Dict:
        """Analyze hashtag effectiveness"""
        hashtag_performance = defaultdict(list)
        
        for post in self.performance_history:
            content = post['content']
            hashtags = self._extract_hashtags(content)
            engagement_score = self._calculate_engagement_score(post)
            
            for hashtag in hashtags:
                hashtag_performance[hashtag].append(engagement_score)
        
        # Calculate effectiveness for each hashtag
        hashtag_analysis = {}
        for hashtag, scores in hashtag_performance.items():
            if len(scores) >= 3:  # Minimum usage for reliable data
                hashtag_analysis[hashtag] = {
                    'avg_engagement': statistics.mean(scores),
                    'usage_count': len(scores),
                    'best_performance': max(scores),
                    'effectiveness_score': statistics.mean(scores) * math.log(len(scores))  # Weight by usage frequency
                }
        
        # Sort by effectiveness
        top_hashtags = sorted(
            hashtag_analysis.items(),
            key=lambda x: x[1]['effectiveness_score'],
            reverse=True
        )[:20]
        
        return {
            'top_performing_hashtags': dict(top_hashtags),
            'total_hashtags_analyzed': len(hashtag_analysis)
        }
    
    def _analyze_content_length(self) -> Dict:
        """Analyze optimal content length"""
        length_performance = defaultdict(list)
        
        for post in self.performance_history:
            content_length = len(post['content'])
            engagement_score = self._calculate_engagement_score(post)
            
            # Categorize by length
            if content_length < 100:
                category = 'short'
            elif content_length < 300:
                category = 'medium'
            elif content_length < 500:
                category = 'long'
            else:
                category = 'very_long'
            
            length_performance[category].append(engagement_score)
        
        # Calculate performance for each category
        length_analysis = {}
        for category, scores in length_performance.items():
            if scores:
                length_analysis[category] = {
                    'avg_engagement': statistics.mean(scores),
                    'post_count': len(scores),
                    'best_performance': max(scores)
                }
        
        return length_analysis
    
    def _analyze_engagement_patterns(self) -> Dict:
        """Analyze general engagement patterns"""
        patterns = {
            'emoji_impact': self._analyze_emoji_impact(),
            'question_impact': self._analyze_question_impact(),
            'cta_effectiveness': self._analyze_cta_effectiveness(),
            'timing_patterns': self._analyze_timing_patterns()
        }
        
        return patterns
    
    def _analyze_emoji_impact(self) -> Dict:
        """Analyze impact of emoji usage"""
        emoji_performance = {'with_emojis': [], 'without_emojis': []}
        
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
        
        for post in self.performance_history:
            engagement_score = self._calculate_engagement_score(post)
            
            if emoji_pattern.search(post['content']):
                emoji_performance['with_emojis'].append(engagement_score)
            else:
                emoji_performance['without_emojis'].append(engagement_score)
        
        analysis = {}
        for category, scores in emoji_performance.items():
            if scores:
                analysis[category] = {
                    'avg_engagement': statistics.mean(scores),
                    'post_count': len(scores)
                }
        
        return analysis
    
    def _analyze_question_impact(self) -> Dict:
        """Analyze impact of questions in posts"""
        question_performance = {'with_questions': [], 'without_questions': []}
        
        for post in self.performance_history:
            engagement_score = self._calculate_engagement_score(post)
            
            if '?' in post['content']:
                question_performance['with_questions'].append(engagement_score)
            else:
                question_performance['without_questions'].append(engagement_score)
        
        analysis = {}
        for category, scores in question_performance.items():
            if scores:
                analysis[category] = {
                    'avg_engagement': statistics.mean(scores),
                    'post_count': len(scores)
                }
        
        return analysis
    
    def _analyze_cta_effectiveness(self) -> Dict:
        """Analyze call-to-action effectiveness"""
        cta_keywords = ['contact', 'call', 'dm', 'message', 'reach out', 'book', 'schedule']
        cta_performance = {'with_cta': [], 'without_cta': []}
        
        for post in self.performance_history:
            engagement_score = self._calculate_engagement_score(post)
            content_lower = post['content'].lower()
            
            if any(keyword in content_lower for keyword in cta_keywords):
                cta_performance['with_cta'].append(engagement_score)
            else:
                cta_performance['without_cta'].append(engagement_score)
        
        analysis = {}
        for category, scores in cta_performance.items():
            if scores:
                analysis[category] = {
                    'avg_engagement': statistics.mean(scores),
                    'post_count': len(scores)
                }
        
        return analysis
    
    def _analyze_timing_patterns(self) -> Dict:
        """Analyze timing-related patterns"""
        # This could include analysis of posting frequency, time between posts, etc.
        return {'analysis': 'Timing patterns analysis would go here'}
    
    def _analyze_seasonal_trends(self) -> Dict:
        """Analyze seasonal performance trends"""
        monthly_performance = defaultdict(list)
        
        for post in self.performance_history:
            created_time = datetime.fromisoformat(post['created_time'].replace('Z', '+00:00'))
            month = created_time.month
            engagement_score = self._calculate_engagement_score(post)
            
            monthly_performance[month].append(engagement_score)
        
        seasonal_analysis = {}
        for month, scores in monthly_performance.items():
            if len(scores) >= 2:
                seasonal_analysis[month] = {
                    'avg_engagement': statistics.mean(scores),
                    'post_count': len(scores)
                }
        
        return seasonal_analysis
    
    def _analyze_audience_behavior(self) -> Dict:
        """Analyze audience behavior patterns"""
        behavior_patterns = {
            'comment_to_like_ratio': [],
            'share_rate': [],
            'save_rate': []
        }
        
        for post in self.performance_history:
            metrics = post['metrics']
            likes = metrics.get('likes', 0)
            comments = metrics.get('comments', 0)
            shares = metrics.get('shares', 0)
            saves = metrics.get('saves', 0)
            
            if likes > 0:
                behavior_patterns['comment_to_like_ratio'].append(comments / likes)
            
            total_engagement = likes + comments + shares + saves
            if total_engagement > 0:
                behavior_patterns['share_rate'].append(shares / total_engagement)
                behavior_patterns['save_rate'].append(saves / total_engagement)
        
        analysis = {}
        for pattern, values in behavior_patterns.items():
            if values:
                analysis[pattern] = {
                    'average': statistics.mean(values),
                    'median': statistics.median(values)
                }
        
        return analysis
    
    def _calculate_engagement_score(self, post: Dict) -> float:
        """Calculate weighted engagement score for a post"""
        metrics = post['metrics']
        score = 0
        
        for metric, weight in self.metric_weights.items():
            value = metrics.get(metric, 0)
            score += value * weight
        
        # Normalize by impressions if available
        impressions = metrics.get('impressions', 1)
        return (score / impressions) * 100 if impressions > 0 else score
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        import re
        hashtags = re.findall(r'#\w+', content)
        return [tag.lower() for tag in hashtags]
    
    def get_content_recommendations(self, content_type: str = None) -> Dict:
        """Get AI-powered content recommendations based on learning"""
        if len(self.performance_history) < self.min_data_points:
            return {'error': 'Insufficient data for recommendations'}
        
        insights = self.learning_insights
        recommendations = {
            'optimal_posting_time': self._get_optimal_posting_time(),
            'recommended_hashtags': self._get_recommended_hashtags(content_type),
            'content_style_suggestions': self._get_content_style_suggestions(),
            'engagement_optimization_tips': self._get_engagement_tips()
        }
        
        return recommendations
    
    def _get_optimal_posting_time(self) -> Dict:
        """Get optimal posting time recommendation"""
        posting_times = self.learning_insights.get('optimal_posting_times', {})
        
        if not posting_times:
            return {'recommendation': 'Insufficient data'}
        
        best_hours = posting_times.get('best_hours', [])
        best_days = posting_times.get('best_days', [])
        
        if best_hours and best_days:
            return {
                'recommended_hour': best_hours[0],
                'recommended_days': best_days[:2],
                'confidence': 'high' if len(self.performance_history) > 30 else 'medium'
            }
        
        return {'recommendation': 'More data needed for reliable timing recommendations'}
    
    def _get_recommended_hashtags(self, content_type: str = None) -> List[str]:
        """Get recommended hashtags based on performance"""
        hashtag_data = self.learning_insights.get('hashtag_effectiveness', {})
        top_hashtags = hashtag_data.get('top_performing_hashtags', {})
        
        if not top_hashtags:
            return []
        
        # Return top 10 performing hashtags
        return list(top_hashtags.keys())[:10]
    
    def _get_content_style_suggestions(self) -> List[str]:
        """Get content style suggestions based on performance"""
        suggestions = []
        
        engagement_patterns = self.learning_insights.get('engagement_patterns', {})
        
        # Emoji recommendations
        emoji_impact = engagement_patterns.get('emoji_impact', {})
        if emoji_impact:
            with_emojis = emoji_impact.get('with_emojis', {}).get('avg_engagement', 0)
            without_emojis = emoji_impact.get('without_emojis', {}).get('avg_engagement', 0)
            
            if with_emojis > without_emojis * 1.2:
                suggestions.append("Use emojis to increase engagement")
            elif without_emojis > with_emojis * 1.2:
                suggestions.append("Consider reducing emoji usage")
        
        # Question recommendations
        question_impact = engagement_patterns.get('question_impact', {})
        if question_impact:
            with_questions = question_impact.get('with_questions', {}).get('avg_engagement', 0)
            without_questions = question_impact.get('without_questions', {}).get('avg_engagement', 0)
            
            if with_questions > without_questions * 1.2:
                suggestions.append("Include questions to boost engagement")
        
        # CTA recommendations
        cta_impact = engagement_patterns.get('cta_effectiveness', {})
        if cta_impact:
            with_cta = cta_impact.get('with_cta', {}).get('avg_engagement', 0)
            without_cta = cta_impact.get('without_cta', {}).get('avg_engagement', 0)
            
            if with_cta > without_cta * 1.2:
                suggestions.append("Include clear call-to-action statements")
        
        return suggestions
    
    def _get_engagement_tips(self) -> List[str]:
        """Get engagement optimization tips"""
        tips = []
        
        content_types = self.learning_insights.get('content_type_performance', {})
        if content_types:
            best_type = max(content_types.items(), key=lambda x: x[1].get('avg_engagement', 0))
            tips.append(f"Focus more on {best_type[0]} content - it performs best for your audience")
        
        length_analysis = self.learning_insights.get('content_length_optimization', {})
        if length_analysis:
            best_length = max(length_analysis.items(), key=lambda x: x[1].get('avg_engagement', 0))
            tips.append(f"Optimal content length appears to be {best_length[0]}")
        
        return tips

# Global instance
learning_algorithm_service = LearningAlgorithmService()

