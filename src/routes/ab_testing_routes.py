from flask import Blueprint, request, jsonify
from ..services.ab_testing_service import ab_testing_service
from ..services.seo_content_service import seo_content_service
import json

ab_testing_bp = Blueprint('ab_testing', __name__)

@ab_testing_bp.route('/create-test', methods=['POST'])
def create_ab_test():
    """Create a new A/B test"""
    try:
        data = request.get_json()
        test_name = data.get('test_name')
        content_type = data.get('content_type', 'general')
        platform = data.get('platform', 'instagram')
        location = data.get('location', 'Windsor')
        variation_types = data.get('variation_types', ['hooks', 'cta_styles'])
        custom_data = data.get('custom_data', {})
        
        if not test_name:
            return jsonify({'error': 'Test name is required'}), 400
        
        # Generate base content using SEO service
        base_content = seo_content_service.generate_seo_optimized_content(
            content_type=content_type,
            platform=platform,
            location=location,
            custom_data=custom_data
        )
        
        # Create A/B test with variations
        ab_test = ab_testing_service.create_ab_test(
            test_name=test_name,
            base_content=base_content,
            variation_types=variation_types,
            platform=platform
        )
        
        # Convert to dict for JSON serialization
        test_data = {
            'id': ab_test.id,
            'name': ab_test.name,
            'content_type': ab_test.content_type,
            'platform': ab_test.platform,
            'status': ab_test.status,
            'created_at': ab_test.created_at,
            'variations': [
                {
                    'id': var.id,
                    'content': var.content,
                    'hashtags': var.hashtags,
                    'image_prompt': var.image_prompt,
                    'created_at': var.created_at
                }
                for var in ab_test.variations
            ]
        }
        
        return jsonify({
            'success': True,
            'test': test_data,
            'message': f'A/B test created with {len(ab_test.variations)} variations'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to create A/B test: {str(e)}'}), 500

@ab_testing_bp.route('/start-test/<test_id>', methods=['POST'])
def start_ab_test(test_id):
    """Start an A/B test"""
    try:
        success = ab_testing_service.start_ab_test(test_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'A/B test {test_id} started successfully'
            })
        else:
            return jsonify({'error': 'Test not found or already started'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to start test: {str(e)}'}), 500

@ab_testing_bp.route('/update-performance', methods=['POST'])
def update_variation_performance():
    """Update performance data for a test variation"""
    try:
        data = request.get_json()
        test_id = data.get('test_id')
        variation_id = data.get('variation_id')
        post_id = data.get('post_id')
        engagement_data = data.get('engagement_data')
        
        if not all([test_id, variation_id, post_id, engagement_data]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success = ab_testing_service.update_variation_performance(
            test_id, variation_id, post_id, engagement_data
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Performance data updated successfully'
            })
        else:
            return jsonify({'error': 'Test or variation not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to update performance: {str(e)}'}), 500

@ab_testing_bp.route('/analyze-results/<test_id>', methods=['GET'])
def analyze_test_results(test_id):
    """Analyze A/B test results"""
    try:
        results = ab_testing_service.analyze_test_results(test_id)
        
        if 'error' in results:
            return jsonify(results), 400
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to analyze results: {str(e)}'}), 500

@ab_testing_bp.route('/tests', methods=['GET'])
def get_all_tests():
    """Get all A/B tests"""
    try:
        tests = ab_testing_service.get_all_tests()
        
        return jsonify({
            'success': True,
            'tests': tests
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve tests: {str(e)}'}), 500

@ab_testing_bp.route('/test/<test_id>', methods=['GET'])
def get_test_details(test_id):
    """Get detailed information about a specific test"""
    try:
        test_summary = ab_testing_service.get_test_summary(test_id)
        
        if 'error' in test_summary:
            return jsonify(test_summary), 404
        
        return jsonify({
            'success': True,
            'test': test_summary
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve test details: {str(e)}'}), 500

@ab_testing_bp.route('/test/<test_id>', methods=['DELETE'])
def delete_test(test_id):
    """Delete an A/B test"""
    try:
        success = ab_testing_service.delete_test(test_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Test {test_id} deleted successfully'
            })
        else:
            return jsonify({'error': 'Test not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to delete test: {str(e)}'}), 500

@ab_testing_bp.route('/variation-strategies', methods=['GET'])
def get_variation_strategies():
    """Get available variation strategies for A/B testing"""
    try:
        strategies = {
            'variation_types': [
                {
                    'id': 'hooks',
                    'name': 'Opening Hooks',
                    'description': 'Test different opening lines and attention grabbers'
                },
                {
                    'id': 'cta_styles',
                    'name': 'Call-to-Action Styles',
                    'description': 'Test different call-to-action approaches (direct, soft, urgent)'
                },
                {
                    'id': 'emoji_styles',
                    'name': 'Emoji Usage',
                    'description': 'Test different levels of emoji usage'
                },
                {
                    'id': 'hashtag_strategies',
                    'name': 'Hashtag Strategies',
                    'description': 'Test different hashtag approaches (focused, broad, niche)'
                }
            ],
            'content_types': [
                {
                    'id': 'property_showcase',
                    'name': 'Property Showcase',
                    'description': 'Posts featuring specific properties'
                },
                {
                    'id': 'market_update',
                    'name': 'Market Update',
                    'description': 'Market trends and analysis posts'
                },
                {
                    'id': 'educational',
                    'name': 'Educational',
                    'description': 'Tips and educational content'
                },
                {
                    'id': 'community',
                    'name': 'Community',
                    'description': 'Local community and neighborhood content'
                }
            ],
            'platforms': [
                {
                    'id': 'instagram',
                    'name': 'Instagram',
                    'optimal_hashtags': '8-12',
                    'optimal_length': '100-300 characters'
                },
                {
                    'id': 'facebook',
                    'name': 'Facebook',
                    'optimal_hashtags': '2-5',
                    'optimal_length': '100-500 characters'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'strategies': strategies
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve strategies: {str(e)}'}), 500

@ab_testing_bp.route('/test-templates', methods=['GET'])
def get_test_templates():
    """Get pre-configured A/B test templates"""
    try:
        templates = [
            {
                'id': 'hook_optimization',
                'name': 'Hook Optimization',
                'description': 'Test different opening hooks to maximize attention',
                'variation_types': ['hooks'],
                'recommended_duration': '7 days',
                'min_audience_size': 1000
            },
            {
                'id': 'cta_effectiveness',
                'name': 'CTA Effectiveness',
                'description': 'Compare direct vs soft call-to-action approaches',
                'variation_types': ['cta_styles'],
                'recommended_duration': '5 days',
                'min_audience_size': 500
            },
            {
                'id': 'hashtag_strategy',
                'name': 'Hashtag Strategy',
                'description': 'Test focused vs broad hashtag approaches',
                'variation_types': ['hashtag_strategies'],
                'recommended_duration': '10 days',
                'min_audience_size': 2000
            },
            {
                'id': 'comprehensive',
                'name': 'Comprehensive Test',
                'description': 'Test multiple elements simultaneously',
                'variation_types': ['hooks', 'cta_styles', 'emoji_styles'],
                'recommended_duration': '14 days',
                'min_audience_size': 5000
            }
        ]
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve templates: {str(e)}'}), 500

@ab_testing_bp.route('/performance-metrics', methods=['GET'])
def get_performance_metrics():
    """Get available performance metrics for A/B testing"""
    try:
        metrics = {
            'primary_metrics': [
                {
                    'id': 'engagement_rate',
                    'name': 'Engagement Rate',
                    'description': 'Total engagement divided by reach',
                    'weight': 'high'
                },
                {
                    'id': 'click_through_rate',
                    'name': 'Click-Through Rate',
                    'description': 'Clicks divided by impressions',
                    'weight': 'high'
                }
            ],
            'secondary_metrics': [
                {
                    'id': 'likes',
                    'name': 'Likes',
                    'description': 'Total number of likes',
                    'weight': 'medium'
                },
                {
                    'id': 'comments',
                    'name': 'Comments',
                    'description': 'Total number of comments',
                    'weight': 'high'
                },
                {
                    'id': 'shares',
                    'name': 'Shares',
                    'description': 'Total number of shares',
                    'weight': 'very_high'
                },
                {
                    'id': 'saves',
                    'name': 'Saves',
                    'description': 'Total number of saves (Instagram)',
                    'weight': 'high'
                }
            ],
            'reach_metrics': [
                {
                    'id': 'reach',
                    'name': 'Reach',
                    'description': 'Unique accounts reached',
                    'weight': 'medium'
                },
                {
                    'id': 'impressions',
                    'name': 'Impressions',
                    'description': 'Total number of times content was displayed',
                    'weight': 'low'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve metrics: {str(e)}'}), 500

