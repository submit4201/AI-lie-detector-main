"""
Unit tests for psychological service fallback functions.
Tests fallback psychological analysis without LLM dependencies.
"""
import pytest
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.psychological_service import PsychologicalService


@pytest.mark.unit
def test_fallback_analysis_structure():
    """Test that fallback analysis returns all required fields."""
    service = PsychologicalService(gemini_service=None)
    result = service._fallback_analysis("test transcript")
    
    # Check all required fields exist
    assert hasattr(result, 'emotional_state')
    assert hasattr(result, 'emotional_state_analysis')
    assert hasattr(result, 'cognitive_load')
    assert hasattr(result, 'cognitive_load_analysis')
    assert hasattr(result, 'stress_level')
    assert hasattr(result, 'stress_level_analysis')
    assert hasattr(result, 'confidence_level')
    assert hasattr(result, 'confidence_level_analysis')
    assert hasattr(result, 'psychological_summary')
    assert hasattr(result, 'potential_biases')
    assert hasattr(result, 'potential_biases_analysis')


@pytest.mark.unit
def test_fallback_analysis_types():
    """Test that fallback analysis returns correct types."""
    service = PsychologicalService(gemini_service=None)
    result = service._fallback_analysis("test transcript")
    
    # Check types
    assert isinstance(result.emotional_state, str)
    assert isinstance(result.emotional_state_analysis, str)
    assert isinstance(result.cognitive_load, str)
    assert isinstance(result.cognitive_load_analysis, str)
    assert isinstance(result.stress_level, float)
    assert isinstance(result.stress_level_analysis, str)
    assert isinstance(result.confidence_level, float)
    assert isinstance(result.confidence_level_analysis, str)
    assert isinstance(result.psychological_summary, str)
    assert isinstance(result.potential_biases, list)
    assert isinstance(result.potential_biases_analysis, str)


@pytest.mark.unit
def test_fallback_default_emotional_state():
    """Test that fallback sets emotional state to Neutral."""
    service = PsychologicalService(gemini_service=None)
    result = service._fallback_analysis("test transcript")
    
    assert result.emotional_state == "Neutral"


@pytest.mark.unit
def test_fallback_default_cognitive_load():
    """Test that fallback sets cognitive load to Normal."""
    service = PsychologicalService(gemini_service=None)
    result = service._fallback_analysis("test transcript")
    
    assert result.cognitive_load == "Normal"


@pytest.mark.unit
def test_fallback_default_stress_level():
    """Test that fallback sets stress level to 0.0."""
    service = PsychologicalService(gemini_service=None)
    result = service._fallback_analysis("test transcript")
    
    assert result.stress_level == 0.0
    assert result.stress_level >= 0.0
    assert result.stress_level <= 1.0


@pytest.mark.unit
def test_fallback_default_confidence_level():
    """Test that fallback sets confidence level to 0.0."""
    service = PsychologicalService(gemini_service=None)
    result = service._fallback_analysis("test transcript")
    
    assert result.confidence_level == 0.0
    assert result.confidence_level >= 0.0
    assert result.confidence_level <= 1.0


@pytest.mark.unit
def test_fallback_default_potential_biases():
    """Test that fallback sets potential biases to empty list."""
    service = PsychologicalService(gemini_service=None)
    result = service._fallback_analysis("test transcript")
    
    assert result.potential_biases == []
    assert isinstance(result.potential_biases, list)


@pytest.mark.unit
def test_fallback_analysis_fields_not_empty():
    """Test that fallback analysis fields contain meaningful values."""
    service = PsychologicalService(gemini_service=None)
    result = service._fallback_analysis("test transcript")
    
    # String fields should not be empty
    assert len(result.emotional_state) > 0
    assert len(result.emotional_state_analysis) > 0
    assert len(result.cognitive_load) > 0
    assert len(result.cognitive_load_analysis) > 0
    assert len(result.stress_level_analysis) > 0
    assert len(result.confidence_level_analysis) > 0
    assert len(result.psychological_summary) > 0
    assert len(result.potential_biases_analysis) > 0


@pytest.mark.unit
def test_fallback_analysis_with_empty_transcript():
    """Test fallback analysis with empty transcript."""
    service = PsychologicalService(gemini_service=None)
    result = service._fallback_analysis("")
    
    # Should still return valid fallback values
    assert result.emotional_state == "Neutral"
    assert result.cognitive_load == "Normal"
    assert result.stress_level == 0.0
    assert result.confidence_level == 0.0


@pytest.mark.unit
def test_fallback_analysis_with_long_transcript():
    """Test fallback analysis with long transcript snippet."""
    service = PsychologicalService(gemini_service=None)
    long_transcript = "This is a long transcript. " * 100
    result = service._fallback_analysis(long_transcript)
    
    # Should handle long transcripts gracefully
    assert result.emotional_state == "Neutral"
    assert result.cognitive_load == "Normal"


@pytest.mark.unit
def test_fallback_analysis_consistency():
    """Test that fallback analysis returns consistent results."""
    service = PsychologicalService(gemini_service=None)
    transcript = "test transcript"
    
    result1 = service._fallback_analysis(transcript)
    result2 = service._fallback_analysis(transcript)
    
    # Results should be identical for same transcript
    assert result1.emotional_state == result2.emotional_state
    assert result1.cognitive_load == result2.cognitive_load
    assert result1.stress_level == result2.stress_level
    assert result1.confidence_level == result2.confidence_level


@pytest.mark.unit
def test_fallback_contains_fallback_indicator():
    """Test that fallback analysis indicates it's a fallback."""
    service = PsychologicalService(gemini_service=None)
    result = service._fallback_analysis("test transcript")
    
    # Analysis fields should indicate this is a fallback
    assert "Fallback" in result.emotional_state_analysis
    assert "Fallback" in result.cognitive_load_analysis
    assert "Fallback" in result.stress_level_analysis
    assert "Fallback" in result.confidence_level_analysis
    assert "Fallback" in result.psychological_summary
    assert "Fallback" in result.potential_biases_analysis


@pytest.mark.unit
def test_psychological_analysis_valid_ranges():
    """Test that numerical values are in valid ranges."""
    service = PsychologicalService(gemini_service=None)
    result = service._fallback_analysis("test transcript")
    
    # Stress level should be between 0.0 and 1.0
    assert 0.0 <= result.stress_level <= 1.0
    
    # Confidence level should be between 0.0 and 1.0
    assert 0.0 <= result.confidence_level <= 1.0


@pytest.mark.unit
def test_service_initialization_without_gemini():
    """Test that service can be initialized without gemini_service."""
    # Should not raise an error
    service = PsychologicalService(gemini_service=None)
    assert service is not None
    assert hasattr(service, '_fallback_analysis')


@pytest.mark.unit
def test_fallback_with_special_characters():
    """Test fallback analysis with special characters in transcript."""
    service = PsychologicalService(gemini_service=None)
    transcript = "Test @#$% transcript with !@#$ special &*() characters"
    
    result = service._fallback_analysis(transcript)
    
    # Should handle special characters without errors
    assert result.emotional_state == "Neutral"
    assert result.cognitive_load == "Normal"


@pytest.mark.unit
def test_fallback_with_unicode():
    """Test fallback analysis with unicode characters."""
    service = PsychologicalService(gemini_service=None)
    transcript = "Test transcript with unicode: 你好 مرحبا 🙂"
    
    result = service._fallback_analysis(transcript)
    
    # Should handle unicode without errors
    assert result.emotional_state == "Neutral"
    assert result.cognitive_load == "Normal"
