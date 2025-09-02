import re
import json
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter
import statistics

class BrandVoiceService:
    """Service for analyzing and learning user's brand voice from social media content"""
    
    def __init__(self):
        self.voice_profile = {
            'tone_indicators': {},
            'common_phrases': [],
            'sentence_patterns': [],
            'vocabulary_preferences': {},
            'punctuation_style': {},
            'emoji_usage': {},
            'call_to_action_style': [],
            'greeting_style': [],
            'closing_style': []
        }
        
        # Tone analysis keywords
        self.tone_keywords = {
            'professional': [
                'expertise', 'experience', 'professional', 'service', 'consultation',
                'analysis', 'market', 'investment', 'strategy', 'guidance'
            ],
            'friendly': [
                'love', 'excited', 'happy', 'amazing', 'wonderful', 'great',
                'fantastic', 'awesome', 'beautiful', 'perfect'
            ],
            'educational': [
                'tip', 'learn', 'understand', 'know', 'important', 'remember',
                'consider', 'advice', 'guide', 'help'
            ],
            'motivational': [
                'achieve', 'success', 'dream', 'goal', 'opportunity', 'potential',
                'future', 'possible', 'believe', 'confidence'
            ],
            'urgent': [
                'now', 'today', 'immediately', 'quick', 'fast', 'urgent',
                'limited', 'hurry', 'soon', 'deadline'
            ]
        }
        
        # Common real estate phrases to identify
        self.real_estate_phrases = [
            'just listed', 'new on the market', 'price reduced', 'open house',
            'under contract', 'sold', 'coming soon', 'market update',
            'home buying tips', 'selling your home', 'first time buyer',
            'investment opportunity', 'market analysis', 'property value'
        ]
    
    def fetch_user_posts(self, access_token: str, platform: str = 'facebook', limit: int = 50) -> List[Dict]:
        """
        Fetch user's recent posts from Facebook/Instagram
        
        Args:
            access_token: User's social media access token
            platform: 'facebook' or 'instagram'
            limit: Number of posts to fetch
        
        Returns:
            List of post data dictionaries
        """
        posts = []
        
        try:
            if platform == 'facebook':
                # Facebook Graph API endpoint for user's posts
                url = f"https://graph.facebook.com/v18.0/me/posts"
                params = {
                    'access_token': access_token,
                    'fields': 'message,created_time,engagement',
                    'limit': limit
                }
                
            elif platform == 'instagram':
                # Instagram Basic Display API endpoint
                url = f"https://graph.instagram.com/me/media"
                params = {
                    'access_token': access_token,
                    'fields': 'caption,timestamp,like_count,comments_count',
                    'limit': limit
                }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                for post in data.get('data', []):
                    if platform == 'facebook':
                        text_content = post.get('message', '')
                    else:  # Instagram
                        text_content = post.get('caption', '')
                    
                    if text_content:  # Only include posts with text content
                        posts.append({
                            'text': text_content,
                            'created_time': post.get('created_time') or post.get('timestamp'),
                            'engagement': post.get('engagement') or {
                                'likes': post.get('like_count', 0),
                                'comments': post.get('comments_count', 0)
                            },
                            'platform': platform
                        })
            
        except Exception as e:
            print(f"Error fetching posts: {str(e)}")
        
        return posts
    
    def analyze_writing_style(self, posts: List[Dict]) -> Dict:
        """
        Analyze writing style from a collection of posts
        
        Args:
            posts: List of post dictionaries with 'text' field
        
        Returns:
            Dictionary containing style analysis
        """
        if not posts:
            return {}
        
        all_text = [post['text'] for post in posts if post.get('text')]
        
        analysis = {
            'tone_analysis': self._analyze_tone(all_text),
            'sentence_structure': self._analyze_sentence_structure(all_text),
            'vocabulary_analysis': self._analyze_vocabulary(all_text),
            'punctuation_patterns': self._analyze_punctuation(all_text),
            'emoji_patterns': self._analyze_emoji_usage(all_text),
            'cta_patterns': self._analyze_cta_patterns(all_text),
            'greeting_patterns': self._analyze_greeting_patterns(all_text),
            'closing_patterns': self._analyze_closing_patterns(all_text),
            'content_themes': self._analyze_content_themes(all_text),
            'engagement_correlation': self._analyze_engagement_correlation(posts)
        }
        
        return analysis
    
    def _analyze_tone(self, texts: List[str]) -> Dict:
        """Analyze the overall tone of the writing"""
        tone_scores = {tone: 0 for tone in self.tone_keywords.keys()}
        total_words = 0
        
        for text in texts:
            words = text.lower().split()
            total_words += len(words)
            
            for tone, keywords in self.tone_keywords.items():
                for keyword in keywords:
                    tone_scores[tone] += text.lower().count(keyword)
        
        # Normalize scores
        if total_words > 0:
            for tone in tone_scores:
                tone_scores[tone] = (tone_scores[tone] / total_words) * 100
        
        return tone_scores
    
    def _analyze_sentence_structure(self, texts: List[str]) -> Dict:
        """Analyze sentence structure patterns"""
        sentence_lengths = []
        question_count = 0
        exclamation_count = 0
        total_sentences = 0
        
        for text in texts:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            for sentence in sentences:
                sentence_lengths.append(len(sentence.split()))
                total_sentences += 1
                
                if '?' in sentence:
                    question_count += 1
                if '!' in sentence:
                    exclamation_count += 1
        
        return {
            'avg_sentence_length': statistics.mean(sentence_lengths) if sentence_lengths else 0,
            'question_frequency': (question_count / total_sentences) * 100 if total_sentences > 0 else 0,
            'exclamation_frequency': (exclamation_count / total_sentences) * 100 if total_sentences > 0 else 0,
            'sentence_length_variance': statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0
        }
    
    def _analyze_vocabulary(self, texts: List[str]) -> Dict:
        """Analyze vocabulary preferences and word usage"""
        all_words = []
        
        for text in texts:
            # Remove punctuation and convert to lowercase
            clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
            words = clean_text.split()
            all_words.extend(words)
        
        word_freq = Counter(all_words)
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        filtered_freq = {word: count for word, count in word_freq.items() 
                        if word not in stop_words and len(word) > 2}
        
        return {
            'most_common_words': dict(Counter(filtered_freq).most_common(20)),
            'vocabulary_size': len(set(all_words)),
            'avg_word_length': statistics.mean([len(word) for word in all_words]) if all_words else 0
        }
    
    def _analyze_punctuation(self, texts: List[str]) -> Dict:
        """Analyze punctuation usage patterns"""
        punctuation_counts = Counter()
        total_chars = 0
        
        for text in texts:
            total_chars += len(text)
            for char in text:
                if char in '.,!?;:()[]{}"-':
                    punctuation_counts[char] += 1
        
        # Normalize by total character count
        punctuation_freq = {punct: (count / total_chars) * 100 
                           for punct, count in punctuation_counts.items()}
        
        return punctuation_freq
    
    def _analyze_emoji_usage(self, texts: List[str]) -> Dict:
        """Analyze emoji usage patterns"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        
        all_emojis = []
        emoji_positions = []  # Track where emojis appear (beginning, middle, end)
        
        for text in texts:
            emojis = emoji_pattern.findall(text)
            all_emojis.extend(emojis)
            
            # Analyze emoji positions
            text_length = len(text)
            for match in emoji_pattern.finditer(text):
                position = match.start() / text_length
                if position < 0.2:
                    emoji_positions.append('beginning')
                elif position > 0.8:
                    emoji_positions.append('end')
                else:
                    emoji_positions.append('middle')
        
        emoji_freq = Counter(all_emojis)
        position_freq = Counter(emoji_positions)
        
        return {
            'most_used_emojis': dict(emoji_freq.most_common(10)),
            'emoji_frequency': len(all_emojis) / len(texts) if texts else 0,
            'position_preferences': dict(position_freq)
        }
    
    def _analyze_cta_patterns(self, texts: List[str]) -> List[str]:
        """Analyze call-to-action patterns"""
        cta_patterns = []
        
        cta_indicators = [
            r'contact me', r'call me', r'dm me', r'message me',
            r'reach out', r'get in touch', r'let\'s talk',
            r'schedule', r'book', r'visit', r'see more',
            r'learn more', r'find out', r'discover'
        ]
        
        for text in texts:
            text_lower = text.lower()
            for pattern in cta_indicators:
                matches = re.findall(pattern, text_lower)
                if matches:
                    # Extract the sentence containing the CTA
                    sentences = re.split(r'[.!?]+', text)
                    for sentence in sentences:
                        if any(re.search(pattern, sentence.lower()) for pattern in cta_indicators):
                            cta_patterns.append(sentence.strip())
                            break
        
        return list(set(cta_patterns))  # Remove duplicates
    
    def _analyze_greeting_patterns(self, texts: List[str]) -> List[str]:
        """Analyze greeting and opening patterns"""
        greeting_patterns = []
        
        for text in texts:
            # Get first sentence
            first_sentence = re.split(r'[.!?]+', text)[0].strip()
            if len(first_sentence) < 100:  # Likely a greeting if short
                greeting_patterns.append(first_sentence)
        
        return list(set(greeting_patterns))
    
    def _analyze_closing_patterns(self, texts: List[str]) -> List[str]:
        """Analyze closing and ending patterns"""
        closing_patterns = []
        
        for text in texts:
            # Get last sentence
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
            if sentences:
                last_sentence = sentences[-1]
                if len(last_sentence) < 100:  # Likely a closing if short
                    closing_patterns.append(last_sentence)
        
        return list(set(closing_patterns))
    
    def _analyze_content_themes(self, texts: List[str]) -> Dict:
        """Analyze common content themes"""
        theme_counts = Counter()
        
        for text in texts:
            text_lower = text.lower()
            for phrase in self.real_estate_phrases:
                if phrase in text_lower:
                    theme_counts[phrase] += 1
        
        return dict(theme_counts.most_common(10))
    
    def _analyze_engagement_correlation(self, posts: List[Dict]) -> Dict:
        """Analyze correlation between writing style and engagement"""
        if not posts:
            return {}
        
        high_engagement_posts = []
        low_engagement_posts = []
        
        # Calculate engagement scores
        engagement_scores = []
        for post in posts:
            engagement = post.get('engagement', {})
            likes = engagement.get('likes', 0)
            comments = engagement.get('comments', 0)
            score = likes + (comments * 2)  # Weight comments higher
            engagement_scores.append(score)
        
        if not engagement_scores:
            return {}
        
        median_engagement = statistics.median(engagement_scores)
        
        for i, post in enumerate(posts):
            if engagement_scores[i] > median_engagement:
                high_engagement_posts.append(post['text'])
            else:
                low_engagement_posts.append(post['text'])
        
        return {
            'high_engagement_characteristics': self._get_text_characteristics(high_engagement_posts),
            'low_engagement_characteristics': self._get_text_characteristics(low_engagement_posts),
            'median_engagement': median_engagement
        }
    
    def _get_text_characteristics(self, texts: List[str]) -> Dict:
        """Get basic characteristics of a text collection"""
        if not texts:
            return {}
        
        total_length = sum(len(text) for text in texts)
        avg_length = total_length / len(texts)
        
        question_count = sum(text.count('?') for text in texts)
        exclamation_count = sum(text.count('!') for text in texts)
        
        return {
            'avg_length': avg_length,
            'question_frequency': question_count / len(texts),
            'exclamation_frequency': exclamation_count / len(texts),
            'sample_count': len(texts)
        }
    
    def create_brand_voice_profile(self, analysis: Dict) -> Dict:
        """Create a brand voice profile from analysis results"""
        profile = {
            'dominant_tone': max(analysis.get('tone_analysis', {}), 
                               key=analysis.get('tone_analysis', {}).get, default='professional'),
            'writing_style': {
                'avg_sentence_length': analysis.get('sentence_structure', {}).get('avg_sentence_length', 15),
                'uses_questions': analysis.get('sentence_structure', {}).get('question_frequency', 0) > 10,
                'uses_exclamations': analysis.get('sentence_structure', {}).get('exclamation_frequency', 0) > 5,
                'emoji_frequency': analysis.get('emoji_patterns', {}).get('emoji_frequency', 0)
            },
            'vocabulary_preferences': analysis.get('vocabulary_analysis', {}).get('most_common_words', {}),
            'signature_phrases': analysis.get('cta_patterns', [])[:5],
            'greeting_style': analysis.get('greeting_patterns', [])[:3],
            'closing_style': analysis.get('closing_patterns', [])[:3],
            'content_themes': analysis.get('content_themes', {}),
            'engagement_insights': analysis.get('engagement_correlation', {})
        }
        
        return profile
    
    def generate_content_with_voice(self, content_template: str, voice_profile: Dict) -> str:
        """Generate content using the learned brand voice"""
        # This would integrate with the existing SEO content service
        # to modify generated content based on the voice profile
        
        # Apply tone adjustments
        dominant_tone = voice_profile.get('dominant_tone', 'professional')
        
        # Apply vocabulary preferences
        common_words = voice_profile.get('vocabulary_preferences', {})
        
        # Apply signature phrases
        signature_phrases = voice_profile.get('signature_phrases', [])
        
        # Apply greeting/closing styles
        greeting_options = voice_profile.get('greeting_style', [])
        closing_options = voice_profile.get('closing_style', [])
        
        # This is a simplified implementation
        # In practice, this would use more sophisticated NLP techniques
        modified_content = content_template
        
        return modified_content

# Global instance
brand_voice_service = BrandVoiceService()

