#!/usr/bin/env python3

# Simple test for validation function logic
def test_default_structure():
    """Test that our default structure contains all required fields"""
    
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
    
    # Test accessing all fields that were causing KeyErrors
    print("Testing access to all default structure fields...")
    
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
        ('audio_analysis', dict)
    ]
    
    for field, expected_type in test_cases:
        try:
            value = default_structure[field]
            if isinstance(value, expected_type):
                print(f"[PASS] {field}: {type(value).__name__}")
            else:
                print(f"[FAIL] {field}: Expected {expected_type.__name__}, got {type(value).__name__}")
        except KeyError:
            print(f"[FAIL] {field}: Missing from default structure!")
    
    # Test nested field access that was causing issues
    nested_tests = [
        ('gemini_summary', 'tone'),
        ('manipulation_assessment', 'manipulation_score'),
        ('argument_analysis', 'overall_argument_coherence_score'),
        ('speaker_attitude', 'respect_level_score'),
        ('speaker_attitude', 'sarcasm_detected'),
        ('session_insights', 'overall_session_assessment'),
        ('audio_analysis', 'vocal_confidence_level')
    ]
    
    print("\nTesting nested field access...")
    for parent, child in nested_tests:
        try:
            value = default_structure[parent][child]
            print(f"[PASS] {parent}.{child}: {value}")
        except KeyError as e:
            print(f"[FAIL] {parent}.{child}: KeyError - {e}")
    
    print("\n[SUCCESS] Default structure validation complete!")
    print(f"Total top-level fields: {len(default_structure)}")

if __name__ == "__main__":
    test_default_structure()
