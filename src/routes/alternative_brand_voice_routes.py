from flask import Blueprint, request, jsonify
from src.services.alternative_brand_voice_service import AlternativeBrandVoiceService
import json

alternative_brand_voice_bp = Blueprint('alternative_brand_voice', __name__)
brand_voice_service = AlternativeBrandVoiceService()

@alternative_brand_voice_bp.route('/analyze-text', methods=['POST'])
def analyze_text_content():
    """
    Analyze brand voice from manually provided text content
    """
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        content = data['content']
        content_type = data.get('content_type', 'mixed')
        
        if not content.strip():
            return jsonify({
                'success': False,
                'error': 'Content cannot be empty'
            }), 400
        
        # Analyze the provided content
        analysis_result = brand_voice_service.analyze_from_text_input(content, content_type)
        
        return jsonify({
            'success': True,
            'data': analysis_result,
            'message': 'Brand voice analysis completed successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@alternative_brand_voice_bp.route('/voice-profile', methods=['GET'])
def get_voice_profile():
    """
    Get the current brand voice profile
    """
    try:
        # Return a sample profile or stored profile
        sample_profile = {
            'dominant_tone': 'professional',
            'writing_style': 'balanced',
            'personality_traits': ['professional', 'helpful', 'knowledgeable'],
            'communication_preferences': {
                'uses_questions': True,
                'uses_exclamations': False,
                'uses_emojis': True,
                'prefers_short_sentences': False,
                'prefers_long_sentences': False
            },
            'vocabulary_level': 'professional',
            'brand_voice_strength': 75,
            'last_updated': '2024-08-28T18:00:00Z'
        }
        
        return jsonify({
            'success': True,
            'data': sample_profile,
            'message': 'Voice profile retrieved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve voice profile: {str(e)}'
        }), 500

@alternative_brand_voice_bp.route('/generate-content', methods=['POST'])
def generate_content_with_voice():
    """
    Generate content using the analyzed brand voice
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400
        
        prompt = data['prompt']
        content_type = data.get('content_type', 'social_post')
        
        # Use a default brand profile or get from stored analysis
        brand_profile = data.get('brand_profile', {
            'dominant_tone': 'professional',
            'writing_style': 'balanced',
            'personality_traits': ['professional', 'helpful'],
            'communication_preferences': {
                'uses_questions': True,
                'uses_exclamations': False,
                'uses_emojis': True,
                'prefers_short_sentences': False,
                'prefers_long_sentences': False
            },
            'vocabulary_level': 'professional'
        })
        
        # Generate content with brand voice
        generated_content = brand_voice_service.generate_content_with_voice(
            prompt, brand_profile, content_type
        )
        
        return jsonify({
            'success': True,
            'data': {
                'generated_content': generated_content,
                'prompt': prompt,
                'content_type': content_type,
                'brand_profile_used': brand_profile
            },
            'message': 'Content generated successfully with brand voice'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Content generation failed: {str(e)}'
        }), 500

@alternative_brand_voice_bp.route('/sample-analysis', methods=['GET'])
def get_sample_analysis():
    """
    Get a sample brand voice analysis for demonstration
    """
    try:
        sample_content = """
        🏡 Just listed! Beautiful 3-bedroom home in Windsor-Essex with stunning curb appeal and move-in ready condition. 
        
        This property features an open-concept layout, updated kitchen, and spacious backyard perfect for entertaining. Located in a quiet neighborhood with excellent schools nearby.
        
        Thinking of buying or selling? I'm here to help guide you through every step of the process. With over 10 years of experience in the Windsor-Essex market, I provide personalized service and expert advice.
        
        Ready to find your dream home? Let's chat! Send me a DM or call today. 📞✨
        
        #WindsorEssexRealEstate #DreamHome #RealEstateExpert #HomeBuying #PropertyListing
        """
        
        # Analyze the sample content
        analysis_result = brand_voice_service.analyze_from_text_input(sample_content, 'posts')
        
        return jsonify({
            'success': True,
            'data': analysis_result,
            'message': 'Sample analysis completed successfully',
            'note': 'This is a sample analysis. Upload your own content for personalized results.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Sample analysis failed: {str(e)}'
        }), 500

@alternative_brand_voice_bp.route('/upload-content', methods=['POST'])
def upload_content_file():
    """
    Upload and analyze content from a file
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Read file content
        if file.filename.endswith('.txt'):
            content = file.read().decode('utf-8')
        else:
            return jsonify({
                'success': False,
                'error': 'Only .txt files are supported'
            }), 400
        
        content_type = request.form.get('content_type', 'mixed')
        
        # Analyze the uploaded content
        analysis_result = brand_voice_service.analyze_from_text_input(content, content_type)
        
        return jsonify({
            'success': True,
            'data': analysis_result,
            'message': f'File "{file.filename}" analyzed successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'File analysis failed: {str(e)}'
        }), 500

@alternative_brand_voice_bp.route('/recommendations', methods=['POST'])
def get_brand_voice_recommendations():
    """
    Get recommendations for improving brand voice consistency
    """
    try:
        data = request.get_json()
        
        if not data or 'analysis' not in data:
            return jsonify({
                'success': False,
                'error': 'Analysis data is required'
            }), 400
        
        analysis = data['analysis']
        recommendations = brand_voice_service._generate_recommendations(analysis)
        
        return jsonify({
            'success': True,
            'data': {
                'recommendations': recommendations,
                'improvement_areas': [
                    'Tone consistency',
                    'Sentence structure',
                    'Call-to-action effectiveness',
                    'Audience engagement',
                    'Brand voice strength'
                ]
            },
            'message': 'Recommendations generated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate recommendations: {str(e)}'
        }), 500

@alternative_brand_voice_bp.route('/training-status', methods=['GET'])
def get_training_status():
    """
    Get the current training status of the brand voice model
    """
    try:
        return jsonify({
            'success': True,
            'data': {
                'status': 'ready',
                'training_method': 'text_analysis',
                'last_training': '2024-08-28T18:00:00Z',
                'content_analyzed': True,
                'profile_generated': True,
                'recommendations_available': True,
                'api_dependency': False,
                'message': 'Brand voice training uses advanced text analysis - no API tokens required!'
            },
            'message': 'Training status retrieved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get training status: {str(e)}'
        }), 500

