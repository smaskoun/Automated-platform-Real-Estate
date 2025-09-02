from flask import Blueprint, request, jsonify
from src.services.manual_content_service import ManualContentService
from src.services.alternative_brand_voice_service import AlternativeBrandVoiceService
import json
import os
from datetime import datetime

manual_content_bp = Blueprint('manual_content', __name__)
content_service = ManualContentService()
brand_voice_service = AlternativeBrandVoiceService()

@manual_content_bp.route('/upload', methods=['POST'])
def upload_content():
    """Upload social media content manually"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        if not data.get('text') and not data.get('caption'):
            return jsonify({
                'success': False,
                'error': 'Text or caption is required'
            }), 400
        
        # Process and save content
        processed_content = content_service.process_content_upload(data)
        content_id = content_service.save_content(processed_content)
        
        return jsonify({
            'success': True,
            'data': {
                'content_id': content_id,
                'processed_content': processed_content
            },
            'message': 'Content uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@manual_content_bp.route('/bulk-upload', methods=['POST'])
def bulk_upload_content():
    """Upload multiple social media posts at once"""
    try:
        data = request.get_json()
        
        if not data or 'content_list' not in data:
            return jsonify({
                'success': False,
                'error': 'Content list is required'
            }), 400
        
        content_list = data['content_list']
        
        if not isinstance(content_list, list):
            return jsonify({
                'success': False,
                'error': 'Content list must be an array'
            }), 400
        
        # Process each content item
        results = {
            'uploaded': 0,
            'failed': 0,
            'content_ids': [],
            'errors': []
        }
        
        for i, content_data in enumerate(content_list):
            try:
                processed_content = content_service.process_content_upload(content_data)
                content_id = content_service.save_content(processed_content)
                results['uploaded'] += 1
                results['content_ids'].append(content_id)
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Item {i+1}: {str(e)}")
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'Bulk upload completed: {results["uploaded"]} uploaded, {results["failed"]} failed'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Bulk upload failed: {str(e)}'
        }), 500

@manual_content_bp.route('/content', methods=['GET'])
def get_all_content():
    """Get all uploaded content"""
    try:
        limit = request.args.get('limit', 50, type=int)
        content_list = content_service.get_all_content(limit)
        
        return jsonify({
            'success': True,
            'data': {
                'content': content_list,
                'total': len(content_list)
            },
            'message': 'Content retrieved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve content: {str(e)}'
        }), 500

@manual_content_bp.route('/content/<content_id>', methods=['GET'])
def get_content_by_id(content_id):
    """Get specific content by ID"""
    try:
        content = content_service.get_content(content_id)
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Content not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': content,
            'message': 'Content retrieved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve content: {str(e)}'
        }), 500

@manual_content_bp.route('/content/<content_id>', methods=['PUT'])
def update_content(content_id):
    """Update existing content"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No update data provided'
            }), 400
        
        success = content_service.update_content(content_id, data)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Content not found or update failed'
            }), 404
        
        # Get updated content
        updated_content = content_service.get_content(content_id)
        
        return jsonify({
            'success': True,
            'data': updated_content,
            'message': 'Content updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Update failed: {str(e)}'
        }), 500

@manual_content_bp.route('/content/<content_id>', methods=['DELETE'])
def delete_content(content_id):
    """Delete content by ID"""
    try:
        success = content_service.delete_content(content_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Content not found or deletion failed'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Content deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Deletion failed: {str(e)}'
        }), 500

@manual_content_bp.route('/search', methods=['GET'])
def search_content():
    """Search content by query and filters"""
    try:
        query = request.args.get('q', '')
        platform = request.args.get('platform')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        filters = {}
        if platform:
            filters['platform'] = platform
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to
        
        results = content_service.search_content(query, filters)
        
        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'total': len(results),
                'query': query,
                'filters': filters
            },
            'message': 'Search completed successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        }), 500

@manual_content_bp.route('/stats', methods=['GET'])
def get_content_stats():
    """Get content statistics"""
    try:
        stats = content_service.get_content_stats()
        
        return jsonify({
            'success': True,
            'data': stats,
            'message': 'Statistics retrieved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve statistics: {str(e)}'
        }), 500

@manual_content_bp.route('/analyze-voice', methods=['POST'])
def analyze_content_voice():
    """Analyze brand voice from uploaded content"""
    try:
        data = request.get_json()
        
        # Get content IDs or use all content
        content_ids = data.get('content_ids', [])
        
        if content_ids:
            # Analyze specific content
            content_texts = []
            for content_id in content_ids:
                content = content_service.get_content(content_id)
                if content:
                    text = content.get('text', '') or content.get('caption', '')
                    if text:
                        content_texts.append(text)
        else:
            # Analyze all content
            all_content = content_service.get_all_content(limit=100)
            content_texts = []
            for content in all_content:
                text = content.get('text', '') or content.get('caption', '')
                if text:
                    content_texts.append(text)
        
        if not content_texts:
            return jsonify({
                'success': False,
                'error': 'No content found for analysis'
            }), 400
        
        # Combine all texts for analysis
        combined_text = '\n\n'.join(content_texts)
        
        # Analyze brand voice
        analysis_result = brand_voice_service.analyze_from_text_input(combined_text, 'posts')
        
        return jsonify({
            'success': True,
            'data': analysis_result,
            'message': f'Brand voice analysis completed for {len(content_texts)} posts'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Voice analysis failed: {str(e)}'
        }), 500

@manual_content_bp.route('/export', methods=['GET'])
def export_content():
    """Export all content"""
    try:
        format_type = request.args.get('format', 'json')
        
        if format_type not in ['json', 'csv']:
            return jsonify({
                'success': False,
                'error': 'Unsupported format. Use json or csv'
            }), 400
        
        exported_data = content_service.export_content(format_type)
        
        return jsonify({
            'success': True,
            'data': {
                'format': format_type,
                'content': exported_data
            },
            'message': 'Content exported successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Export failed: {str(e)}'
        }), 500

@manual_content_bp.route('/import', methods=['POST'])
def import_content():
    """Import content from external source"""
    try:
        data = request.get_json()
        
        if not data or 'content_list' not in data:
            return jsonify({
                'success': False,
                'error': 'Content list is required for import'
            }), 400
        
        content_list = data['content_list']
        results = content_service.import_content(content_list)
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'Import completed: {results["imported"]} imported, {results["failed"]} failed'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Import failed: {str(e)}'
        }), 500

@manual_content_bp.route('/sample-data', methods=['POST'])
def create_sample_data():
    """Create sample social media content for demonstration"""
    try:
        sample_posts = [
            {
                'text': '🏡 Just listed! Beautiful 3-bedroom home in Windsor-Essex with stunning curb appeal and move-in ready condition. This property features an open-concept layout, updated kitchen, and spacious backyard perfect for entertaining. Located in a quiet neighborhood with excellent schools nearby. Ready to find your dream home? Let\'s chat! Send me a DM or call today. 📞✨ #WindsorEssexRealEstate #DreamHome #RealEstateExpert #HomeBuying #PropertyListing',
                'platform': 'instagram',
                'content_type': 'image_with_text',
                'engagement': {'likes': 45, 'comments': 8, 'shares': 3},
                'posted_date': '2024-08-25T10:00:00Z'
            },
            {
                'text': 'Market Update: Windsor-Essex housing market shows strong activity this month! 📈 Average home prices have stabilized, making it a great time for both buyers and sellers. Thinking of making a move? I\'m here to help guide you through every step of the process. With over 10 years of experience in the local market, I provide personalized service and expert advice. Contact me today for a free consultation! #MarketUpdate #WindsorRealEstate #RealEstateAdvice #PropertyMarket',
                'platform': 'facebook',
                'content_type': 'text',
                'engagement': {'likes': 32, 'comments': 12, 'shares': 7},
                'posted_date': '2024-08-24T14:30:00Z'
            },
            {
                'text': 'First-time homebuyer tip: Get pre-approved for your mortgage before you start house hunting! 💡 This crucial step shows sellers you\'re serious and helps you understand your budget. It also speeds up the buying process when you find the perfect home. Need recommendations for trusted mortgage professionals? I\'ve got you covered! Let\'s make your homeownership dreams a reality. #FirstTimeBuyer #MortgagePreApproval #HomeBuyingTips #RealEstateTips #WindsorHomes',
                'platform': 'instagram',
                'content_type': 'image_with_text',
                'engagement': {'likes': 67, 'comments': 15, 'shares': 9},
                'posted_date': '2024-08-23T16:45:00Z'
            },
            {
                'text': 'SOLD! 🎉 Another happy family found their perfect home in Tecumseh! This charming 4-bedroom colonial was on the market for just 5 days. The secret? Proper staging, professional photography, and strategic pricing. Thinking of selling your home? Let\'s discuss how to get you the best results in today\'s market. Your success is my priority! #JustSold #TecumsehHomes #RealEstateSuccess #HomeSelling #PropertySold',
                'platform': 'facebook',
                'content_type': 'image_with_text',
                'engagement': {'likes': 89, 'comments': 23, 'shares': 12},
                'posted_date': '2024-08-22T11:15:00Z'
            },
            {
                'text': 'Weekend Open House Alert! 🏠 Join me this Saturday 2-4 PM for an exclusive viewing of this stunning waterfront property in LaSalle. Features include: ✨ 3 bedrooms, 2.5 baths ✨ Panoramic river views ✨ Updated gourmet kitchen ✨ Private dock access ✨ Beautifully landscaped grounds Don\'t miss this rare opportunity! See you there! #OpenHouse #WaterfrontProperty #LaSalleHomes #RiverView #LuxuryLiving',
                'platform': 'instagram',
                'content_type': 'image_with_text',
                'engagement': {'likes': 78, 'comments': 19, 'shares': 6},
                'posted_date': '2024-08-21T09:30:00Z'
            }
        ]
        
        # Upload sample posts
        results = {
            'uploaded': 0,
            'content_ids': []
        }
        
        for post_data in sample_posts:
            try:
                processed_content = content_service.process_content_upload(post_data)
                content_id = content_service.save_content(processed_content)
                results['uploaded'] += 1
                results['content_ids'].append(content_id)
            except Exception as e:
                continue
        
        return jsonify({
            'success': True,
            'data': results,
            'message': f'Sample data created: {results["uploaded"]} posts uploaded'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create sample data: {str(e)}'
        }), 500

@manual_content_bp.route('/platform-guide', methods=['GET'])
def get_platform_guide():
    """Get guide for using the manual content system"""
    try:
        guide = {
            'overview': 'Manual Content Management System - No API Tokens Required!',
            'features': [
                'Upload social media posts manually',
                'Analyze brand voice from your content',
                'Track engagement metrics',
                'Search and filter content',
                'Export data for analysis',
                'A/B testing without API dependencies'
            ],
            'getting_started': [
                '1. Upload your existing social media posts using the bulk upload feature',
                '2. Use the brand voice analysis to understand your writing style',
                '3. Create A/B tests with different content variations',
                '4. Track performance manually and update engagement data',
                '5. Use insights to improve future content'
            ],
            'upload_formats': {
                'single_post': {
                    'text': 'Post content (required)',
                    'platform': 'instagram, facebook, twitter, linkedin',
                    'content_type': 'text, image_with_text, video_with_text',
                    'engagement': {'likes': 0, 'comments': 0, 'shares': 0},
                    'posted_date': 'ISO date string (optional)'
                },
                'bulk_upload': {
                    'content_list': 'Array of post objects',
                    'note': 'Upload multiple posts at once'
                }
            },
            'benefits': [
                'No Facebook API setup required',
                'Works with any social media platform',
                'Complete control over your data',
                'Advanced analytics and insights',
                'Brand voice training and consistency',
                'A/B testing capabilities'
            ]
        }
        
        return jsonify({
            'success': True,
            'data': guide,
            'message': 'Platform guide retrieved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve guide: {str(e)}'
        }), 500

