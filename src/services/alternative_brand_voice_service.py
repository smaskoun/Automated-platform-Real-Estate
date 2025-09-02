import re
import json
from typing import Dict, List, Optional
from datetime import datetime
from collections import Counter
import statistics

class AlternativeBrandVoiceService:
    """Alternative service for analyzing brand voice from manually provided content"""
    
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
                'analysis', 'market', 'investment', 'strategy', 'guidance', 'qualified',
                'certified', 'licensed', 'proven', 'results'
            ],
            'friendly': [
                'love', 'excited', 'happy', 'amazing', 'wonderful', 'great',
                'fantastic', 'awesome', 'beautiful', 'perfect', 'thrilled',
                'delighted', 'pleased', 'enjoy'
            ],
            'educational': [
                'tip', 'learn', 'understand', 'know', 'important', 'remember',
                'consider', 'advice', 'guide', 'help', 'explain', 'teach',
                'inform', 'educate'
            ],
            'motivational': [
                'achieve', 'success', 'dream', 'goal', 'opportunity', 'potential',
                'future', 'possible', 'believe', 'confidence', 'inspire',
                'motivate', 'empower'
            ],
            'urgent': [
                'now', 'today', 'immediately', 'quick', 'fast', 'urgent',
                'limited', 'hurry', 'soon', 'deadline', 'act', 'don\'t wait'
            ],
            'conversational': [
                'hey', 'hi', 'hello', 'you know', 'let me tell you',
                'guess what', 'by the way', 'speaking of', 'honestly',
                'personally', 'i think', 'in my opinion'
            ]
        }
        
        # Industry-specific phrases (can be customized)
        self.industry_phrases = {
            'real_estate': [
                'just listed', 'new on the market', 'price reduced', 'open house',
                'under contract', 'sold', 'coming soon', 'market update',
                'home buying tips', 'selling your home', 'first time buyer',
                'investment opportunity', 'market analysis', 'property value',
                'dream home', 'perfect location', 'move-in ready'
            ],
            'general_business': [
                'customer service', 'quality products', 'satisfaction guaranteed',
                'free consultation', 'limited time offer', 'special promotion',
                'contact us today', 'learn more', 'get started'
            ]
        }
    
    def analyze_from_text_input(self, content: str, content_type: str = 'mixed') -> Dict:
        """
        Analyze brand voice from manually provided text content
        
        Args:
            content: Raw text content (can be multiple posts separated by newlines)
            content_type: Type of content ('posts', 'website', 'emails', 'mixed')
        
        Returns:
            Dictionary containing comprehensive brand voice analysis
        """
        # Split content into individual pieces if needed
        if content_type == 'posts':
            # Assume each paragraph is a separate post
            posts = [p.strip() for p in content.split('\n\n') if p.strip()]
        else:
            # Treat as continuous content but split by sentences for analysis
            posts = [content]
        
        if not posts:
            return self._get_default_analysis()
        
        analysis = {
            'tone_analysis': self._analyze_tone(posts),
            'sentence_structure': self._analyze_sentence_structure(posts),
            'vocabulary_analysis': self._analyze_vocabulary(posts),
            'punctuation_patterns': self._analyze_punctuation(posts),
            'emoji_patterns': self._analyze_emoji_usage(posts),
            'cta_patterns': self._analyze_cta_patterns(posts),
            'greeting_patterns': self._analyze_greeting_patterns(posts),
            'closing_patterns': self._analyze_closing_patterns(posts),
            'content_themes': self._analyze_content_themes(posts),
            'writing_characteristics': self._analyze_writing_characteristics(posts),
            'brand_voice_score': self._calculate_brand_voice_score(posts)
        }
        
        # Create brand voice profile
        brand_profile = self.create_brand_voice_profile(analysis)
        
        return {
            'analysis': analysis,
            'brand_profile': brand_profile,
            'recommendations': self._generate_recommendations(analysis),
            'content_samples': posts[:5],  # Include first 5 samples
            'analysis_date': datetime.now().isoformat()
        }
    
    def _get_default_analysis(self) -> Dict:
        """Return default analysis when no content is provided"""
        return {
            'analysis': {
                'tone_analysis': {'professional': 70, 'friendly': 20, 'educational': 10},
                'sentence_structure': {'avg_sentence_length': 15, 'question_frequency': 5, 'exclamation_frequency': 3},
                'vocabulary_analysis': {'most_common_words': {}, 'vocabulary_size': 0, 'avg_word_length': 5},
                'punctuation_patterns': {'.': 60, ',': 30, '!': 5, '?': 5},
                'emoji_patterns': {'emoji_frequency': 0, 'most_used_emojis': {}},
                'cta_patterns': [],
                'greeting_patterns': [],
                'closing_patterns': [],
                'content_themes': {},
                'writing_characteristics': {'formality_score': 70, 'readability_score': 75},
                'brand_voice_score': 65
            },
            'brand_profile': {
                'dominant_tone': 'professional',
                'writing_style': 'formal',
                'personality_traits': ['professional', 'helpful', 'knowledgeable']
            },
            'recommendations': ['Add more content to get better analysis'],
            'content_samples': [],
            'analysis_date': datetime.now().isoformat()
        }
    
    def _analyze_tone(self, texts: List[str]) -> Dict:
        """Analyze the overall tone of the writing"""
        tone_scores = {tone: 0 for tone in self.tone_keywords.keys()}
        total_words = 0
        
        for text in texts:
            words = text.lower().split()
            total_words += len(words)
            
            for tone, keywords in self.tone_keywords.items():
                for keyword in keywords:
                    # Count both exact matches and partial matches
                    tone_scores[tone] += text.lower().count(keyword)
                    # Also check for variations
                    if keyword.endswith('e'):
                        tone_scores[tone] += text.lower().count(keyword[:-1] + 'ing')
        
        # Normalize scores and convert to percentages
        if total_words > 0:
            total_tone_score = sum(tone_scores.values())
            if total_tone_score > 0:
                for tone in tone_scores:
                    tone_scores[tone] = (tone_scores[tone] / total_tone_score) * 100
            else:
                # Default distribution if no tone keywords found
                tone_scores = {'professional': 40, 'friendly': 30, 'educational': 20, 'motivational': 10}
        
        return tone_scores
    
    def _analyze_sentence_structure(self, texts: List[str]) -> Dict:
        """Analyze sentence structure patterns"""
        sentence_lengths = []
        question_count = 0
        exclamation_count = 0
        total_sentences = 0
        compound_sentences = 0
        
        for text in texts:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            for sentence in sentences:
                words = sentence.split()
                sentence_lengths.append(len(words))
                total_sentences += 1
                
                if '?' in sentence:
                    question_count += 1
                if '!' in sentence:
                    exclamation_count += 1
                if ' and ' in sentence or ' but ' in sentence or ' or ' in sentence:
                    compound_sentences += 1
        
        return {
            'avg_sentence_length': statistics.mean(sentence_lengths) if sentence_lengths else 15,
            'question_frequency': (question_count / total_sentences) * 100 if total_sentences > 0 else 0,
            'exclamation_frequency': (exclamation_count / total_sentences) * 100 if total_sentences > 0 else 0,
            'compound_sentence_frequency': (compound_sentences / total_sentences) * 100 if total_sentences > 0 else 0,
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
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        filtered_freq = {word: count for word, count in word_freq.items() 
                        if word not in stop_words and len(word) > 2}
        
        return {
            'most_common_words': dict(Counter(filtered_freq).most_common(20)),
            'vocabulary_size': len(set(all_words)),
            'avg_word_length': statistics.mean([len(word) for word in all_words]) if all_words else 5,
            'unique_word_ratio': len(set(all_words)) / len(all_words) if all_words else 0
        }
    
    def _analyze_punctuation(self, texts: List[str]) -> Dict:
        """Analyze punctuation usage patterns"""
        punctuation_counts = Counter()
        total_chars = 0
        
        for text in texts:
            total_chars += len(text)
            for char in text:
                if char in '.,!?;:()[]{}"-\'':
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
        emoji_positions = []
        
        for text in texts:
            emojis = emoji_pattern.findall(text)
            all_emojis.extend(emojis)
            
            # Analyze emoji positions
            text_length = len(text)
            for match in emoji_pattern.finditer(text):
                position = match.start() / text_length if text_length > 0 else 0
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
            'position_preferences': dict(position_freq),
            'emoji_diversity': len(set(all_emojis))
        }
    
    def _analyze_cta_patterns(self, texts: List[str]) -> List[str]:
        """Analyze call-to-action patterns"""
        cta_patterns = []
        
        cta_indicators = [
            r'contact me', r'call me', r'dm me', r'message me', r'text me',
            r'reach out', r'get in touch', r'let\'s talk', r'let\'s chat',
            r'schedule', r'book', r'visit', r'see more', r'click here',
            r'learn more', r'find out', r'discover', r'explore',
            r'sign up', r'register', r'subscribe', r'follow'
        ]
        
        for text in texts:
            text_lower = text.lower()
            for pattern in cta_indicators:
                if re.search(pattern, text_lower):
                    # Extract the sentence containing the CTA
                    sentences = re.split(r'[.!?]+', text)
                    for sentence in sentences:
                        if re.search(pattern, sentence.lower()):
                            cta_patterns.append(sentence.strip())
                            break
        
        return list(set(cta_patterns))[:10]  # Remove duplicates, limit to 10
    
    def _analyze_greeting_patterns(self, texts: List[str]) -> List[str]:
        """Analyze greeting and opening patterns"""
        greeting_patterns = []
        
        greeting_indicators = [
            r'^hey', r'^hi', r'^hello', r'^good morning', r'^good afternoon',
            r'^welcome', r'^greetings', r'^happy', r'^excited to'
        ]
        
        for text in texts:
            # Get first sentence
            first_sentence = re.split(r'[.!?]+', text)[0].strip()
            if len(first_sentence) < 150:  # Likely a greeting if reasonably short
                for pattern in greeting_indicators:
                    if re.search(pattern, first_sentence.lower()):
                        greeting_patterns.append(first_sentence)
                        break
        
        return list(set(greeting_patterns))[:10]
    
    def _analyze_closing_patterns(self, texts: List[str]) -> List[str]:
        """Analyze closing and ending patterns"""
        closing_patterns = []
        
        closing_indicators = [
            r'thank you', r'thanks', r'best regards', r'sincerely',
            r'talk soon', r'see you', r'have a great', r'cheers'
        ]
        
        for text in texts:
            # Get last sentence
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
            if sentences:
                last_sentence = sentences[-1]
                if len(last_sentence) < 150:  # Likely a closing if reasonably short
                    for pattern in closing_indicators:
                        if re.search(pattern, last_sentence.lower()):
                            closing_patterns.append(last_sentence)
                            break
        
        return list(set(closing_patterns))[:10]
    
    def _analyze_content_themes(self, texts: List[str]) -> Dict:
        """Analyze common content themes"""
        theme_counts = Counter()
        
        # Combine all industry phrases
        all_phrases = []
        for phrases in self.industry_phrases.values():
            all_phrases.extend(phrases)
        
        for text in texts:
            text_lower = text.lower()
            for phrase in all_phrases:
                if phrase in text_lower:
                    theme_counts[phrase] += 1
        
        return dict(theme_counts.most_common(15))
    
    def _analyze_writing_characteristics(self, texts: List[str]) -> Dict:
        """Analyze overall writing characteristics"""
        total_text = ' '.join(texts)
        
        # Calculate formality score
        formal_indicators = ['therefore', 'however', 'furthermore', 'moreover', 'consequently']
        informal_indicators = ['gonna', 'wanna', 'yeah', 'ok', 'awesome', 'cool']
        
        formal_count = sum(total_text.lower().count(word) for word in formal_indicators)
        informal_count = sum(total_text.lower().count(word) for word in informal_indicators)
        
        formality_score = 50  # Default neutral
        if formal_count + informal_count > 0:
            formality_score = (formal_count / (formal_count + informal_count)) * 100
        
        # Calculate readability score (simplified)
        words = total_text.split()
        sentences = re.split(r'[.!?]+', total_text)
        avg_words_per_sentence = len(words) / len(sentences) if sentences else 15
        avg_syllables_per_word = 1.5  # Simplified assumption
        
        # Flesch Reading Ease approximation
        readability_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        readability_score = max(0, min(100, readability_score))  # Clamp between 0-100
        
        return {
            'formality_score': formality_score,
            'readability_score': readability_score,
            'avg_words_per_sentence': avg_words_per_sentence,
            'total_word_count': len(words)
        }
    
    def _calculate_brand_voice_score(self, texts: List[str]) -> int:
        """Calculate overall brand voice consistency score"""
        if not texts:
            return 0
        
        # Factors that contribute to brand voice consistency
        factors = []
        
        # Tone consistency
        tone_analysis = self._analyze_tone(texts)
        dominant_tone_percentage = max(tone_analysis.values()) if tone_analysis else 0
        factors.append(min(dominant_tone_percentage, 100))
        
        # Vocabulary consistency
        vocab_analysis = self._analyze_vocabulary(texts)
        unique_ratio = vocab_analysis.get('unique_word_ratio', 0)
        factors.append((1 - unique_ratio) * 100)  # Lower uniqueness = more consistency
        
        # Structural consistency
        structure_analysis = self._analyze_sentence_structure(texts)
        variance = structure_analysis.get('sentence_length_variance', 0)
        consistency_score = max(0, 100 - (variance * 2))  # Lower variance = higher consistency
        factors.append(consistency_score)
        
        # Content theme consistency
        themes = self._analyze_content_themes(texts)
        theme_score = min(len(themes) * 10, 100) if themes else 50
        factors.append(theme_score)
        
        return int(statistics.mean(factors))
    
    def create_brand_voice_profile(self, analysis: Dict) -> Dict:
        """Create a comprehensive brand voice profile"""
        tone_analysis = analysis.get('tone_analysis', {})
        structure_analysis = analysis.get('sentence_structure', {})
        vocab_analysis = analysis.get('vocabulary_analysis', {})
        emoji_analysis = analysis.get('emoji_patterns', {})
        
        # Determine dominant characteristics
        dominant_tone = max(tone_analysis, key=tone_analysis.get) if tone_analysis else 'professional'
        
        # Determine writing style
        avg_length = structure_analysis.get('avg_sentence_length', 15)
        if avg_length < 10:
            writing_style = 'concise'
        elif avg_length > 20:
            writing_style = 'detailed'
        else:
            writing_style = 'balanced'
        
        # Determine personality traits
        personality_traits = []
        for tone, score in tone_analysis.items():
            if score > 20:  # Significant presence
                personality_traits.append(tone)
        
        if not personality_traits:
            personality_traits = ['professional']
        
        return {
            'dominant_tone': dominant_tone,
            'writing_style': writing_style,
            'personality_traits': personality_traits[:3],  # Top 3 traits
            'communication_preferences': {
                'uses_questions': structure_analysis.get('question_frequency', 0) > 10,
                'uses_exclamations': structure_analysis.get('exclamation_frequency', 0) > 5,
                'uses_emojis': emoji_analysis.get('emoji_frequency', 0) > 0.5,
                'prefers_short_sentences': avg_length < 12,
                'prefers_long_sentences': avg_length > 18
            },
            'vocabulary_level': 'professional' if vocab_analysis.get('avg_word_length', 5) > 5.5 else 'conversational',
            'brand_voice_strength': analysis.get('brand_voice_score', 65)
        }
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations for improving brand voice consistency"""
        recommendations = []
        
        tone_analysis = analysis.get('tone_analysis', {})
        structure_analysis = analysis.get('sentence_structure', {})
        brand_score = analysis.get('brand_voice_score', 65)
        
        # Tone recommendations
        if max(tone_analysis.values()) if tone_analysis else 0 < 40:
            recommendations.append("Consider developing a more consistent tone across your content")
        
        # Structure recommendations
        variance = structure_analysis.get('sentence_length_variance', 0)
        if variance > 10:
            recommendations.append("Try to maintain more consistent sentence lengths for better readability")
        
        # Engagement recommendations
        question_freq = structure_analysis.get('question_frequency', 0)
        if question_freq < 5:
            recommendations.append("Consider adding more questions to increase audience engagement")
        
        # Brand voice strength
        if brand_score < 70:
            recommendations.append("Focus on developing a more distinctive and consistent brand voice")
        
        # CTA recommendations
        cta_patterns = analysis.get('cta_patterns', [])
        if len(cta_patterns) < 2:
            recommendations.append("Include more clear calls-to-action in your content")
        
        if not recommendations:
            recommendations.append("Your brand voice is well-developed and consistent!")
        
        return recommendations
    
    def generate_content_with_voice(self, prompt: str, brand_profile: Dict, content_type: str = 'social_post') -> str:
        """Generate content that matches the analyzed brand voice"""
        
        # Extract key characteristics
        tone = brand_profile.get('dominant_tone', 'professional')
        style = brand_profile.get('writing_style', 'balanced')
        traits = brand_profile.get('personality_traits', ['professional'])
        prefs = brand_profile.get('communication_preferences', {})
        
        # Build content based on brand voice
        content_parts = []
        
        # Add greeting if appropriate
        if prefs.get('uses_questions') and content_type == 'social_post':
            greetings = {
                'friendly': "Hey there! 👋",
                'professional': "Good morning,",
                'conversational': "Hi everyone!",
                'motivational': "Ready for something amazing?"
            }
            content_parts.append(greetings.get(tone, "Hello!"))
        
        # Main content based on prompt and tone
        if tone == 'professional':
            main_content = f"As a professional in this field, I want to share some insights about {prompt}. "
        elif tone == 'friendly':
            main_content = f"I'm so excited to talk about {prompt}! "
        elif tone == 'educational':
            main_content = f"Let me share what you need to know about {prompt}. "
        elif tone == 'motivational':
            main_content = f"Here's how {prompt} can help you achieve your goals: "
        else:
            main_content = f"Let's discuss {prompt}. "
        
        content_parts.append(main_content)
        
        # Add style-specific elements
        if style == 'detailed':
            content_parts.append("Here are the key points to consider...")
        elif style == 'concise':
            content_parts.append("Bottom line:")
        
        # Add CTA based on preferences
        if content_type == 'social_post':
            if 'motivational' in traits:
                content_parts.append("What are your thoughts? Let's discuss in the comments!")
            elif 'professional' in traits:
                content_parts.append("Feel free to reach out if you have any questions.")
            else:
                content_parts.append("Would love to hear your experience!")
        
        # Add emojis if used frequently
        if prefs.get('uses_emojis'):
            content_parts[-1] += " ✨"
        
        return " ".join(content_parts)

