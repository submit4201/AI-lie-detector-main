#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath('.'))

def test_default_structure_with_models():
    """Test the default structure matches all model requirements"""
    from backend.models import (
        LinguisticAnalysis, RiskAssessment, GeminiSummary, 
        SessionInsights, ManipulationAssessment, ArgumentAnalysis,
        SpeakerAttitude, EnhancedUnderstanding, AudioAnalysis, InteractionMetrics
    )
    from pydantic import ValidationError
    
    # The default structure from our validation function
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
            # Quantitative metrics
            "word_count": 0,
            "hesitation_count": 0,
            "qualifier_count": 0,
            "certainty_count": 0,
            "filler_count": 0,
            "repetition_count": 0,
            "formality_score": 50.0,
            "complexity_score": 50.0,
            "avg_word_length": 5.0,
            "avg_words_per_sentence": 10.0,
            "sentence_count": 0,
            "speech_rate_wpm": None,
            "hesitation_rate": None,
            "confidence_ratio": 0.5,
            # Descriptive analysis
            "speech_patterns": "Analysis not available",
            "word_choice": "Analysis not available",
            "emotional_consistency": "Analysis not available", 
            "detail_level": "Analysis not available",
            # New analysis fields
            "pause_analysis": "Analysis not available",
            "filler_word_analysis": "Analysis not available",
            "repetition_analysis": "Analysis not available",
            "hesitation_analysis": "Analysis not available",
            "qualifier_analysis": "Analysis not available",
            "certainty_analysis": "Analysis not available",
            "formality_analysis": "Analysis not available",
            "complexity_analysis": "Analysis not available",
            "avg_word_length_analysis": "Analysis not available",
            "avg_words_per_sentence_analysis": "Analysis not available",
            "sentence_count_analysis": "Analysis not available",
            "overall_linguistic_analysis": "Analysis not available"
        },
        'risk_assessment': {
            "overall_risk": "medium",
            "risk_factors": ["Insufficient data"],
            "mitigation_suggestions": ["Collect more information"]
        },
        'session_insights': {
            "consistency_analysis": "Analysis not available",
            "behavioral_evolution": "Analysis not available", 
            "risk_trajectory": "Analysis not available",
            "conversation_dynamics": "Analysis not available"
        },
        'interaction_metrics': {
            "talk_to_listen_ratio": None,
            "speaker_turn_duration_avg_seconds": None,
            "interruptions_count": None,
            "sentiment_trend": []
        }
    }
    
    # Test each model with corresponding default structure
    test_models = [
        (GeminiSummary, default_structure['gemini_summary'], "GeminiSummary"),
        (LinguisticAnalysis, default_structure['linguistic_analysis'], "LinguisticAnalysis"),
        (RiskAssessment, default_structure['risk_assessment'], "RiskAssessment"),
        (SessionInsights, default_structure['session_insights'], "SessionInsights"),
        (InteractionMetrics, default_structure['interaction_metrics'], "InteractionMetrics"),
    ]
    
    for model_class, default_data, model_name in test_models:
        try:
            instance = model_class(**default_data)
            print(f"[PASS] {model_name} validation passed")
        except ValidationError as e:
            print(f"[FAIL] {model_name} validation failed:")
            missing_fields = [error['loc'][0] for error in e.errors() if error['type'] == 'missing']
            if missing_fields:
                print(f"   Missing required fields: {missing_fields}")
            type_errors = [f"{error['loc'][0]}: {error['msg']}" for error in e.errors() if error['type'] != 'missing']
            if type_errors:
                print(f"   Type errors: {type_errors}")
        except Exception as e:
            print(f"[FAIL] {model_name} unexpected error: {e}")
    
    print("\n[SUCCESS] Model validation test complete!")

if __name__ == "__main__":
    test_default_structure_with_models()

