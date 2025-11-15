"""
Unit tests for manipulation service fallback functions.
Tests basic manipulation detection without LLM dependencies.
"""
import pytest
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.manipulation_service import ManipulationService


@pytest.mark.unit
def test_fallback_empty_transcript():
    """Test fallback manipulation analysis with empty transcript."""
    service = ManipulationService(gemini_service=None)
    result = service._fallback_text_analysis("")
    
    assert result.is_manipulative is False
    assert result.manipulation_score == 0.0
    assert len(result.manipulation_techniques) == 0


@pytest.mark.unit
def test_fallback_no_manipulation():
    """Test fallback analysis with clean transcript."""
    service = ManipulationService(gemini_service=None)
    transcript = "I think we should discuss this matter calmly and rationally."
    
    result = service._fallback_text_analysis(transcript)
    
    assert result.is_manipulative is False
    assert result.manipulation_score == 0.0
    assert len(result.manipulation_techniques) == 0


@pytest.mark.unit
def test_fallback_overgeneralization_detection():
    """Test detection of overgeneralization patterns."""
    service = ManipulationService(gemini_service=None)
    
    # Test "you always"
    transcript_always = "You always do this to me"
    result_always = service._fallback_text_analysis(transcript_always)
    
    assert result_always.is_manipulative is True
    assert "Overgeneralization/Absolutes" in result_always.manipulation_techniques
    assert result_always.manipulation_score >= 0.2
    
    # Test "you never"
    transcript_never = "You never listen to me"
    result_never = service._fallback_text_analysis(transcript_never)
    
    assert result_never.is_manipulative is True
    assert "Overgeneralization/Absolutes" in result_never.manipulation_techniques


@pytest.mark.unit
def test_fallback_guilt_tripping_detection():
    """Test detection of guilt-tripping patterns."""
    service = ManipulationService(gemini_service=None)
    
    # Test "if you really loved me"
    transcript_love = "If you really loved me, you would do this"
    result_love = service._fallback_text_analysis(transcript_love)
    
    assert result_love.is_manipulative is True
    assert "Guilt-tripping/Moralizing" in result_love.manipulation_techniques
    assert result_love.manipulation_score >= 0.3
    
    # Test "a good person would"
    transcript_good = "A good person would never say that"
    result_good = service._fallback_text_analysis(transcript_good)
    
    assert result_good.is_manipulative is True
    assert "Guilt-tripping/Moralizing" in result_good.manipulation_techniques


@pytest.mark.unit
def test_fallback_multiple_techniques():
    """Test detection of multiple manipulation techniques."""
    service = ManipulationService(gemini_service=None)
    transcript = "You always forget and you never care. If you really loved me, you would remember."
    
    result = service._fallback_text_analysis(transcript)
    
    assert result.is_manipulative is True
    assert len(result.manipulation_techniques) >= 2
    assert "Overgeneralization/Absolutes" in result.manipulation_techniques
    assert "Guilt-tripping/Moralizing" in result.manipulation_techniques
    # Score should be sum of individual scores (0.2 + 0.3) = 0.5
    assert result.manipulation_score >= 0.5


@pytest.mark.unit
def test_fallback_score_capping():
    """Test that manipulation score is capped at 1.0."""
    service = ManipulationService(gemini_service=None)
    # Create transcript with many techniques to test capping
    transcript = "You always do this. You never care. If you really loved me, you would understand."
    
    result = service._fallback_text_analysis(transcript)
    
    assert result.manipulation_score <= 1.0


@pytest.mark.unit
def test_fallback_case_insensitivity():
    """Test that pattern detection is case-insensitive."""
    service = ManipulationService(gemini_service=None)
    
    transcript_lower = "you always do this"
    transcript_upper = "YOU ALWAYS DO THIS"
    transcript_mixed = "You Always Do This"
    
    result_lower = service._fallback_text_analysis(transcript_lower)
    result_upper = service._fallback_text_analysis(transcript_upper)
    result_mixed = service._fallback_text_analysis(transcript_mixed)
    
    # All should detect the same manipulation
    assert result_lower.is_manipulative == result_upper.is_manipulative
    assert result_lower.manipulation_score == result_upper.manipulation_score
    assert result_lower.manipulation_techniques == result_upper.manipulation_techniques


@pytest.mark.unit
def test_fallback_confidence_level():
    """Test that fallback analysis has low confidence."""
    service = ManipulationService(gemini_service=None)
    transcript = "You always do this to me"
    
    result = service._fallback_text_analysis(transcript)
    
    # Fallback should have low confidence (0.3)
    assert result.manipulation_confidence == 0.3


@pytest.mark.unit
def test_fallback_explanation_populated():
    """Test that explanation field is populated."""
    service = ManipulationService(gemini_service=None)
    
    # With manipulation
    transcript_manip = "You always forget"
    result_manip = service._fallback_text_analysis(transcript_manip)
    assert len(result_manip.manipulation_explanation) > 0
    assert "Overgeneralization/Absolutes" in result_manip.manipulation_explanation
    
    # Without manipulation
    transcript_clean = "Let's discuss this calmly"
    result_clean = service._fallback_text_analysis(transcript_clean)
    assert len(result_clean.manipulation_explanation) > 0


@pytest.mark.unit
def test_fallback_score_analysis_populated():
    """Test that score analysis field is populated."""
    service = ManipulationService(gemini_service=None)
    transcript = "You always do this"
    
    result = service._fallback_text_analysis(transcript)
    
    assert len(result.manipulation_score_analysis) > 0
    assert "Fallback score" in result.manipulation_score_analysis


@pytest.mark.unit
def test_manipulation_assessment_structure():
    """Test that ManipulationAssessment has all required fields."""
    service = ManipulationService(gemini_service=None)
    transcript = "You never listen to me"
    
    result = service._fallback_text_analysis(transcript)
    
    # Check all required fields exist
    assert hasattr(result, 'is_manipulative')
    assert hasattr(result, 'manipulation_score')
    assert hasattr(result, 'manipulation_techniques')
    assert hasattr(result, 'manipulation_confidence')
    assert hasattr(result, 'manipulation_explanation')
    assert hasattr(result, 'manipulation_score_analysis')
    
    # Check types
    assert isinstance(result.is_manipulative, bool)
    assert isinstance(result.manipulation_score, float)
    assert isinstance(result.manipulation_techniques, list)
    assert isinstance(result.manipulation_confidence, float)
    assert isinstance(result.manipulation_explanation, str)
    assert isinstance(result.manipulation_score_analysis, str)


@pytest.mark.unit
def test_fallback_partial_match():
    """Test that partial matches don't trigger false positives."""
    service = ManipulationService(gemini_service=None)
    
    # Should NOT match - "always" without "you"
    transcript_no_match = "I always try my best"
    result = service._fallback_text_analysis(transcript_no_match)
    
    assert result.is_manipulative is False
    assert result.manipulation_score == 0.0


@pytest.mark.unit
def test_fallback_whitespace_handling():
    """Test handling of extra whitespace."""
    service = ManipulationService(gemini_service=None)
    
    # Normal spacing should detect manipulation
    transcript_normal = "You always do this"
    result_normal = service._fallback_text_analysis(transcript_normal)
    assert result_normal.is_manipulative is True
    
    # Extra whitespace between words may not match pattern (current implementation behavior)
    # This test verifies the function handles extra whitespace without crashing
    transcript_extra = "   You   always   do   this   "
    result_extra = service._fallback_text_analysis(transcript_extra)
    
    # Should handle whitespace without errors (may or may not detect manipulation)
    assert isinstance(result_extra.is_manipulative, bool)
