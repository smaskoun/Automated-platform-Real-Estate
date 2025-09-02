from flask import Blueprint, request, jsonify
from ..services.learning_algorithm_service import learning_algorithm_service
import json

learning_algorithm_bp = Blueprint('learning_algorithm', __name__)

@learning_algorithm_bp.route('/fetch-performance', methods=['POST'])
def fetch_post_performance():
    """Fetch performance data from social media platforms"""
    try:
        data = request.get_json()
        access_token = data.get('access_token')
        platform = data.get('platform', 'facebook')
        
        if not access_token:
            return jsonify({'error': 'Access token is required'}), 400
        
        # Fetch performance data
        posts_data = learning_algorithm_service.fetch_post_performance(access_token, platform)
        
        if not posts_data:
            return jsonify({'error': 'No performance data found or unable to fetch data'}), 404
        
        # Update performance history
        learning_algorithm_service.update_performance_history(posts_data)
        
        return jsonify({
            'success': True,
            'posts_fetched': len(posts_data),
            'platform': platform,
            'message': f'Successfully fetched performance data for {len(posts_data)} posts'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch performance data: {str(e)}'}), 500

@learning_algorithm_bp.route('/analyze-patterns', methods=['POST'])
def analyze_performance_patterns():
    """Analyze performance patterns and generate insights"""
    try:
        insights = learning_algorithm_service.analyze_performance_patterns()
        
        if 'error' in insights:
            return jsonify(insights), 400
        
        return jsonify({
            'success': True,
            'insights': insights,
            'data_points': len(learning_algorithm_service.performance_history),
            'message': 'Performance patterns analyzed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to analyze patterns: {str(e)}'}), 500

@learning_algorithm_bp.route('/recommendations', methods=['GET'])
def get_content_recommendations():
    """Get AI-powered content recommendations"""
    try:
        content_type = request.args.get('content_type')
        
        recommendations = learning_algorithm_service.get_content_recommendations(content_type)
        
        if 'error' in recommendations:
            return jsonify(recommendations), 400
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'generated_at': learning_algorithm_service.performance_history[-1]['created_time'] if learning_algorithm_service.performance_history else None
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate recommendations: {str(e)}'}), 500

@learning_algorithm_bp.route('/insights', methods=['GET'])
def get_learning_insights():
    """Get current learning insights"""
    try:
        insights = learning_algorithm_service.learning_insights
        
        # Add summary statistics
        summary = {
            'total_posts_analyzed': len(learning_algorithm_service.performance_history),
            'data_quality': 'high' if len(learning_algorithm_service.performance_history) > 30 else 'medium' if len(learning_algorithm_service.performance_history) > 10 else 'low',
            'last_analysis': learning_algorithm_service.performance_history[-1]['created_time'] if learning_algorithm_service.performance_history else None,
            'insights_available': len([k for k, v in insights.items() if v])
        }
        
        return jsonify({
            'success': True,
            'insights': insights,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve insights: {str(e)}'}), 500

@learning_algorithm_bp.route('/performance-history', methods=['GET'])
def get_performance_history():
    """Get performance history data"""
    try:
        limit = request.args.get('limit', 50, type=int)
        platform = request.args.get('platform')
        
        history = learning_algorithm_service.performance_history
        
        # Filter by platform if specified
        if platform:
            history = [post for post in history if post.get('platform') == platform]
        
        # Limit results
        history = history[-limit:] if limit else history
        
        # Calculate summary statistics
        if history:
            engagement_rates = [post.get('engagement_rate', 0) for post in history]
            total_engagements = [post.get('total_engagement', 0) for post in history]
            
            summary_stats = {
                'avg_engagement_rate': sum(engagement_rates) / len(engagement_rates),
                'max_engagement_rate': max(engagement_rates),
                'min_engagement_rate': min(engagement_rates),
                'avg_total_engagement': sum(total_engagements) / len(total_engagements),
                'total_posts': len(history)
            }
        else:
            summary_stats = {}
        
        return jsonify({
            'success': True,
            'history': history,
            'summary_stats': summary_stats,
            'total_available': len(learning_algorithm_service.performance_history)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve performance history: {str(e)}'}), 500

@learning_algorithm_bp.route('/optimal-timing', methods=['GET'])
def get_optimal_timing():
    """Get optimal posting timing recommendations"""
    try:
        platform = request.args.get('platform', 'instagram')
        
        insights = learning_algorithm_service.learning_insights
        timing_data = insights.get('optimal_posting_times', {})
        
        if not timing_data:
            return jsonify({
                'success': False,
                'error': 'Insufficient data for timing analysis',
                'recommendation': 'Need at least 10 posts for reliable timing insights'
            }), 400
        
        # Convert hour numbers to readable format
        best_hours = timing_data.get('best_hours', [])
        best_days = timing_data.get('best_days', [])
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        readable_timing = {
            'best_hours': [f"{hour}:00" for hour in best_hours],
            'best_days': [day_names[day] for day in best_days if day < len(day_names)],
            'detailed_analysis': timing_data.get('detailed_analysis', {})
        }
        
        return jsonify({
            'success': True,
            'optimal_timing': readable_timing,
            'platform': platform,
            'confidence': 'high' if len(learning_algorithm_service.performance_history) > 30 else 'medium'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get optimal timing: {str(e)}'}), 500

@learning_algorithm_bp.route('/hashtag-analysis', methods=['GET'])
def get_hashtag_analysis():
    """Get hashtag effectiveness analysis"""
    try:
        insights = learning_algorithm_service.learning_insights
        hashtag_data = insights.get('hashtag_effectiveness', {})
        
        if not hashtag_data:
            return jsonify({
                'success': False,
                'error': 'No hashtag analysis available',
                'recommendation': 'Need more posts with hashtags for analysis'
            }), 400
        
        top_hashtags = hashtag_data.get('top_performing_hashtags', {})
        
        # Format for better readability
        formatted_hashtags = []
        for hashtag, data in list(top_hashtags.items())[:15]:
            formatted_hashtags.append({
                'hashtag': hashtag,
                'avg_engagement': data.get('avg_engagement', 0),
                'usage_count': data.get('usage_count', 0),
                'effectiveness_score': data.get('effectiveness_score', 0)
            })
        
        return jsonify({
            'success': True,
            'top_hashtags': formatted_hashtags,
            'total_analyzed': hashtag_data.get('total_hashtags_analyzed', 0),
            'recommendations': formatted_hashtags[:5]  # Top 5 recommendations
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get hashtag analysis: {str(e)}'}), 500

@learning_algorithm_bp.route('/content-optimization', methods=['GET'])
def get_content_optimization():
    """Get content optimization insights"""
    try:
        insights = learning_algorithm_service.learning_insights
        
        content_types = insights.get('content_type_performance', {})
        length_analysis = insights.get('content_length_optimization', {})
        engagement_patterns = insights.get('engagement_patterns', {})
        
        optimization_tips = []
        
        # Content type recommendations
        if content_types:
            best_type = max(content_types.items(), key=lambda x: x[1].get('avg_engagement', 0))
            optimization_tips.append({
                'category': 'Content Type',
                'recommendation': f"Focus more on {best_type[0]} content",
                'reason': f"Performs {best_type[1].get('avg_engagement', 0):.1f}% better on average",
                'confidence': 'high' if best_type[1].get('post_count', 0) > 5 else 'medium'
            })
        
        # Length recommendations
        if length_analysis:
            best_length = max(length_analysis.items(), key=lambda x: x[1].get('avg_engagement', 0))
            optimization_tips.append({
                'category': 'Content Length',
                'recommendation': f"Optimal content length is {best_length[0]}",
                'reason': f"Shows {best_length[1].get('avg_engagement', 0):.1f}% engagement rate",
                'confidence': 'medium'
            })
        
        # Engagement pattern recommendations
        if engagement_patterns:
            emoji_impact = engagement_patterns.get('emoji_impact', {})
            if emoji_impact:
                with_emojis = emoji_impact.get('with_emojis', {}).get('avg_engagement', 0)
                without_emojis = emoji_impact.get('without_emojis', {}).get('avg_engagement', 0)
                
                if with_emojis > without_emojis * 1.2:
                    optimization_tips.append({
                        'category': 'Emoji Usage',
                        'recommendation': 'Include emojis in your posts',
                        'reason': f"{((with_emojis - without_emojis) / without_emojis * 100):.1f}% better engagement",
                        'confidence': 'high'
                    })
        
        return jsonify({
            'success': True,
            'optimization_tips': optimization_tips,
            'detailed_insights': {
                'content_types': content_types,
                'length_analysis': length_analysis,
                'engagement_patterns': engagement_patterns
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get content optimization: {str(e)}'}), 500

@learning_algorithm_bp.route('/learning-status', methods=['GET'])
def get_learning_status():
    """Get current learning algorithm status"""
    try:
        history_count = len(learning_algorithm_service.performance_history)
        min_required = learning_algorithm_service.min_data_points
        
        status = {
            'data_points': history_count,
            'min_required': min_required,
            'status': 'active' if history_count >= min_required else 'learning',
            'progress': min(100, (history_count / min_required) * 100),
            'insights_available': len([k for k, v in learning_algorithm_service.learning_insights.items() if v]),
            'last_update': learning_algorithm_service.performance_history[-1]['created_time'] if learning_algorithm_service.performance_history else None
        }
        
        # Determine learning quality
        if history_count >= 50:
            status['quality'] = 'excellent'
        elif history_count >= 30:
            status['quality'] = 'good'
        elif history_count >= min_required:
            status['quality'] = 'fair'
        else:
            status['quality'] = 'insufficient'
        
        return jsonify({
            'success': True,
            'learning_status': status
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get learning status: {str(e)}'}), 500

@learning_algorithm_bp.route('/export-insights', methods=['GET'])
def export_insights():
    """Export learning insights as downloadable data"""
    try:
        export_format = request.args.get('format', 'json')
        
        export_data = {
            'export_date': learning_algorithm_service.performance_history[-1]['created_time'] if learning_algorithm_service.performance_history else None,
            'total_posts_analyzed': len(learning_algorithm_service.performance_history),
            'insights': learning_algorithm_service.learning_insights,
            'performance_summary': {
                'avg_engagement_rate': sum(post.get('engagement_rate', 0) for post in learning_algorithm_service.performance_history) / len(learning_algorithm_service.performance_history) if learning_algorithm_service.performance_history else 0,
                'total_posts': len(learning_algorithm_service.performance_history)
            }
        }
        
        if export_format == 'json':
            return jsonify({
                'success': True,
                'export_data': export_data,
                'format': 'json'
            })
        else:
            return jsonify({'error': 'Only JSON format is currently supported'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Failed to export insights: {str(e)}'}), 500

