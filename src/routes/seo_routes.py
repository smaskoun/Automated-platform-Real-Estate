from flask import Blueprint, request, jsonify
from ..services.seo_content_service import seo_content_service
import json
from datetime import datetime

seo_bp = Blueprint('seo', __name__)

@seo_bp.route('/content/generate', methods=['POST'])
def generate_seo_content():
    """Generate SEO-optimized social media content"""
    data = request.get_json()
    
    # Validate required fields
    content_type = data.get('content_type', 'community')
    platform = data.get('platform', 'instagram')
    location = data.get('location')
    custom_data = data.get('custom_data', {})
    
    # Validate content type
    valid_types = ['property_showcase', 'market_update', 'educational', 'community']
    if content_type not in valid_types:
        return jsonify({
            'error': f'Invalid content type. Must be one of: {", ".join(valid_types)}'
        }), 400
    
    # Validate platform
    valid_platforms = ['instagram', 'facebook']
    if platform not in valid_platforms:
        return jsonify({
            'error': f'Invalid platform. Must be one of: {", ".join(valid_platforms)}'
        }), 400
    
    try:
        # Generate SEO-optimized content
        result = seo_content_service.generate_seo_optimized_content(
            content_type=content_type,
            platform=platform,
            location=location,
            custom_data=custom_data
        )
        
        return jsonify({
            'success': True,
            'content': result
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to generate content: {str(e)}'
        }), 500

@seo_bp.route('/content/optimize', methods=['POST'])
def optimize_content():
    """Optimize existing content for better SEO and engagement"""
    data = request.get_json()
    
    if 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    content = data['content']
    platform = data.get('platform', 'instagram')
    
    try:
        result = seo_content_service.optimize_existing_content(
            content=content,
            platform=platform
        )
        
        return jsonify({
            'success': True,
            'optimization': result
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to optimize content: {str(e)}'
        }), 500

@seo_bp.route('/content/calendar', methods=['POST'])
def generate_content_calendar():
    """Generate a content calendar with SEO-optimized posts"""
    data = request.get_json()
    
    days = data.get('days', 30)
    platform = data.get('platform', 'instagram')
    
    # Validate days
    if not isinstance(days, int) or days < 1 or days > 90:
        return jsonify({
            'error': 'Days must be an integer between 1 and 90'
        }), 400
    
    try:
        calendar = seo_content_service.generate_content_calendar(
            days=days,
            platform=platform
        )
        
        return jsonify({
            'success': True,
            'calendar': calendar,
            'total_posts': len(calendar)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to generate calendar: {str(e)}'
        }), 500

@seo_bp.route('/hashtags/generate', methods=['POST'])
def generate_hashtags():
    """Generate SEO-optimized hashtags for content"""
    data = request.get_json()
    
    content_type = data.get('content_type', 'community')
    platform = data.get('platform', 'instagram')
    location = data.get('location', 'Windsor')
    
    try:
        hashtags = seo_content_service._generate_hashtags(
            content_type=content_type,
            platform=platform,
            location=location
        )
        
        return jsonify({
            'success': True,
            'hashtags': hashtags,
            'count': len(hashtags)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to generate hashtags: {str(e)}'
        }), 500

@seo_bp.route('/content/analyze', methods=['POST'])
def analyze_content():
    """Analyze content for SEO and engagement metrics"""
    data = request.get_json()
    
    if 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    content = data['content']
    location = data.get('location', 'Windsor')
    content_type = data.get('content_type', 'general')
    platform = data.get('platform', 'instagram')
    hashtags = data.get('hashtags', [])
    
    try:
        # Generate SEO metadata
        seo_metadata = seo_content_service._generate_seo_metadata(
            content=content,
            location=location,
            content_type=content_type
        )
        
        # Calculate engagement score
        engagement_score = seo_content_service._calculate_engagement_score(
            content=content,
            hashtags=hashtags,
            platform=platform
        )
        
        # Get optimization suggestions
        optimization = seo_content_service.optimize_existing_content(
            content=content,
            platform=platform
        )
        
        return jsonify({
            'success': True,
            'analysis': {
                'seo_metadata': seo_metadata,
                'engagement_score': engagement_score,
                'optimization_suggestions': optimization['suggestions'],
                'character_count': len(content),
                'word_count': len(content.split()),
                'hashtag_count': len(hashtags)
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to analyze content: {str(e)}'
        }), 500

@seo_bp.route('/templates/content-types', methods=['GET'])
def get_content_types():
    """Get available content types and their descriptions"""
    content_types = {
        'property_showcase': {
            'name': 'Property Showcase',
            'description': 'Highlight specific properties, listings, and real estate features',
            'best_for': ['New listings', 'Featured properties', 'Property tours'],
            'optimal_frequency': '2-3 times per week'
        },
        'market_update': {
            'name': 'Market Update',
            'description': 'Share market trends, statistics, and analysis',
            'best_for': ['Monthly market reports', 'Trend analysis', 'Investment insights'],
            'optimal_frequency': '1-2 times per week'
        },
        'educational': {
            'name': 'Educational Content',
            'description': 'Provide valuable tips, guides, and educational information',
            'best_for': ['Home buying tips', 'Market education', 'Process explanations'],
            'optimal_frequency': '2-3 times per week'
        },
        'community': {
            'name': 'Community Focus',
            'description': 'Showcase local community, businesses, and neighborhood features',
            'best_for': ['Local spotlights', 'Community events', 'Neighborhood features'],
            'optimal_frequency': '1-2 times per week'
        }
    }
    
    return jsonify({
        'success': True,
        'content_types': content_types
    })

@seo_bp.route('/templates/locations', methods=['GET'])
def get_locations():
    """Get available locations for content generation"""
    return jsonify({
        'success': True,
        'locations': {
            'primary': seo_content_service.location_keywords['primary'],
            'neighborhoods': seo_content_service.location_keywords['neighborhoods']
        }
    })

@seo_bp.route('/analytics/keywords', methods=['GET'])
def get_keyword_analytics():
    """Get keyword analytics and suggestions"""
    location = request.args.get('location', 'Windsor')
    content_type = request.args.get('content_type', 'general')
    
    # Get relevant keywords
    primary_keywords = seo_content_service.real_estate_keywords['primary']
    long_tail_keywords = seo_content_service.real_estate_keywords['long_tail']
    
    # Location-specific keywords
    location_keywords = [
        f"{location} real estate",
        f"{location} homes for sale",
        f"{location} property market",
        f"{location} real estate agent",
        f"buy home in {location}",
        f"sell house {location}"
    ]
    
    return jsonify({
        'success': True,
        'keywords': {
            'primary': primary_keywords,
            'long_tail': long_tail_keywords,
            'location_specific': location_keywords,
            'trending': [
                f"{location} market trends 2025",
                f"investment opportunities {location}",
                f"first time buyer {location}",
                f"{location} neighborhood guide"
            ]
        }
    })

@seo_bp.route('/posting/optimal-times', methods=['GET'])
def get_optimal_posting_times():
    """Get optimal posting times for different platforms"""
    platform = request.args.get('platform', 'instagram')
    
    if platform not in ['instagram', 'facebook']:
        return jsonify({'error': 'Invalid platform'}), 400
    
    times = seo_content_service.optimal_posting_times[platform]
    
    return jsonify({
        'success': True,
        'platform': platform,
        'optimal_times': times,
        'timezone': 'Eastern Time',
        'recommendations': {
            'instagram': {
                'best_days': ['Tuesday', 'Wednesday', 'Thursday'],
                'avoid_times': ['Late evening', 'Early morning'],
                'peak_engagement': 'Lunch time and early evening'
            },
            'facebook': {
                'best_days': ['Tuesday', 'Wednesday', 'Thursday'],
                'avoid_times': ['Weekends after 3PM', 'Monday mornings'],
                'peak_engagement': 'Mid-morning and mid-afternoon'
            }
        }[platform]
    })

@seo_bp.route('/content/batch-generate', methods=['POST'])
def batch_generate_content():
    """Generate multiple pieces of content at once"""
    data = request.get_json()
    
    count = data.get('count', 5)
    platform = data.get('platform', 'instagram')
    content_types = data.get('content_types', ['property_showcase', 'educational', 'community'])
    locations = data.get('locations', ['Windsor'])
    
    # Validate count
    if not isinstance(count, int) or count < 1 or count > 20:
        return jsonify({
            'error': 'Count must be an integer between 1 and 20'
        }), 400
    
    try:
        generated_content = []
        
        for i in range(count):
            # Rotate through content types and locations
            content_type = content_types[i % len(content_types)]
            location = locations[i % len(locations)]
            
            result = seo_content_service.generate_seo_optimized_content(
                content_type=content_type,
                platform=platform,
                location=location
            )
            
            generated_content.append(result)
        
        return jsonify({
            'success': True,
            'content': generated_content,
            'total_generated': len(generated_content)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to generate batch content: {str(e)}'
        }), 500

@seo_bp.route('/export/content-plan', methods=['POST'])
def export_content_plan():
    """Export a complete content plan as JSON"""
    data = request.get_json()
    
    days = data.get('days', 30)
    platform = data.get('platform', 'instagram')
    include_images = data.get('include_images', True)
    
    try:
        # Generate content calendar
        calendar = seo_content_service.generate_content_calendar(
            days=days,
            platform=platform
        )
        
        # Create export data
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'platform': platform,
            'duration_days': days,
            'total_posts': len(calendar),
            'content_calendar': calendar,
            'seo_guidelines': {
                'hashtag_strategy': seo_content_service.hashtag_strategies[platform],
                'optimal_posting_times': seo_content_service.optimal_posting_times[platform],
                'content_distribution': {
                    'property_showcase': '40%',
                    'market_update': '20%',
                    'educational': '25%',
                    'community': '15%'
                }
            }
        }
        
        return jsonify({
            'success': True,
            'export': export_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to export content plan: {str(e)}'
        }), 500

