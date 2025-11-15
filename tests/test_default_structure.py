"""
Pytest unit tests for default data structure validation.
Tests that the default structure contains all required fields with correct types.
"""
import pytest


@pytest.mark.unit
def test_default_structure_all_fields():
    """Test that default structure contains all required top-level fields."""
    
    default_structure = {
        'speaker_transcripts': {"Speaker 1": "No transcript available"},
        'red_flags_per_speaker': {"Speaker 1": []},
        'credibility_score': 50,
        'confidence_level': "medium",
        'gemini_summary': {
            "tone": "Analysis not available",
            "motivation": "Analysis not available", 
            "credibility": "Analysis not available",
            "emotional_state": "Analysis not available",
            "communication_style": "Analysis not available",
            "key_concerns": "Analysis not available",
            "strengths": "Analysis not available"
        },
        'recommendations': ["Further analysis needed"],
        'linguistic_analysis': {
            "speech_patterns": "Analysis not available",
            "word_choice": "Analysis not available",
            "emotional_consistency": "Analysis not available", 
            "detail_level": "Analysis not available"
        },
        'risk_assessment': {
            "overall_risk": "medium",
            "risk_factors": ["Insufficient data"],
            "mitigation_suggestions": ["Collect more information"]
        },
        'manipulation_assessment': {
            "manipulation_score": 0,
            "manipulation_tactics": [],
            "manipulation_explanation": "No manipulation detected.",
            "example_phrases": []
        },
        'argument_analysis': {
            "argument_strengths": ["Analysis needed"],
            "argument_weaknesses": ["Analysis needed"],
            "overall_argument_coherence_score": 50
        },
        'speaker_attitude': {
            "respect_level_score": 50,
            "sarcasm_detected": False,
            "sarcasm_confidence_score": 0,
            "tone_indicators_respect_sarcasm": []
        },
        'enhanced_understanding': {
            "key_inconsistencies": [],
            "areas_of_evasiveness": [],
            "suggested_follow_up_questions": ["Ask for clarification"],
            "unverified_claims": []
        },
        'conversation_flow': "Analysis not available",
        'behavioral_patterns': "Analysis not available", 
        'verification_suggestions': ["Request additional information"],
        'session_insights': {
            "overall_session_assessment": "Analysis in progress",
            "trust_building_indicators": "Analysis not available",
            "concern_escalation": "Analysis not available"
        },
        'quantitative_metrics': {
            "speech_rate_words_per_minute": 0,
            "formality_score": 50,
            "hesitation_count": 0,
            "filler_word_frequency": 0,
            "repetition_count": 0,
            "sentence_length_variability": 50,
            "vocabulary_complexity": 50
        },
        'audio_analysis': {
            "vocal_stress_indicators": ["Analysis not available"],
            "pitch_analysis": "Analysis not available",
            "pause_patterns": "Analysis not available", 
            "vocal_confidence_level": 50,
            "speaking_pace_consistency": "Analysis not available",
            "speaking_rate_variations": "Analysis not available",
            "voice_quality": "Analysis not available"
        },
        'overall_risk': "medium"
    }
    
    # Test all top-level fields with expected types
    test_cases = [
        ('credibility_score', int),
        ('confidence_level', str),
        ('gemini_summary', dict),
        ('linguistic_analysis', dict),
        ('risk_assessment', dict),
        ('manipulation_assessment', dict),
        ('argument_analysis', dict),
        ('speaker_attitude', dict),
        ('enhanced_understanding', dict),
        ('conversation_flow', str),
        ('behavioral_patterns', str),
        ('verification_suggestions', list),
        ('session_insights', dict),
        ('quantitative_metrics', dict),
        ('audio_analysis', dict),
        ('overall_risk', str)
    ]
    
    for field, expected_type in test_cases:
        assert field in default_structure, f"Missing required field: {field}"
        assert isinstance(default_structure[field], expected_type), \
            f"Field {field} should be {expected_type.__name__}, got {type(default_structure[field]).__name__}"


@pytest.mark.unit
def test_default_structure_nested_fields():
    """Test that nested fields in default structure are accessible."""
    
    default_structure = {
        'gemini_summary': {
            "tone": "Analysis not available",
            "motivation": "Analysis not available", 
            "credibility": "Analysis not available",
            "emotional_state": "Analysis not available",
            "communication_style": "Analysis not available",
            "key_concerns": "Analysis not available",
            "strengths": "Analysis not available"
        },
        'manipulation_assessment': {
            "manipulation_score": 0,
            "manipulation_tactics": [],
            "manipulation_explanation": "No manipulation detected.",
            "example_phrases": []
        },
        'argument_analysis': {
            "argument_strengths": ["Analysis needed"],
            "argument_weaknesses": ["Analysis needed"],
            "overall_argument_coherence_score": 50
        },
        'speaker_attitude': {
            "respect_level_score": 50,
            "sarcasm_detected": False,
            "sarcasm_confidence_score": 0,
            "tone_indicators_respect_sarcasm": []
        },
        'session_insights': {
            "overall_session_assessment": "Analysis in progress",
            "trust_building_indicators": "Analysis not available",
            "concern_escalation": "Analysis not available"
        },
        'audio_analysis': {
            "vocal_stress_indicators": ["Analysis not available"],
            "pitch_analysis": "Analysis not available",
            "pause_patterns": "Analysis not available", 
            "vocal_confidence_level": 50,
            "speaking_pace_consistency": "Analysis not available",
            "speaking_rate_variations": "Analysis not available",
            "voice_quality": "Analysis not available"
        }
    }
    
    # Test nested field access
    nested_tests = [
        ('gemini_summary', 'tone', str),
        ('manipulation_assessment', 'manipulation_score', int),
        ('argument_analysis', 'overall_argument_coherence_score', int),
        ('speaker_attitude', 'respect_level_score', int),
        ('speaker_attitude', 'sarcasm_detected', bool),
        ('session_insights', 'overall_session_assessment', str),
        ('audio_analysis', 'vocal_confidence_level', int)
    ]
    
    for parent, child, expected_type in nested_tests:
        assert parent in default_structure, f"Missing parent field: {parent}"
        assert child in default_structure[parent], f"Missing nested field: {parent}.{child}"
        assert isinstance(default_structure[parent][child], expected_type), \
            f"Field {parent}.{child} should be {expected_type.__name__}"


@pytest.mark.unit
def test_default_structure_quantitative_metrics():
    """Test that quantitative metrics have correct structure and types."""
    
    quantitative_metrics = {
        "speech_rate_words_per_minute": 0,
        "formality_score": 50,
        "hesitation_count": 0,
        "filler_word_frequency": 0,
        "repetition_count": 0,
        "sentence_length_variability": 50,
        "vocabulary_complexity": 50
    }
    
    expected_fields = [
        'speech_rate_words_per_minute',
        'formality_score',
        'hesitation_count',
        'filler_word_frequency',
        'repetition_count',
        'sentence_length_variability',
        'vocabulary_complexity'
    ]
    
    for field in expected_fields:
        assert field in quantitative_metrics, f"Missing quantitative metric: {field}"
        assert isinstance(quantitative_metrics[field], (int, float)), \
            f"Quantitative metric {field} should be numeric"


@pytest.mark.unit
def test_default_structure_score_ranges():
    """Test that score fields have valid ranges."""
    
    default_structure = {
        'credibility_score': 50,
        'manipulation_assessment': {
            "manipulation_score": 0,
        },
        'argument_analysis': {
            "overall_argument_coherence_score": 50
        },
        'speaker_attitude': {
            "respect_level_score": 50,
            "sarcasm_confidence_score": 0,
        },
        'quantitative_metrics': {
            "formality_score": 50,
        },
        'audio_analysis': {
            "vocal_confidence_level": 50,
        }
    }
    
    # Test score ranges (typically 0-100)
    assert 0 <= default_structure['credibility_score'] <= 100
    assert 0 <= default_structure['manipulation_assessment']['manipulation_score'] <= 100
    assert 0 <= default_structure['argument_analysis']['overall_argument_coherence_score'] <= 100
    assert 0 <= default_structure['speaker_attitude']['respect_level_score'] <= 100
    assert 0 <= default_structure['speaker_attitude']['sarcasm_confidence_score'] <= 100
    assert 0 <= default_structure['quantitative_metrics']['formality_score'] <= 100
    assert 0 <= default_structure['audio_analysis']['vocal_confidence_level'] <= 100
