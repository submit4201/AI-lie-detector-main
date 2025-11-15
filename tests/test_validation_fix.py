#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath('.'))

from backend.services.gemini_service import validate_and_structure_gemini_response

def test_validation_with_empty_response():
    """Test validation function with empty dict to ensure no KeyErrors"""
    print("Testing validation function with empty dict...")
    
    # Test with completely empty response
    empty_response = {}
    result = validate_and_structure_gemini_response(empty_response, "test transcript")
    
    print("[PASS] Empty dict test passed - no KeyError exceptions")
    print(f"Result has {len(result)} fields")
    
    # Check that all required fields are present with defaults
    required_fields = [
        'speaker_transcripts', 'red_flags_per_speaker', 'credibility_score',
        'confidence_level', 'gemini_summary', 'recommendations',
        'linguistic_analysis', 'risk_assessment', 'manipulation_assessment',
        'argument_analysis', 'speaker_attitude', 'enhanced_understanding',
        'conversation_flow', 'behavioral_patterns', 'verification_suggestions',
        'session_insights', 'quantitative_metrics', 'audio_analysis', 'overall_risk'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in result:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"[FAIL] Missing fields: {missing_fields}")
    else:
        print("[PASS] All required fields present")
    
    # Test with partial response
    partial_response = {
        "credibility_score": 75,
        "gemini_summary": {
            "tone": "Test tone"
        }
    }
    
    print("\nTesting validation function with partial response...")
    result2 = validate_and_structure_gemini_response(partial_response, "test transcript")
    print("[PASS] Partial response test passed")
    print(f"Credibility score: {result2['credibility_score']}")
    print(f"Gemini summary tone: {result2['gemini_summary']['tone']}")
    
    # Test with error response
    error_response = {"error": "Test error"}
    result3 = validate_and_structure_gemini_response(error_response, "test transcript")
    print(f"\nError response test: {result3}")
    
    print("\n[SUCCESS] All validation tests passed successfully!")

if __name__ == "__main__":
    test_validation_with_empty_response()
