"""
Unit tests for linguistic service functions.
Tests quantitative linguistic analysis functions without external dependencies.
"""
import pytest
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.linguistic_service import (
    analyze_numerical_linguistic_metrics,
    HESITATION_MARKER_PATTERN,
    QUALIFIER_PATTERN,
    CERTAINTY_PATTERN
)


@pytest.mark.unit
def test_analyze_empty_transcript():
    """Test linguistic analysis with empty transcript."""
    result = analyze_numerical_linguistic_metrics("")
    assert isinstance(result, dict)
    assert result["word_count"] == 0
    assert result["hesitation_marker_count"] == 0


@pytest.mark.unit
def test_analyze_simple_transcript():
    """Test linguistic analysis with simple transcript."""
    transcript = "Hello world this is a test"
    result = analyze_numerical_linguistic_metrics(transcript)
    
    assert isinstance(result, dict)
    assert result["word_count"] == 6
    assert result["hesitation_marker_count"] == 0
    assert result["avg_word_length_chars"] > 0


@pytest.mark.unit
def test_hesitation_marker_detection():
    """Test detection of hesitation markers (um, uh, er, ah)."""
    transcript = "Um, well, uh, I think that er we should ah proceed"
    result = analyze_numerical_linguistic_metrics(transcript)
    
    # Should detect: um, uh, er, ah
    assert result["hesitation_marker_count"] == 4


@pytest.mark.unit
def test_filler_word_detection():
    """Test detection of filler words."""
    transcript = "Like, you know, well I actually think basically it's totally like really just fine"
    result = analyze_numerical_linguistic_metrics(transcript)
    
    # Should detect multiple filler words
    assert result["filler_word_count"] > 0


@pytest.mark.unit
def test_qualifier_detection():
    """Test detection of qualifier words."""
    transcript = "Maybe perhaps I might could possibly think about it"
    result = analyze_numerical_linguistic_metrics(transcript)
    
    # Should detect: maybe, perhaps, might, could, possibly
    assert result["qualifier_count"] >= 5


@pytest.mark.unit
def test_certainty_indicator_detection():
    """Test detection of certainty indicators."""
    transcript = "I definitely know certainly absolutely for sure it's true"
    result = analyze_numerical_linguistic_metrics(transcript)
    
    # Should detect: definitely, certainly, absolutely, sure
    assert result["certainty_indicator_count"] >= 4


@pytest.mark.unit
def test_repetition_detection():
    """Test detection of word repetitions."""
    transcript = "I said said that this this is important"
    result = analyze_numerical_linguistic_metrics(transcript)
    
    # Should detect immediate repetitions
    assert result["repetition_count"] >= 2


@pytest.mark.unit
def test_vocabulary_richness():
    """Test vocabulary richness (type-token ratio) calculation."""
    # High vocabulary richness - all unique words
    transcript_high = "The quick brown fox jumps over lazy dog"
    result_high = analyze_numerical_linguistic_metrics(transcript_high)
    
    # Low vocabulary richness - repeated words
    transcript_low = "the the the dog dog dog cat cat cat"
    result_low = analyze_numerical_linguistic_metrics(transcript_low)
    
    assert result_high["vocabulary_richness_ttr"] > result_low["vocabulary_richness_ttr"]


@pytest.mark.unit
def test_speech_rate_calculation():
    """Test speech rate calculation with duration."""
    transcript = "Hello world this is a test of speech rate"
    duration = 10.0  # 10 seconds
    
    result = analyze_numerical_linguistic_metrics(transcript, duration)
    
    # 9 words in 10 seconds = 54 wpm
    assert result["speech_rate_wpm"] is not None
    assert result["speech_rate_wpm"] > 0
    assert result["hesitation_rate_hpm"] is not None


@pytest.mark.unit
def test_speech_rate_without_duration():
    """Test that speech rate is None when duration not provided."""
    transcript = "Hello world this is a test"
    result = analyze_numerical_linguistic_metrics(transcript)
    
    assert result["speech_rate_wpm"] is None
    assert result["hesitation_rate_hpm"] is None


@pytest.mark.unit
def test_confidence_metric_ratio():
    """Test confidence metric ratio calculation."""
    # High certainty transcript
    transcript_certain = "I definitely know certainly absolutely it's true"
    result_certain = analyze_numerical_linguistic_metrics(transcript_certain)
    
    # High qualifier transcript
    transcript_uncertain = "Maybe perhaps possibly I might think probably"
    result_uncertain = analyze_numerical_linguistic_metrics(transcript_uncertain)
    
    assert result_certain["confidence_metric_ratio"] is not None
    assert result_uncertain["confidence_metric_ratio"] is not None
    assert result_certain["confidence_metric_ratio"] > result_uncertain["confidence_metric_ratio"]


@pytest.mark.unit
def test_formality_score():
    """Test formality score calculation."""
    # Formal transcript
    transcript_formal = "Furthermore, I would like to respectfully submit this proposal pursuant to regulations"
    result_formal = analyze_numerical_linguistic_metrics(transcript_formal)
    
    # Informal transcript
    transcript_informal = "Yeah, gonna wanna totally like dude it's cool whatever"
    result_informal = analyze_numerical_linguistic_metrics(transcript_informal)
    
    assert result_formal["formality_score_calculated"] > result_informal["formality_score_calculated"]


@pytest.mark.unit
def test_average_sentence_length():
    """Test average sentence length calculation."""
    transcript = "This is sentence one. This is sentence two. This is sentence three."
    result = analyze_numerical_linguistic_metrics(transcript)
    
    assert result["avg_sentence_length_words"] > 0
    # 3 sentences with roughly 4 words each
    assert result["avg_sentence_length_words"] >= 3


@pytest.mark.unit
def test_average_word_length():
    """Test average word length calculation."""
    # Long words
    transcript_long = "extraordinary comprehensive fundamental significantly"
    result_long = analyze_numerical_linguistic_metrics(transcript_long)
    
    # Short words
    transcript_short = "I am at my car on the way"
    result_short = analyze_numerical_linguistic_metrics(transcript_short)
    
    assert result_long["avg_word_length_chars"] > result_short["avg_word_length_chars"]


@pytest.mark.unit
def test_transcript_with_punctuation():
    """Test analysis with punctuation in transcript."""
    transcript = "Hello, world! How are you? I'm fine, thanks."
    result = analyze_numerical_linguistic_metrics(transcript)
    
    # Should handle punctuation correctly
    assert result["word_count"] > 0
    assert isinstance(result["avg_word_length_chars"], (int, float))


@pytest.mark.unit
def test_case_insensitivity():
    """Test that pattern matching is case-insensitive."""
    transcript_lower = "um, i definitely think maybe"
    transcript_upper = "UM, I DEFINITELY THINK MAYBE"
    transcript_mixed = "Um, I Definitely Think Maybe"
    
    result_lower = analyze_numerical_linguistic_metrics(transcript_lower)
    result_upper = analyze_numerical_linguistic_metrics(transcript_upper)
    result_mixed = analyze_numerical_linguistic_metrics(transcript_mixed)
    
    # All should detect the same patterns
    assert result_lower["hesitation_marker_count"] == result_upper["hesitation_marker_count"]
    assert result_lower["certainty_indicator_count"] == result_upper["certainty_indicator_count"]
    assert result_lower["qualifier_count"] == result_upper["qualifier_count"]


@pytest.mark.unit
def test_unique_word_count():
    """Test unique word count calculation."""
    transcript = "the cat and the dog and the bird"
    result = analyze_numerical_linguistic_metrics(transcript)
    
    # Words: the (3x), cat, and (2x), dog, bird = 5 unique words
    assert result["unique_word_count"] == 5


@pytest.mark.unit
def test_zero_duration_handling():
    """Test that zero duration doesn't cause division errors."""
    transcript = "Hello world"
    result = analyze_numerical_linguistic_metrics(transcript, duration=0)
    
    # Should handle zero duration gracefully
    assert result["speech_rate_wpm"] is None or result["speech_rate_wpm"] >= 0


@pytest.mark.unit
def test_whitespace_only_transcript():
    """Test analysis with whitespace-only transcript."""
    transcript = "   \n\t  "
    result = analyze_numerical_linguistic_metrics(transcript)
    
    assert result["word_count"] == 0
    assert result["hesitation_marker_count"] == 0


@pytest.mark.unit
def test_single_word_transcript():
    """Test analysis with single word."""
    transcript = "Hello"
    result = analyze_numerical_linguistic_metrics(transcript)
    
    assert result["word_count"] == 1
    assert result["avg_word_length_chars"] == 5
    assert result["vocabulary_richness_ttr"] == 1.0
