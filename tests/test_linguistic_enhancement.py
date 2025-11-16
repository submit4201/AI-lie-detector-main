"""
Unit tests for LinguisticEnhancementService
"""

import pytest
from backend.services.linguistic_enhancement_service import LinguisticEnhancementService
from backend.models import LinguisticEnhancementMetrics


@pytest.fixture
def ling_service():
    """Create a linguistic enhancement service instance."""
    return LinguisticEnhancementService()


class TestLinguisticEnhancementService:
    """Test suite for LinguisticEnhancementService."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = LinguisticEnhancementService()
        assert service is not None
    
    def test_pronoun_ratios_first_person(self, ling_service):
        """Test first-person pronoun detection."""
        text = "I think that my opinion is important to me and myself."
        result = ling_service.calculate_pronoun_ratios(text)
        
        assert result["first_person_count"] == 4  # I, my, me, myself
        assert result["first_person_ratio"] > 0
    
    def test_pronoun_ratios_mixed(self, ling_service):
        """Test mixed pronoun detection."""
        text = "I told you that he should do his work."
        result = ling_service.calculate_pronoun_ratios(text)
        
        assert result["first_person_count"] == 1  # I
        assert result["second_person_ratio"] > 0  # you
        assert result["third_person_ratio"] > 0  # he, his
    
    def test_pronoun_ratios_empty(self, ling_service):
        """Test empty text handling."""
        text = ""
        result = ling_service.calculate_pronoun_ratios(text)
        
        assert result["first_person_count"] == 0
        assert result["first_person_ratio"] == 0.0
    
    def test_article_usage(self, ling_service):
        """Test article usage detection."""
        text = "The cat sat on a mat with an apple."
        result = ling_service.calculate_article_usage(text)
        
        assert result["article_count"] == 3  # the, a, an
        assert result["article_ratio"] > 0
        assert 0 < result["definite_ratio"] < 1  # 1 definite (the) out of 3 total
    
    def test_article_usage_no_articles(self, ling_service):
        """Test text without articles."""
        text = "Dogs run fast every day."
        result = ling_service.calculate_article_usage(text)
        
        assert result["article_count"] == 0
        assert result["article_ratio"] == 0.0
        assert result["definite_ratio"] == 0.0
    
    def test_sentence_complexity_simple(self, ling_service):
        """Test simple sentence complexity."""
        text = "The cat sat. The dog ran. The bird flew."
        result = ling_service.calculate_sentence_complexity(text)
        
        assert result["complexity_score"] > 0
        assert result["avg_clauses_per_sentence"] >= 1.0
        assert result["subordinate_clause_ratio"] == 0  # No subordinate clauses
    
    def test_sentence_complexity_complex(self, ling_service):
        """Test complex sentence complexity."""
        text = "Although the cat sat, the dog ran because it was scared when the bird flew."
        result = ling_service.calculate_sentence_complexity(text)
        
        assert result["complexity_score"] > 0
        assert result["subordinate_clause_ratio"] > 0  # Has although, because, when
    
    def test_emotional_leakage_detection(self, ling_service):
        """Test emotional leakage word detection."""
        text = "Honestly, I really think that maybe you should definitely consider this."
        result = ling_service.detect_emotional_leakage(text)
        
        assert result["leakage_count"] > 0
        assert len(result["leakage_words"]) > 0
        assert "honestly" in result["leakage_words"]
        assert "really" in result["leakage_words"]
        assert "maybe" in result["leakage_words"]
        assert "definitely" in result["leakage_words"]
    
    def test_emotional_leakage_none(self, ling_service):
        """Test text without emotional leakage."""
        text = "The weather is sunny today."
        result = ling_service.detect_emotional_leakage(text)
        
        assert result["leakage_count"] == 0
        assert len(result["leakage_words"]) == 0
    
    def test_prosodic_congruence_without_context(self, ling_service):
        """Test prosodic congruence without external context."""
        text = "I am very happy and excited about this wonderful opportunity."
        result = ling_service.calculate_prosodic_congruence(text)
        
        assert "congruence_score" in result
        assert "text_sentiment" in result
        assert result["text_sentiment"] == "positive"
    
    def test_prosodic_congruence_with_mismatch(self, ling_service):
        """Test prosodic congruence with acoustic-linguistic mismatch."""
        text = "I am very happy about this."
        acoustic_emotions = ["anger", "frustration"]
        linguistic_sentiment = "positive"
        
        result = ling_service.calculate_prosodic_congruence(
            text, acoustic_emotions, linguistic_sentiment
        )
        
        assert result["congruence_score"] < 0.7  # Should detect mismatch
        assert len(result["mismatches"]) > 0
    
    def test_prosodic_congruence_congruent(self, ling_service):
        """Test prosodic congruence with matching signals."""
        text = "I am very happy about this."
        acoustic_emotions = ["joy", "happiness"]
        linguistic_sentiment = "positive"
        
        result = ling_service.calculate_prosodic_congruence(
            text, acoustic_emotions, linguistic_sentiment
        )
        
        assert result["congruence_score"] > 0.5  # Should detect congruence
    
    def test_full_extraction(self, ling_service):
        """Test full linguistic metrics extraction."""
        text = "I really think that my opinion matters. You should definitely consider what I'm saying."
        
        metrics = ling_service.extract_linguistic_metrics(text)
        
        assert isinstance(metrics, LinguisticEnhancementMetrics)
        assert metrics.pronoun_ratio_first_person > 0
        assert metrics.article_usage_ratio >= 0
        assert metrics.sentence_complexity_score >= 0
        assert metrics.emotional_leakage_count > 0  # "really", "definitely"
    
    def test_full_extraction_with_context(self, ling_service):
        """Test full extraction with acoustic context."""
        text = "I am happy about the results."
        acoustic_emotions = ["joy"]
        linguistic_sentiment = "positive"
        
        metrics = ling_service.extract_linguistic_metrics(
            text, acoustic_emotions, linguistic_sentiment
        )
        
        assert isinstance(metrics, LinguisticEnhancementMetrics)
        assert metrics.prosodic_congruence_score is not None
        assert metrics.prosodic_congruence_score > 0.5
    
    def test_response_latency_calculation(self, ling_service):
        """Test response latency calculation."""
        text = "This is a test."
        response_latencies = [0.5, 1.0, 0.8, 1.2]
        
        metrics = ling_service.extract_linguistic_metrics(
            text, response_latencies=response_latencies
        )
        
        assert metrics.response_latency_mean is not None
        assert metrics.response_latency_std is not None
        assert metrics.response_latency_mean > 0
    
    def test_case_insensitivity(self, ling_service):
        """Test that detection is case-insensitive."""
        text_lower = "i think my opinion matters"
        text_upper = "I THINK MY OPINION MATTERS"
        
        result_lower = ling_service.calculate_pronoun_ratios(text_lower)
        result_upper = ling_service.calculate_pronoun_ratios(text_upper)
        
        assert result_lower["first_person_count"] == result_upper["first_person_count"]
    
    def test_multi_word_phrases(self, ling_service):
        """Test detection of multi-word emotional leakage phrases."""
        text = "To be honest, I believe me when I say this is true."
        result = ling_service.detect_emotional_leakage(text)
        
        assert "to be honest" in result["leakage_words"]
        assert "believe me" in result["leakage_words"]
    
    def test_subordinate_clause_detection(self, ling_service):
        """Test subordinate clause marker detection."""
        text = "I went home because I was tired although I wanted to stay."
        result = ling_service.calculate_sentence_complexity(text)
        
        # Should detect "because" and "although"
        assert result["subordinate_clause_ratio"] > 0
    
    def test_empty_text_handling(self, ling_service):
        """Test handling of empty text."""
        metrics = ling_service.extract_linguistic_metrics("")
        
        assert isinstance(metrics, LinguisticEnhancementMetrics)
        assert metrics.pronoun_ratio_first_person == 0.0
        assert metrics.article_usage_ratio == 0.0
        assert metrics.sentence_complexity_score == 0.0
    
    def test_special_characters(self, ling_service):
        """Test handling of text with special characters."""
        text = "I think... maybe??? You know!!! It's great!!!"
        result = ling_service.calculate_pronoun_ratios(text)
        
        # Should still detect pronouns despite punctuation
        assert result["first_person_count"] > 0
        assert result["second_person_ratio"] > 0


@pytest.mark.unit
class TestLinguisticEnhancement:
    """Additional unit tests for linguistic enhancement."""
    
    def test_tokenization(self):
        """Test internal tokenization."""
        service = LinguisticEnhancementService()
        tokens = service._tokenize("Hello, world! How are you?")
        
        assert "hello" in tokens
        assert "world" in tokens
        assert "how" in tokens
        # Punctuation should be excluded
        assert "," not in tokens
        assert "!" not in tokens
    
    def test_sentence_splitting(self):
        """Test internal sentence splitting."""
        service = LinguisticEnhancementService()
        text = "First sentence. Second sentence! Third sentence?"
        sentences = service._split_sentences(text)
        
        assert len(sentences) == 3
        assert "First sentence" in sentences[0]
        assert "Second sentence" in sentences[1]
        assert "Third sentence" in sentences[2]
    
    def test_emotion_valence_detection(self):
        """Test emotion valence detection."""
        service = LinguisticEnhancementService()
        
        # Positive emotions
        positive_valence = service._get_emotion_valence(["joy", "happiness"])
        assert positive_valence == "positive"
        
        # Negative emotions
        negative_valence = service._get_emotion_valence(["anger", "sad"])
        assert negative_valence == "negative"
        
        # Neutral/mixed
        neutral_valence = service._get_emotion_valence(["neutral"])
        assert neutral_valence == "neutral"
    
    def test_sentiment_to_valence_conversion(self):
        """Test sentiment label to valence conversion."""
        service = LinguisticEnhancementService()
        
        assert service._sentiment_to_valence("positive") == "positive"
        assert service._sentiment_to_valence("negative") == "negative"
        assert service._sentiment_to_valence("neutral") == "neutral"
        assert service._sentiment_to_valence("Positive sentiment") == "positive"
    
    def test_complexity_score_bounds(self):
        """Test that complexity scores stay within bounds."""
        service = LinguisticEnhancementService()
        
        # Very simple sentence
        simple = "Cat ran."
        result_simple = service.calculate_sentence_complexity(simple)
        assert 0.0 <= result_simple["complexity_score"] <= 1.0
        
        # Very complex sentence
        complex_text = ("Although the cat, which was very large and had been sitting "
                       "on the mat that was placed near the door because it was "
                       "comfortable, decided to run when the dog arrived, "
                       "it still managed to escape since it was very fast.")
        result_complex = service.calculate_sentence_complexity(complex_text)
        assert 0.0 <= result_complex["complexity_score"] <= 1.0
        assert result_complex["complexity_score"] > result_simple["complexity_score"]
