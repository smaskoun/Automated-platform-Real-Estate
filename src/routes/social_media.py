from flask import Blueprint, request, jsonify, session, redirect, url_for
from src.models.social_media import db, SocialMediaAccount, SocialMediaPost, AIImageGeneration
import requests
import os
import json
from datetime import datetime, timedelta
import hashlib
import hmac
import base64
from cryptography.fernet import Fernet
import logging

social_media_bp = Blueprint('social_media', __name__)

# Configuration - In production, these should be environment variables
FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID', 'your_facebook_app_id')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET', 'your_facebook_app_secret')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', 'your_huggingface_api_key')

# Initialize encryption
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_token(token):
    """Encrypt access token for secure storage"""
    return cipher_suite.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token):
    """Decrypt access token for use"""
    return cipher_suite.decrypt(encrypted_token.encode()).decode()

@social_media_bp.route('/auth/facebook/login', methods=['GET'])
def facebook_login():
    """Initiate Facebook OAuth flow"""
    redirect_uri = request.args.get('redirect_uri', request.host_url + 'api/auth/facebook/callback')
    
    facebook_auth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={FACEBOOK_APP_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=pages_manage_posts,pages_read_engagement,instagram_basic,instagram_content_publish&"
        f"response_type=code&"
        f"state={generate_state_token()}"
    )
    
    return jsonify({
        'auth_url': facebook_auth_url,
        'redirect_uri': redirect_uri
    })

@social_media_bp.route('/auth/facebook/callback', methods=['GET'])
def facebook_callback():
    """Handle Facebook OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    if error:
        return jsonify({'error': f'Facebook authentication failed: {error}'}), 400
    
    if not code:
        return jsonify({'error': 'No authorization code received'}), 400
    
    # Exchange code for access token
    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    token_params = {
        'client_id': FACEBOOK_APP_ID,
        'client_secret': FACEBOOK_APP_SECRET,
        'redirect_uri': request.host_url + 'api/auth/facebook/callback',
        'code': code
    }
    
    try:
        token_response = requests.get(token_url, params=token_params)
        token_data = token_response.json()
        
        if 'access_token' not in token_data:
            return jsonify({'error': 'Failed to obtain access token'}), 400
        
        access_token = token_data['access_token']
        
        # Get user's Facebook pages and Instagram accounts
        accounts = get_user_accounts(access_token)
        
        return jsonify({
            'success': True,
            'accounts': accounts,
            'access_token': access_token  # In production, don't return this directly
        })
        
    except Exception as e:
        logging.error(f"Facebook callback error: {str(e)}")
        return jsonify({'error': 'Authentication failed'}), 500

@social_media_bp.route('/accounts', methods=['GET'])
def get_accounts():
    """Get user's connected social media accounts"""
    user_id = request.args.get('user_id', 'default_user')
    
    accounts = SocialMediaAccount.query.filter_by(user_id=user_id, is_active=True).all()
    
    return jsonify({
        'accounts': [account.to_dict() for account in accounts]
    })

@social_media_bp.route('/accounts', methods=['POST'])
def connect_account():
    """Connect a new social media account"""
    data = request.get_json()
    
    required_fields = ['user_id', 'platform', 'account_id', 'account_name', 'access_token']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Encrypt the access token
    encrypted_token = encrypt_token(data['access_token'])
    
    # Check if account already exists
    existing_account = SocialMediaAccount.query.filter_by(
        user_id=data['user_id'],
        platform=data['platform'],
        account_id=data['account_id']
    ).first()
    
    if existing_account:
        # Update existing account
        existing_account.access_token = encrypted_token
        existing_account.account_name = data['account_name']
        existing_account.is_active = True
        existing_account.updated_at = datetime.utcnow()
        account = existing_account
    else:
        # Create new account
        account = SocialMediaAccount(
            user_id=data['user_id'],
            platform=data['platform'],
            account_id=data['account_id'],
            account_name=data['account_name'],
            access_token=encrypted_token,
            token_expires_at=datetime.utcnow() + timedelta(days=60)  # Facebook tokens typically last 60 days
        )
        db.session.add(account)
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'account': account.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error connecting account: {str(e)}")
        return jsonify({'error': 'Failed to connect account'}), 500

@social_media_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
def disconnect_account(account_id):
    """Disconnect a social media account"""
    account = SocialMediaAccount.query.get_or_404(account_id)
    
    try:
        account.is_active = False
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Account disconnected'})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error disconnecting account: {str(e)}")
        return jsonify({'error': 'Failed to disconnect account'}), 500

@social_media_bp.route('/posts', methods=['GET'])
def get_posts():
    """Get user's social media posts"""
    user_id = request.args.get('user_id', 'default_user')
    status = request.args.get('status')  # Optional filter by status
    
    query = db.session.query(SocialMediaPost).join(SocialMediaAccount).filter(
        SocialMediaAccount.user_id == user_id
    )
    
    if status:
        query = query.filter(SocialMediaPost.status == status)
    
    posts = query.order_by(SocialMediaPost.created_at.desc()).all()
    
    return jsonify({
        'posts': [post.to_dict() for post in posts]
    })

@social_media_bp.route('/posts', methods=['POST'])
def create_post():
    """Create a new social media post"""
    data = request.get_json()
    
    required_fields = ['account_id', 'content']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify account exists and is active
    account = SocialMediaAccount.query.filter_by(
        id=data['account_id'],
        is_active=True
    ).first()
    
    if not account:
        return jsonify({'error': 'Account not found or inactive'}), 404
    
    # Create post record
    post = SocialMediaPost(
        account_id=data['account_id'],
        content=data['content'],
        image_prompt=data.get('image_prompt'),
        hashtags=json.dumps(data.get('hashtags', [])),
        scheduled_at=datetime.fromisoformat(data['scheduled_at']) if data.get('scheduled_at') else None
    )
    
    try:
        db.session.add(post)
        db.session.commit()
        
        # If image prompt provided, generate image
        if data.get('image_prompt'):
            generate_image_for_post(post.id, data['image_prompt'])
        
        return jsonify({
            'success': True,
            'post': post.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating post: {str(e)}")
        return jsonify({'error': 'Failed to create post'}), 500

@social_media_bp.route('/posts/<int:post_id>/approve', methods=['POST'])
def approve_post(post_id):
    """Approve a post for publishing"""
    post = SocialMediaPost.query.get_or_404(post_id)
    
    if post.status != 'draft':
        return jsonify({'error': 'Post is not in draft status'}), 400
    
    try:
        post.status = 'approved'
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        # If scheduled, it will be posted automatically
        # If not scheduled, post immediately
        if not post.scheduled_at:
            publish_post_now(post_id)
        
        return jsonify({
            'success': True,
            'post': post.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error approving post: {str(e)}")
        return jsonify({'error': 'Failed to approve post'}), 500

@social_media_bp.route('/posts/<int:post_id>/publish', methods=['POST'])
def publish_post(post_id):
    """Manually publish a post immediately"""
    return publish_post_now(post_id)

@social_media_bp.route('/images/generate', methods=['POST'])
def generate_image():
    """Generate an AI image from a prompt"""
    data = request.get_json()
    
    if 'prompt' not in data:
        return jsonify({'error': 'Prompt is required'}), 400
    
    prompt = data['prompt']
    platform = data.get('platform', 'instagram')
    content_type = data.get('content_type', 'post')
    model = data.get('model', 'stable-diffusion-v1-5')
    provider = data.get('provider', 'auto')
    
    # Create image generation record
    image_gen = AIImageGeneration(
        prompt=prompt,
        model_used=f"{provider}:{model}",
        status='pending'
    )
    
    try:
        db.session.add(image_gen)
        db.session.commit()
        
        # Generate image using AI service
        from src.services.ai_image_service import ai_image_service
        
        start_time = time.time()
        result = ai_image_service.generate_social_media_image(
            prompt=prompt,
            platform=platform,
            content_type=content_type,
            model=model,
            provider=provider
        )
        generation_time = time.time() - start_time
        
        # Update image generation record
        image_gen.generation_time = generation_time
        
        if result['success']:
            image_gen.image_url = result['image_url']
            image_gen.status = 'completed'
            image_gen.model_used = f"{result.get('provider', provider)}:{result.get('model', model)}"
        else:
            image_gen.status = 'failed'
            image_gen.error_message = result.get('error', 'Unknown error')
        
        db.session.commit()
        
        return jsonify({
            'success': result['success'],
            'image': image_gen.to_dict(),
            'generation_details': result if result['success'] else None
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error generating image: {str(e)}")
        return jsonify({'error': 'Failed to generate image'}), 500

# Helper functions

def generate_state_token():
    """Generate a random state token for OAuth security"""
    import secrets
    return secrets.token_urlsafe(32)

def get_user_accounts(access_token):
    """Get user's Facebook pages and Instagram accounts"""
    try:
        # Get Facebook pages
        pages_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={access_token}"
        pages_response = requests.get(pages_url)
        pages_data = pages_response.json()
        
        accounts = []
        
        if 'data' in pages_data:
            for page in pages_data['data']:
                # Add Facebook page
                accounts.append({
                    'platform': 'facebook',
                    'account_id': page['id'],
                    'account_name': page['name'],
                    'access_token': page['access_token']
                })
                
                # Check for connected Instagram account
                instagram_url = f"https://graph.facebook.com/v18.0/{page['id']}?fields=instagram_business_account&access_token={page['access_token']}"
                instagram_response = requests.get(instagram_url)
                instagram_data = instagram_response.json()
                
                if 'instagram_business_account' in instagram_data:
                    ig_account = instagram_data['instagram_business_account']
                    
                    # Get Instagram account details
                    ig_details_url = f"https://graph.facebook.com/v18.0/{ig_account['id']}?fields=username&access_token={page['access_token']}"
                    ig_details_response = requests.get(ig_details_url)
                    ig_details_data = ig_details_response.json()
                    
                    accounts.append({
                        'platform': 'instagram',
                        'account_id': ig_account['id'],
                        'account_name': f"@{ig_details_data.get('username', 'Unknown')}",
                        'access_token': page['access_token']
                    })
        
        return accounts
        
    except Exception as e:
        logging.error(f"Error getting user accounts: {str(e)}")
        return []

def generate_image_for_post(post_id, prompt, platform='instagram'):
    """Generate image for a specific post using AI image service"""
    try:
        from src.services.ai_image_service import ai_image_service
        
        # Generate image optimized for the platform
        result = ai_image_service.generate_social_media_image(
            prompt=prompt,
            platform=platform,
            content_type='post'
        )
        
        if result['success']:
            post = SocialMediaPost.query.get(post_id)
            if post:
                post.image_url = result['image_url']
                db.session.commit()
                return result['image_url']
        else:
            logging.error(f"Failed to generate image for post {post_id}: {result.get('error', 'Unknown error')}")
            return None
                
    except Exception as e:
        logging.error(f"Error generating image for post {post_id}: {str(e)}")
        return None

def publish_post_now(post_id):
    """Publish a post immediately to the social media platform"""
    post = SocialMediaPost.query.get_or_404(post_id)
    account = post.account
    
    if not account or not account.is_active:
        return jsonify({'error': 'Account not found or inactive'}), 404
    
    try:
        # Decrypt access token
        access_token = decrypt_token(account.access_token)
        
        if account.platform == 'facebook':
            success = publish_to_facebook(post, access_token)
        elif account.platform == 'instagram':
            success = publish_to_instagram(post, access_token)
        else:
            return jsonify({'error': 'Unsupported platform'}), 400
        
        if success:
            post.status = 'posted'
            post.posted_at = datetime.utcnow()
        else:
            post.status = 'failed'
            post.error_message = 'Failed to publish to platform'
        
        db.session.commit()
        
        return jsonify({
            'success': success,
            'post': post.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error publishing post {post_id}: {str(e)}")
        return jsonify({'error': 'Failed to publish post'}), 500

def publish_to_facebook(post, access_token):
    """Publish post to Facebook"""
    try:
        url = f"https://graph.facebook.com/v18.0/{post.account.account_id}/feed"
        
        data = {
            'message': post.content,
            'access_token': access_token
        }
        
        # Add image if available
        if post.image_url:
            # Convert relative URL to absolute URL
            if post.image_url.startswith('/'):
                data['picture'] = request.host_url.rstrip('/') + post.image_url
            else:
                data['picture'] = post.image_url
        
        response = requests.post(url, data=data)
        result = response.json()
        
        if 'id' in result:
            post.platform_post_id = result['id']
            return True
        else:
            post.error_message = result.get('error', {}).get('message', 'Unknown error')
            return False
            
    except Exception as e:
        logging.error(f"Error publishing to Facebook: {str(e)}")
        post.error_message = str(e)
        return False

def publish_to_instagram(post, access_token):
    """Publish post to Instagram"""
    try:
        # Instagram requires a two-step process: create container, then publish
        
        # Step 1: Create media container
        container_url = f"https://graph.facebook.com/v18.0/{post.account.account_id}/media"
        
        container_data = {
            'caption': post.content,
            'access_token': access_token
        }
        
        # Add image if available
        if post.image_url:
            if post.image_url.startswith('/'):
                container_data['image_url'] = request.host_url.rstrip('/') + post.image_url
            else:
                container_data['image_url'] = post.image_url
        
        container_response = requests.post(container_url, data=container_data)
        container_result = container_response.json()
        
        if 'id' not in container_result:
            post.error_message = container_result.get('error', {}).get('message', 'Failed to create container')
            return False
        
        container_id = container_result['id']
        
        # Step 2: Publish the container
        publish_url = f"https://graph.facebook.com/v18.0/{post.account.account_id}/media_publish"
        
        publish_data = {
            'creation_id': container_id,
            'access_token': access_token
        }
        
        publish_response = requests.post(publish_url, data=publish_data)
        publish_result = publish_response.json()
        
        if 'id' in publish_result:
            post.platform_post_id = publish_result['id']
            return True
        else:
            post.error_message = publish_result.get('error', {}).get('message', 'Failed to publish')
            return False
            
    except Exception as e:
        logging.error(f"Error publishing to Instagram: {str(e)}")
        post.error_message = str(e)
        return False

