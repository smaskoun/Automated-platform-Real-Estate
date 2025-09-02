from flask import Blueprint, request, jsonify
from ..services.brand_voice_service import brand_voice_service
import json

brand_voice_bp = Blueprint('brand_voice', __name__)

@brand_voice_bp.route('/analyze-posts', methods=['POST'])
def analyze_user_posts():
    """Analyze user's social media posts to learn their brand voice"""
    try:
        data = request.get_json()
        access_token = data.get('access_token')
        platform = data.get('platform', 'facebook')
        limit = data.get('limit', 50)
        
        if not access_token:
            return jsonify({'error': 'Access token is required'}), 400
        
        # Fetch user's posts
        posts = brand_voice_service.fetch_user_posts(access_token, platform, limit)
        
        if not posts:
            return jsonify({'error': 'No posts found or unable to fetch posts'}), 404
        
        # Analyze writing style
        analysis = brand_voice_service.analyze_writing_style(posts)
        
        # Create brand voice profile
        voice_profile = brand_voice_service.create_brand_voice_profile(analysis)
        
        return jsonify({
            'success': True,
            'posts_analyzed': len(posts),
            'analysis': analysis,
            'voice_profile': voice_profile,
            'message': f'Successfully analyzed {len(posts)} posts from {platform}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@brand_voice_bp.route('/upload-content', methods=['POST'])
def upload_content_for_analysis():
    """Upload text content for brand voice analysis"""
    try:
        data = request.get_json()
        content_text = data.get('content')
        
        if not content_text:
            return jsonify({'error': 'Content text is required'}), 400
        
        # Split content into individual posts (assuming separated by double newlines)
        posts = [{'text': post.strip()} for post in content_text.split('\n\n') if post.strip()]
        
        if not posts:
            return jsonify({'error': 'No valid content found'}), 400
        
        # Analyze writing style
        analysis = brand_voice_service.analyze_writing_style(posts)
        
        # Create brand voice profile
        voice_profile = brand_voice_service.create_brand_voice_profile(analysis)
        
        return jsonify({
            'success': True,
            'posts_analyzed': len(posts),
            'analysis': analysis,
            'voice_profile': voice_profile,
            'message': f'Successfully analyzed {len(posts)} text samples'
        })
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@brand_voice_bp.route('/generate-with-voice', methods=['POST'])
def generate_content_with_voice():
    """Generate content using learned brand voice"""
    try:
        data = request.get_json()
        content_template = data.get('content_template')
        voice_profile = data.get('voice_profile')
        
        if not content_template or not voice_profile:
            return jsonify({'error': 'Content template and voice profile are required'}), 400
        
        # Generate content with brand voice
        generated_content = brand_voice_service.generate_content_with_voice(
            content_template, voice_profile
        )
        
        return jsonify({
            'success': True,
            'generated_content': generated_content,
            'voice_applied': True
        })
        
    except Exception as e:
        return jsonify({'error': f'Content generation failed: {str(e)}'}), 500

@brand_voice_bp.route('/voice-profile', methods=['GET'])
def get_voice_profile():
    """Get the current brand voice profile"""
    try:
        # In a real implementation, this would fetch from database
        # For now, return a sample profile structure
        sample_profile = {
            'dominant_tone': 'professional',
            'writing_style': {
                'avg_sentence_length': 15,
                'uses_questions': True,
                'uses_exclamations': False,
                'emoji_frequency': 2.5
            },
            'vocabulary_preferences': {
                'home': 45,
                'property': 38,
                'market': 32,
                'investment': 28,
                'community': 25
            },
            'signature_phrases': [
                "Ready to make your move?",
                "Let's find your dream home",
                "Contact me for more details"
            ],
            'content_themes': {
                'just listed': 12,
                'market update': 8,
                'home buying tips': 15,
                'community spotlight': 6
            }
        }
        
        return jsonify({
            'success': True,
            'voice_profile': sample_profile,
            'profile_exists': True
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve voice profile: {str(e)}'}), 500

@brand_voice_bp.route('/voice-profile', methods=['POST'])
def save_voice_profile():
    """Save or update brand voice profile"""
    try:
        data = request.get_json()
        voice_profile = data.get('voice_profile')
        
        if not voice_profile:
            return jsonify({'error': 'Voice profile data is required'}), 400
        
        # In a real implementation, this would save to database
        # For now, just validate the structure
        required_fields = ['dominant_tone', 'writing_style', 'vocabulary_preferences']
        
        for field in required_fields:
            if field not in voice_profile:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Voice profile saved successfully',
            'profile_id': 'voice_profile_001'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to save voice profile: {str(e)}'}), 500

@brand_voice_bp.route('/voice-insights', methods=['GET'])
def get_voice_insights():
    """Get insights about the brand voice analysis"""
    try:
        # Sample insights data
        insights = {
            'analysis_summary': {
                'total_posts_analyzed': 45,
                'analysis_date': '2025-08-27',
                'confidence_score': 85,
                'data_quality': 'high'
            },
            'tone_breakdown': {
                'professional': 65,
                'friendly': 25,
                'educational': 8,
                'motivational': 2
            },
            'writing_characteristics': {
                'avg_post_length': 180,
                'question_frequency': 15,
                'emoji_usage': 'moderate',
                'hashtag_count_avg': 9
            },
            'engagement_correlation': {
                'high_engagement_traits': [
                    'Posts with questions get 40% more comments',
                    'Educational content has highest save rate',
                    'Community posts generate most shares'
                ],
                'optimization_suggestions': [
                    'Increase question usage for better engagement',
                    'Maintain current emoji level',
                    'Focus on educational content themes'
                ]
            }
        }
        
        return jsonify({
            'success': True,
            'insights': insights
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve insights: {str(e)}'}), 500

