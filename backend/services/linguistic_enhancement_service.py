"""
Linguistic Enhancement Service
Extracts advanced linguistic features including pronoun ratios, article usage,
sentence complexity, emotional leakage, and prosodic congruence.
"""

import re
from typing import List, Dict, Optional, Set
from backend.models import LinguisticEnhancementMetrics


class LinguisticEnhancementService:
    """
    Service for extracting enhanced linguistic features from text.
    """
    
    # Pronoun categories
    FIRST_PERSON_PRONOUNS = {
        "i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"
    }
    SECOND_PERSON_PRONOUNS = {
        "you", "your", "yours", "yourself", "yourselves"
    }
    THIRD_PERSON_PRONOUNS = {
        "he", "him", "his", "himself", "she", "her", "hers", "herself",
        "they", "them", "their", "theirs", "themselves", "it", "its", "itself"
    }
    
    # Articles
    DEFINITE_ARTICLES = {"the"}
    INDEFINITE_ARTICLES = {"a", "an"}
    ALL_ARTICLES = DEFINITE_ARTICLES | INDEFINITE_ARTICLES
    
    # Emotional leakage words (indicating stress or deception)
    EMOTIONAL_LEAKAGE_WORDS = {
        # Stress indicators
        "honestly", "frankly", "truthfully", "literally", "actually", "really",
        "believe me", "trust me", "to be honest", "to tell the truth",
        # Hedging/uncertainty
        "maybe", "perhaps", "possibly", "probably", "might", "could",
        "sort of", "kind of", "somewhat", "rather",
        # Intensifiers (overcompensation)
        "absolutely", "definitely", "certainly", "surely", "clearly",
        "obviously", "totally", "completely", "entirely",
        # Evasive
        "basically", "essentially", "generally", "typically", "normally"
    }
    
    # Subordinate clause markers
    SUBORDINATE_MARKERS = {
        "because", "since", "although", "though", "while", "when", "if",
        "unless", "until", "before", "after", "as", "that", "which", "who"
    }
    
    def __init__(self):
        """Initialize the linguistic enhancement service."""
        pass
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of lowercase tokens
        """
        # Simple word tokenization
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def calculate_pronoun_ratios(self, text: str) -> Dict[str, float]:
        """
        Calculate pronoun usage ratios.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with pronoun ratios and counts
        """
        tokens = self._tokenize(text)
        total_words = len(tokens)
        
        if total_words == 0:
            return {
                "first_person_count": 0,
                "first_person_ratio": 0.0,
                "second_person_ratio": 0.0,
                "third_person_ratio": 0.0
            }
        
        first_person_count = sum(1 for t in tokens if t in self.FIRST_PERSON_PRONOUNS)
        second_person_count = sum(1 for t in tokens if t in self.SECOND_PERSON_PRONOUNS)
        third_person_count = sum(1 for t in tokens if t in self.THIRD_PERSON_PRONOUNS)
        
        return {
            "first_person_count": first_person_count,
            "first_person_ratio": first_person_count / total_words,
            "second_person_ratio": second_person_count / total_words,
            "third_person_ratio": third_person_count / total_words
        }
    
    def calculate_article_usage(self, text: str) -> Dict[str, float]:
        """
        Calculate article usage patterns.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with article usage metrics
        """
        tokens = self._tokenize(text)
        total_words = len(tokens)
        
        if total_words == 0:
            return {
                "article_count": 0,
                "article_ratio": 0.0,
                "definite_ratio": 0.0
            }
        
        article_count = sum(1 for t in tokens if t in self.ALL_ARTICLES)
        definite_count = sum(1 for t in tokens if t in self.DEFINITE_ARTICLES)
        
        definite_ratio = definite_count / article_count if article_count > 0 else 0.0
        
        return {
            "article_count": article_count,
            "article_ratio": article_count / total_words,
            "definite_ratio": definite_ratio
        }
    
    def calculate_sentence_complexity(self, text: str) -> Dict[str, float]:
        """
        Calculate sentence complexity metrics.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with complexity metrics
        """
        sentences = self._split_sentences(text)
        
        if not sentences:
            return {
                "complexity_score": 0.0,
                "avg_clauses_per_sentence": 0.0,
                "subordinate_clause_ratio": 0.0
            }
        
        total_words = len(self._tokenize(text))
        avg_words_per_sentence = total_words / len(sentences)
        
        # Count subordinate clauses
        subordinate_count = 0
        for sentence in sentences:
            tokens = self._tokenize(sentence)
            subordinate_count += sum(1 for t in tokens if t in self.SUBORDINATE_MARKERS)
        
        subordinate_ratio = subordinate_count / len(sentences)
        
        # Complexity score (normalized combination of metrics)
        # Longer sentences + more subordination = higher complexity
        complexity_score = min(1.0, (avg_words_per_sentence / 30.0) * 0.5 + 
                                    (subordinate_ratio / 2.0) * 0.5)
        
        return {
            "complexity_score": complexity_score,
            "avg_clauses_per_sentence": 1.0 + subordinate_ratio,
            "subordinate_clause_ratio": subordinate_ratio
        }
    
    def detect_emotional_leakage(self, text: str) -> Dict[str, any]:
        """
        Detect emotional leakage words and patterns.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with emotional leakage metrics
        """
        text_lower = text.lower()
        tokens = self._tokenize(text)
        total_words = len(tokens)
        
        # Find emotional leakage words
        detected_words = []
        for word in self.EMOTIONAL_LEAKAGE_WORDS:
            if ' ' in word:
                # Multi-word phrase
                if word in text_lower:
                    detected_words.append(word)
            else:
                # Single word
                if word in tokens:
                    detected_words.append(word)
        
        leakage_count = len(detected_words)
        leakage_ratio = leakage_count / total_words if total_words > 0 else 0.0
        
        return {
            "leakage_words": detected_words,
            "leakage_count": leakage_count,
            "leakage_ratio": leakage_ratio
        }
    
    def calculate_prosodic_congruence(
        self,
        text: str,
        acoustic_emotions: Optional[List[str]] = None,
        linguistic_sentiment: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Calculate prosodic congruence (match between acoustic and linguistic signals).
        
        Args:
            text: Input text
            acoustic_emotions: Emotions detected from acoustic analysis
            linguistic_sentiment: Sentiment detected from text
            
        Returns:
            Dictionary with prosodic congruence metrics
        """
        # Simple sentiment detection from text
        positive_words = {
            "good", "great", "excellent", "wonderful", "happy", "joy",
            "pleased", "satisfied", "love", "like", "enjoy"
        }
        negative_words = {
            "bad", "terrible", "awful", "sad", "angry", "hate", "dislike",
            "upset", "frustrated", "disappointed", "worried", "concerned"
        }
        
        tokens = self._tokenize(text)
        
        positive_count = sum(1 for t in tokens if t in positive_words)
        negative_count = sum(1 for t in tokens if t in negative_words)
        
        # Determine text sentiment
        if positive_count > negative_count:
            text_sentiment = "positive"
        elif negative_count > positive_count:
            text_sentiment = "negative"
        else:
            text_sentiment = "neutral"
        
        # Compare with provided linguistic sentiment
        congruence_score = None
        mismatches = []
        
        if acoustic_emotions and linguistic_sentiment:
            # Check for mismatches between acoustic and linguistic signals
            acoustic_valence = self._get_emotion_valence(acoustic_emotions)
            linguistic_valence = self._sentiment_to_valence(linguistic_sentiment)
            
            if acoustic_valence != linguistic_valence and acoustic_valence != "neutral" and linguistic_valence != "neutral":
                mismatches.append(f"Acoustic ({acoustic_valence}) vs Linguistic ({linguistic_valence})")
                congruence_score = 0.3
            else:
                congruence_score = 0.8
        
        # Compare acoustic with text sentiment if available
        if acoustic_emotions:
            acoustic_valence = self._get_emotion_valence(acoustic_emotions)
            if acoustic_valence != text_sentiment and acoustic_valence != "neutral" and text_sentiment != "neutral":
                mismatches.append(f"Acoustic emotion ({acoustic_valence}) vs Text sentiment ({text_sentiment})")
                if congruence_score is None:
                    congruence_score = 0.4
                else:
                    congruence_score = (congruence_score + 0.4) / 2
        
        if congruence_score is None:
            congruence_score = 0.7  # Default moderate congruence if not enough data
        
        return {
            "congruence_score": congruence_score,
            "mismatches": mismatches,
            "text_sentiment": text_sentiment
        }
    
    def _get_emotion_valence(self, emotions: List[str]) -> str:
        """
        Get overall valence from emotion list.
        
        Args:
            emotions: List of emotion labels
            
        Returns:
            Valence: "positive", "negative", or "neutral"
        """
        positive_emotions = {"joy", "happiness", "excited", "pleased", "satisfied"}
        negative_emotions = {"anger", "sad", "fear", "disgust", "frustrated", "worried"}
        
        emotions_lower = [e.lower() for e in emotions]
        
        positive_count = sum(1 for e in emotions_lower if e in positive_emotions)
        negative_count = sum(1 for e in emotions_lower if e in negative_emotions)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _sentiment_to_valence(self, sentiment: str) -> str:
        """
        Convert sentiment label to valence.
        
        Args:
            sentiment: Sentiment label
            
        Returns:
            Valence: "positive", "negative", or "neutral"
        """
        sentiment_lower = sentiment.lower()
        if "positive" in sentiment_lower:
            return "positive"
        elif "negative" in sentiment_lower:
            return "negative"
        else:
            return "neutral"
    
    def extract_linguistic_metrics(
        self,
        text: str,
        acoustic_emotions: Optional[List[str]] = None,
        linguistic_sentiment: Optional[str] = None,
        response_latencies: Optional[List[float]] = None
    ) -> LinguisticEnhancementMetrics:
        """
        Extract comprehensive linguistic enhancement metrics.
        
        Args:
            text: Input text
            acoustic_emotions: Optional emotions from acoustic analysis
            linguistic_sentiment: Optional sentiment from linguistic analysis
            response_latencies: Optional list of response latencies
            
        Returns:
            LinguisticEnhancementMetrics with comprehensive features
        """
        # Pronoun analysis
        pronoun_data = self.calculate_pronoun_ratios(text)
        
        # Article usage
        article_data = self.calculate_article_usage(text)
        
        # Sentence complexity
        complexity_data = self.calculate_sentence_complexity(text)
        
        # Emotional leakage
        leakage_data = self.detect_emotional_leakage(text)
        
        # Prosodic congruence
        congruence_data = self.calculate_prosodic_congruence(
            text, acoustic_emotions, linguistic_sentiment
        )
        
        # Response latency statistics
        response_latency_mean = None
        response_latency_std = None
        if response_latencies:
            import numpy as np
            response_latency_mean = float(np.mean(response_latencies))
            response_latency_std = float(np.std(response_latencies))
        
        return LinguisticEnhancementMetrics(
            # Pronoun analysis
            pronoun_ratio_first_person=pronoun_data["first_person_ratio"],
            pronoun_count_first_person=pronoun_data["first_person_count"],
            pronoun_ratio_second_person=pronoun_data["second_person_ratio"],
            pronoun_ratio_third_person=pronoun_data["third_person_ratio"],
            
            # Article usage
            article_usage_ratio=article_data["article_ratio"],
            article_count=article_data["article_count"],
            definite_article_ratio=article_data["definite_ratio"],
            
            # Sentence complexity
            sentence_complexity_score=complexity_data["complexity_score"],
            avg_clause_per_sentence=complexity_data["avg_clauses_per_sentence"],
            subordinate_clause_ratio=complexity_data["subordinate_clause_ratio"],
            
            # Emotional leakage
            emotional_leakage_words=leakage_data["leakage_words"],
            emotional_leakage_count=leakage_data["leakage_count"],
            emotional_leakage_ratio=leakage_data["leakage_ratio"],
            
            # Response latency
            response_latency_mean=response_latency_mean,
            response_latency_std=response_latency_std,
            
            # Prosodic congruence
            prosodic_congruence_score=congruence_data["congruence_score"],
            prosodic_mismatches=congruence_data["mismatches"]
        )
