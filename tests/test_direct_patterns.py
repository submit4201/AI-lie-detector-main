"""
Pytest unit tests for enhanced linguistic pattern detection.
Tests pattern detection in various speech styles without external dependencies.
"""
import sys
from pathlib import Path
import pytest

# Ensure backend is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.linguistic_service import analyze_linguistic_patterns


@pytest.mark.unit
def test_repetition_pattern_detection():
    """Test detection of repetitive phrases in speech."""
    text = "Well, I was right out here, right out here on the mountain. The whole thing, the whole thing was confusing."
    duration = 15.0
    
    result = analyze_linguistic_patterns(text, duration)
    
    assert isinstance(result, dict)
    assert result.get('word_count', 0) > 0
    assert result.get('repetition_count', 0) > 0, "Should detect repeated phrases 'right out here' and 'the whole thing'"
    assert result.get('hesitation_count', 0) >= 1, "Should detect 'Well' as hesitation marker"


@pytest.mark.unit
def test_hesitation_marker_detection():
    """Test detection of hesitation markers like 'um', 'well', 'you know'."""
    text = "Um, well, you know, I think maybe, like, it was around 8 PM or so, you understand?"
    duration = 12.0
    
    result = analyze_linguistic_patterns(text, duration)
    
    assert isinstance(result, dict)
    assert result.get('hesitation_count', 0) >= 5, "Should detect multiple hesitation markers"
    assert result.get('qualifier_count', 0) >= 2, "Should detect qualifier words like 'maybe', 'like'"
    assert result.get('word_count', 0) > 0


@pytest.mark.unit
def test_certainty_expression_detection():
    """Test detection of certainty expressions in confident speech."""
    text = "I absolutely know for certain that I definitely saw him there. Without doubt, I'm 100 percent sure."
    duration = 10.0
    
    result = analyze_linguistic_patterns(text, duration)
    
    assert isinstance(result, dict)
    assert result.get('certainty_count', 0) >= 5, "Should detect certainty words: absolutely, certain, definitely, without doubt, sure"
    assert result.get('confidence_ratio') is not None
    assert result.get('word_count', 0) > 0


@pytest.mark.unit
def test_formality_score_calculation():
    """Test formality scoring for formal speech patterns."""
    text = "Thank you kindly sir, I respectfully submit that furthermore, this matter requires careful consideration."
    duration = 8.0
    
    result = analyze_linguistic_patterns(text, duration)
    
    assert isinstance(result, dict)
    assert result.get('formality_score') is not None
    assert result.get('formality_score', 0) > 0, "Formal language should have positive formality score"
    assert result.get('complexity_score') is not None
    assert result.get('word_count', 0) > 0


@pytest.mark.unit
def test_original_recording_pattern():
    """Test pattern detection on realistic speech sample."""
    text = "that's pretty impressive Ben's mom used to live inside of a mountain right out here right out here on this mountain in Oakville"
    duration = 37.33
    
    result = analyze_linguistic_patterns(text, duration)
    
    assert isinstance(result, dict)
    assert result.get('word_count', 0) > 15
    assert result.get('repetition_count', 0) > 0, "Should detect 'right out here' repetition"
    assert result.get('speech_rate_wpm') is not None
    # Speech rate calculation: word_count / (duration / 60)
    expected_rate = result['word_count'] / (duration / 60)
    assert abs(result.get('speech_rate_wpm', 0) - expected_rate) < 1, "Speech rate should be calculated correctly"


@pytest.mark.unit
def test_all_metrics_present():
    """Test that all expected metrics are returned in results."""
    text = "I think maybe I saw something."
    duration = 5.0
    
    result = analyze_linguistic_patterns(text, duration)
    
    expected_keys = [
        'word_count',
        'hesitation_count',
        'qualifier_count',
        'certainty_count',
        'filler_count',
        'repetition_count',
        'formality_score',
        'complexity_score',
    ]
    
    for key in expected_keys:
        assert key in result, f"Missing expected key: {key}"


@pytest.mark.unit
def test_empty_text_handling():
    """Test handling of empty or very short text."""
    text = ""
    duration = 1.0
    
    result = analyze_linguistic_patterns(text, duration)
    
    assert isinstance(result, dict)
    assert result.get('word_count', 0) == 0
    # Other metrics should still be present with appropriate defaults
    assert 'hesitation_count' in result
    assert 'formality_score' in result

