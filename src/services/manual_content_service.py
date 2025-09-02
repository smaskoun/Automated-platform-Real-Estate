import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid
import re

class ManualContentService:
    """Service for managing manually uploaded social media content"""
    
    def __init__(self):
        self.content_storage_path = os.path.join(
            os.path.dirname(__file__), '..', 'data', 'manual_content'
        )
        self.ensure_storage_directory()
    
    def ensure_storage_directory(self):
        """Ensure the content storage directory exists"""
        os.makedirs(self.content_storage_path, exist_ok=True)
    
    def save_content(self, content_data: Dict) -> str:
        """
        Save manually uploaded content
        
        Args:
            content_data: Dictionary containing content information
            
        Returns:
            Content ID for the saved content
        """
        content_id = str(uuid.uuid4())
        
        # Add metadata
        content_data.update({
            'id': content_id,
            'uploaded_at': datetime.now().isoformat(),
            'status': 'active'
        })
        
        # Save to file
        file_path = os.path.join(self.content_storage_path, f"{content_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        
        return content_id
    
    def get_content(self, content_id: str) -> Optional[Dict]:
        """Get content by ID"""
        file_path = os.path.join(self.content_storage_path, f"{content_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def get_all_content(self, limit: int = 50) -> List[Dict]:
        """Get all content, sorted by upload date"""
        content_list = []
        
        for filename in os.listdir(self.content_storage_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.content_storage_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                        content_list.append(content)
                except Exception:
                    continue
        
        # Sort by upload date (newest first)
        content_list.sort(
            key=lambda x: x.get('uploaded_at', ''), 
            reverse=True
        )
        
        return content_list[:limit]
    
    def update_content(self, content_id: str, updates: Dict) -> bool:
        """Update existing content"""
        content = self.get_content(content_id)
        if not content:
            return False
        
        # Update fields
        content.update(updates)
        content['updated_at'] = datetime.now().isoformat()
        
        # Save back to file
        file_path = os.path.join(self.content_storage_path, f"{content_id}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def delete_content(self, content_id: str) -> bool:
        """Delete content by ID"""
        file_path = os.path.join(self.content_storage_path, f"{content_id}.json")
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception:
                return False
        
        return False
    
    def search_content(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search content by text or filters"""
        all_content = self.get_all_content()
        results = []
        
        query_lower = query.lower() if query else ""
        
        for content in all_content:
            # Text search
            if query_lower:
                searchable_text = " ".join([
                    content.get('text', ''),
                    content.get('caption', ''),
                    content.get('platform', ''),
                    " ".join(content.get('hashtags', []))
                ]).lower()
                
                if query_lower not in searchable_text:
                    continue
            
            # Apply filters
            if filters:
                if 'platform' in filters and content.get('platform') != filters['platform']:
                    continue
                if 'date_from' in filters:
                    content_date = content.get('uploaded_at', '')
                    if content_date < filters['date_from']:
                        continue
                if 'date_to' in filters:
                    content_date = content.get('uploaded_at', '')
                    if content_date > filters['date_to']:
                        continue
            
            results.append(content)
        
        return results
    
    def get_content_stats(self) -> Dict:
        """Get statistics about stored content"""
        all_content = self.get_all_content(limit=1000)  # Get more for stats
        
        stats = {
            'total_posts': len(all_content),
            'platforms': {},
            'content_types': {},
            'recent_activity': {},
            'hashtag_usage': {},
            'engagement_summary': {}
        }
        
        # Platform distribution
        for content in all_content:
            platform = content.get('platform', 'unknown')
            stats['platforms'][platform] = stats['platforms'].get(platform, 0) + 1
        
        # Content type distribution
        for content in all_content:
            content_type = content.get('content_type', 'text')
            stats['content_types'][content_type] = stats['content_types'].get(content_type, 0) + 1
        
        # Recent activity (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        recent_content = [c for c in all_content if c.get('uploaded_at', '') > thirty_days_ago]
        stats['recent_activity'] = {
            'posts_last_30_days': len(recent_content),
            'avg_posts_per_day': len(recent_content) / 30
        }
        
        # Hashtag analysis
        hashtag_counts = {}
        for content in all_content:
            hashtags = content.get('hashtags', [])
            for hashtag in hashtags:
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        
        # Top 10 hashtags
        sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
        stats['hashtag_usage'] = dict(sorted_hashtags[:10])
        
        # Engagement summary (if available)
        total_likes = sum(content.get('engagement', {}).get('likes', 0) for content in all_content)
        total_comments = sum(content.get('engagement', {}).get('comments', 0) for content in all_content)
        total_shares = sum(content.get('engagement', {}).get('shares', 0) for content in all_content)
        
        stats['engagement_summary'] = {
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares,
            'avg_likes_per_post': total_likes / len(all_content) if all_content else 0,
            'avg_comments_per_post': total_comments / len(all_content) if all_content else 0
        }
        
        return stats
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, text)
        return [tag.lower() for tag in hashtags]
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        mention_pattern = r'@\w+'
        mentions = re.findall(mention_pattern, text)
        return [mention.lower() for mention in mentions]
    
    def process_content_upload(self, content_data: Dict) -> Dict:
        """
        Process and enrich uploaded content
        
        Args:
            content_data: Raw content data from upload
            
        Returns:
            Processed content with extracted metadata
        """
        text = content_data.get('text', '') or content_data.get('caption', '')
        
        # Extract hashtags and mentions
        hashtags = self.extract_hashtags(text)
        mentions = self.extract_mentions(text)
        
        # Analyze content characteristics
        word_count = len(text.split()) if text else 0
        char_count = len(text) if text else 0
        
        # Determine content type
        content_type = 'text'
        if content_data.get('image_url') or content_data.get('images'):
            content_type = 'image_with_text' if text else 'image'
        elif content_data.get('video_url'):
            content_type = 'video_with_text' if text else 'video'
        
        # Enrich the content data
        enriched_data = {
            **content_data,
            'hashtags': hashtags,
            'mentions': mentions,
            'content_type': content_type,
            'word_count': word_count,
            'char_count': char_count,
            'has_cta': self._detect_call_to_action(text),
            'sentiment': self._analyze_basic_sentiment(text),
            'processed_at': datetime.now().isoformat()
        }
        
        return enriched_data
    
    def _detect_call_to_action(self, text: str) -> bool:
        """Detect if text contains call-to-action phrases"""
        if not text:
            return False
        
        cta_phrases = [
            'contact me', 'call me', 'dm me', 'message me', 'text me',
            'reach out', 'get in touch', 'let\'s talk', 'let\'s chat',
            'schedule', 'book', 'visit', 'see more', 'click here',
            'learn more', 'find out', 'discover', 'explore',
            'sign up', 'register', 'subscribe', 'follow',
            'buy now', 'shop now', 'order now', 'get started'
        ]
        
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in cta_phrases)
    
    def _analyze_basic_sentiment(self, text: str) -> str:
        """Basic sentiment analysis"""
        if not text:
            return 'neutral'
        
        positive_words = [
            'amazing', 'awesome', 'beautiful', 'best', 'excellent', 'fantastic',
            'great', 'happy', 'incredible', 'love', 'perfect', 'wonderful',
            'excited', 'thrilled', 'delighted', 'pleased', 'satisfied'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate',
            'disappointed', 'frustrated', 'angry', 'sad', 'upset'
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def export_content(self, format_type: str = 'json') -> str:
        """Export all content in specified format"""
        all_content = self.get_all_content(limit=1000)
        
        if format_type == 'json':
            return json.dumps(all_content, indent=2, ensure_ascii=False)
        elif format_type == 'csv':
            # Simple CSV export
            if not all_content:
                return "No content to export"
            
            # Get all unique keys
            all_keys = set()
            for content in all_content:
                all_keys.update(content.keys())
            
            csv_lines = [','.join(sorted(all_keys))]
            
            for content in all_content:
                row = []
                for key in sorted(all_keys):
                    value = content.get(key, '')
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value)
                    row.append(f'"{str(value).replace(chr(34), chr(34)+chr(34))}"')
                csv_lines.append(','.join(row))
            
            return '\n'.join(csv_lines)
        
        return "Unsupported format"
    
    def import_content(self, content_list: List[Dict]) -> Dict:
        """Import content from external source"""
        results = {
            'imported': 0,
            'failed': 0,
            'errors': []
        }
        
        for content_data in content_list:
            try:
                processed_content = self.process_content_upload(content_data)
                content_id = self.save_content(processed_content)
                results['imported'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
        
        return results

