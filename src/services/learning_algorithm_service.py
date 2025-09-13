# src/services/learning_algorithm_service.py - COMBINED VERSION

import json
import requests
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
import statistics
import math
import os
from dotenv import load_dotenv

# --- NEW: META AUTOMATOR SERVICE CLASS ADDED DIRECTLY HERE ---
class MetaAutomatorService:
    def __init__(self):
        load_dotenv()
        self.page_id = os.getenv("META_PAGE_ID")
        self.page_access_token = os.getenv("META_PAGE_ACCESS_TOKEN")
        self.base_url = "https://graph.facebook.com/v18.0"

        if not self.page_id or not self.page_access_token:
            # We don't raise an error here to allow the app to start
            # even if the Meta integration isn't fully configured.
            print("WARNING: META_PAGE_ID or META_PAGE_ACCESS_TOKEN are not set. Meta automator will be disabled." )
            self.enabled = False
        else:
            self.enabled = True

    def get_latest_posts_with_insights(self, limit=10):
        if not self.enabled:
            return {"success": False, "error": {"message": "Meta Automator is not configured."}}
            
        print(f"Fetching latest {limit} posts for Page ID: {self.page_id}")
        fields = "id,message,created_time"
        metrics = "post_impressions,post_engaged_users,post_reactions_like_total,post_comments,post_shares"
        url = f"{self.base_url}/{self.page_id}/posts"
        params = {
            'fields': f"{fields},insights.metric({metrics})",
            'limit': limit,
            'access_token': self.page_access_token
        }
        try:
            response = requests.get(url, params=params)
            response_data = response.json()
            if response.status_code == 200:
                print("Successfully fetched posts and insights.")
                return {"success": True, "data": response_data.get("data", [])}
            else:
                print(f"Error fetching posts. Status: {response.status_code}, Response: {response_data}")
                return {"success": False, "error": response_data.get("error", {})}
        except Exception as e:
            print(f"An exception occurred: {e}")
            return {"success": False, "error": {"message": str(e)}}

# Create a single instance of the new service
meta_automator_service = MetaAutomatorService()


# --- EXISTING LEARNING ALGORITHM SERVICE (UNMODIFIED) ---

class LearningAlgorithmService:
    """Service for learning from engagement data and optimizing content generation"""
    
    def __init__(self):
        self.performance_history = []
        self.learning_insights = {
            'optimal_posting_times': {},
            'best_performing_content_types': {},
            'effective_hashtags': {},
            'successful_hooks': [],
            'high_engagement_patterns': {},
            'audience_preferences': {}
        }
        self.min_data_points = 10
        self.metric_weights = {
            'likes': 1.0, 'comments': 2.0, 'shares': 3.0, 'saves': 2.5,
            'reach': 0.1, 'impressions': 0.05
        }
    
    def fetch_post_performance(self, access_token: str, platform: str = 'facebook') -> List[Dict]:
        # This function is now superseded by MetaAutomatorService, but we leave it here.
        return []
    
    def _process_post_data(self, post: Dict, platform: str) -> Optional[Dict]:
        # This logic will need to be adapted to use the new data format.
        pass
    
    def update_performance_history(self, posts_data: List[Dict]):
        """Update the performance history with new data"""
        for post_data in posts_data:
            existing_post = next((p for p in self.performance_history if p['post_id'] == post_data['post_id']), None)
            if existing_post:
                existing_post.update(post_data)
            else:
                self.performance_history.append(post_data)
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
        }
        self.learning_insights.update(insights)
        return insights

    def _analyze_posting_times(self) -> Dict:
        time_performance = defaultdict(list)
        for post in self.performance_history:
            created_time = datetime.fromisoformat(post['created_time'].replace('Z', '+00:00'))
            hour, day_of_week = created_time.hour, created_time.weekday()
            engagement_score = self._calculate_engagement_score(post)
            time_performance[f"hour_{hour}"].append(engagement_score)
            time_performance[f"day_{day_of_week}"].append(engagement_score)
        optimal_times = {}
        for time_slot, scores in time_performance.items():
            if len(scores) >= 3:
                optimal_times[time_slot] = {'avg_engagement': statistics.mean(scores), 'post_count': len(scores)}
        best_hours = sorted([(k, v) for k, v in optimal_times.items() if k.startswith('hour_')], key=lambda x: x[1]['avg_engagement'], reverse=True)[:3]
        best_days = sorted([(k, v) for k, v in optimal_times.items() if k.startswith('day_')], key=lambda x: x[1]['avg_engagement'], reverse=True)[:3]
        return {'best_hours': [int(h[0].split('_')[1]) for h in best_hours], 'best_days': [int(d[0].split('_')[1]) for d in best_days]}

    def _analyze_content_types(self) -> Dict:
        content_performance = defaultdict(list)
        for post in self.performance_history:
            content, score = post['content'].lower(), self._calculate_engagement_score(post)
            if any(k in content for k in ['just listed', 'new listing']): content_performance['property_listing'].append(score)
            elif any(k in content for k in ['market update', 'trends']): content_performance['market_update'].append(score)
            elif any(k in content for k in ['tip', 'advice']): content_performance['educational'].append(score)
            else: content_performance['general'].append(score)
        return {k: {'avg_engagement': statistics.mean(v), 'post_count': len(v)} for k, v in content_performance.items() if v}

    def _analyze_hashtags(self) -> Dict:
        hashtag_performance = defaultdict(list)
        for post in self.performance_history:
            hashtags, score = self._extract_hashtags(post['content']), self._calculate_engagement_score(post)
            for tag in hashtags: hashtag_performance[tag].append(score)
        hashtag_analysis = {tag: {'avg_engagement': statistics.mean(scores), 'usage_count': len(scores)} for tag, scores in hashtag_performance.items() if len(scores) >= 3}
        top_hashtags = sorted(hashtag_analysis.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)[:20]
        return {'top_performing_hashtags': dict(top_hashtags)}

    def _analyze_content_length(self) -> Dict:
        length_performance = defaultdict(list)
        for post in self.performance_history:
            length, score = len(post['content']), self._calculate_engagement_score(post)
            category = 'short' if length < 100 else 'medium' if length < 300 else 'long'
            length_performance[category].append(score)
        return {k: {'avg_engagement': statistics.mean(v), 'post_count': len(v)} for k, v in length_performance.items() if v}

    def _analyze_engagement_patterns(self) -> Dict:
        return {}

    def _calculate_engagement_score(self, post: Dict) -> float:
        metrics, score = post['metrics'], 0
        for metric, weight in self.metric_weights.items(): score += metrics.get(metric, 0) * weight
        return (score / metrics.get('impressions', 1)) * 100 if metrics.get('impressions', 1) > 0 else score

    def _extract_hashtags(self, content: str) -> List[str]:
        return [tag.lower() for tag in re.findall(r'#\w+', content)]

    def get_content_recommendations(self, content_type: str = None) -> Dict:
        if len(self.performance_history) < self.min_data_points: return {'error': 'Insufficient data'}
        return {'optimal_posting_time': self._get_optimal_posting_time(), 'recommended_hashtags': self._get_recommended_hashtags()}

    def _get_optimal_posting_time(self) -> Dict:
        times = self.learning_insights.get('optimal_posting_times', {})
        if not times: return {'recommendation': 'Insufficient data'}
        return {'recommended_hour': times.get('best_hours', [10])[0], 'recommended_days': times.get('best_days', [1, 3])[:2]}

    def _get_recommended_hashtags(self, content_type: str = None) -> List[str]:
        hashtags = self.learning_insights.get('hashtag_effectiveness', {})
        return list(hashtags.get('top_performing_hashtags', {}).keys())[:10]

learning_algorithm_service = LearningAlgorithmService()
