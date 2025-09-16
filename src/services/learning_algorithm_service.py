from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics
import re
from uuid import uuid4

from .manual_content_service import ManualContentService


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

        # Manual content service provides the source data for learning
        self._manual_content_service = ManualContentService()
    
    def fetch_post_performance(
        self,
        access_token: Optional[str] = None,
        platform: str = 'manual',
        content_items: Optional[List[Dict]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """Load performance data from manually uploaded content."""

        if content_items is None:
            content_items = self._manual_content_service.get_all_content(limit=limit or 200)

        processed_posts = []
        for item in content_items:
            processed = self._process_manual_content(item, platform)
            if processed:
                processed_posts.append(processed)

        return processed_posts

    def _process_manual_content(self, content: Dict, default_platform: str) -> Optional[Dict]:
        """Convert stored manual content into a normalized performance record."""

        if not isinstance(content, dict):
            return None

        text_content = content.get('content') or content.get('text') or content.get('caption')
        if not text_content:
            return None

        post_id = content.get('id') or content.get('content_id')
        if not post_id:
            post_id = f"manual-{uuid4()}"

        created_raw = (
            content.get('posted_at')
            or content.get('scheduled_for')
            or content.get('uploaded_at')
            or datetime.utcnow().isoformat()
        )

        try:
            created_dt = datetime.fromisoformat(created_raw.replace('Z', '+00:00'))
        except ValueError:
            created_dt = datetime.utcnow()

        created_time = created_dt.isoformat()

        platform = content.get('platform') or default_platform or 'manual'

        raw_metrics = content.get('metrics') or content.get('engagement') or {}
        likes = int(raw_metrics.get('likes') or 0)
        comments = int(raw_metrics.get('comments') or 0)
        shares = int(raw_metrics.get('shares') or raw_metrics.get('reposts') or 0)
        saves = int(raw_metrics.get('saves') or raw_metrics.get('bookmarks') or 0)
        reach = int(raw_metrics.get('reach') or 0)
        impressions = int(raw_metrics.get('impressions') or raw_metrics.get('views') or reach)

        total_engagement = likes + comments + shares + saves
        baseline = reach or impressions or 0
        engagement_rate = (
            float(raw_metrics.get('engagement_rate'))
            if raw_metrics.get('engagement_rate') is not None
            else ((total_engagement / baseline) * 100 if baseline else 0.0)
        )

        metrics = {
            'likes': likes,
            'comments': comments,
            'shares': shares,
            'saves': saves,
            'reach': reach,
            'impressions': impressions,
            'total_engagement': total_engagement,
            'engagement_rate': engagement_rate,
        }

        return {
            'post_id': post_id,
            'platform': platform,
            'created_time': created_time,
            'content': text_content,
            'metrics': metrics,
            'engagement_rate': engagement_rate,
            'total_engagement': total_engagement,
            'hashtags': content.get('hashtags', []),
            'manual_source': True,
        }
    
    def update_performance_history(self, posts_data: List[Dict]):
        """Update the performance history with new data"""
        for post_data in posts_data:
            existing_post = next((p for p in self.performance_history if p['post_id'] == post_data['post_id']), None)
            if existing_post:
                existing_post.update(post_data)
            else:
                self.performance_history.append(post_data)
        cutoff_date = datetime.now() - timedelta(days=180)
        pruned_history = []
        for post in self.performance_history:
            created_str = post.get('created_time') or datetime.utcnow().isoformat()
            try:
                created_dt = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            except ValueError:
                created_dt = datetime.utcnow()

            if created_dt > cutoff_date:
                pruned_history.append(post)

        self.performance_history = pruned_history
    
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
