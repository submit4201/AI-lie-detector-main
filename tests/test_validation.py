#!/usr/bin/env python3

import requests
import json

def test_analyze_with_mock_transcript():
    """Test the structured output validation by mocking a successful transcript"""
    
    # We'll create a quick test by temporarily modifying the query_gemini function
    # to return a test response without calling the actual Gemini API
    
    print("[SEARCH] Testing structured output validation system...")
    print("[DATA] Creating mock Gemini response to test validation...")
    print("=" * 60)
    
    # Test with mock data that has the list-to-string conversion issue
    mock_gemini_response = {
        "speaker_transcripts": {"Speaker 1": "This is a test transcript"},
        "red_flags_per_speaker": {"Speaker 1": ["Inconsistent details", "Vague responses"]},
        "credibility_score": 75,
        "confidence_level": "high",
        "gemini_summary": {
            "tone": "The speaker appears nervous and hesitant",
            "motivation": "Appears to be withholding information",
            "credibility": "Moderate credibility with some concerns",
            "emotional_state": "Anxious and defensive",
            "communication_style": "Evasive and indirect",
            "key_concerns": ["Lack of specific details", "Inconsistent timeline"],  # This is a list!
            "strengths": ["Clear speech", "Responsive to questions"]  # This is also a list!
        },
        "recommendations": [
            "Follow up with specific questions about timeline",
            "Request documentation to verify claims"
        ],
        "linguistic_analysis": {
            "speech_patterns": "Frequent pauses and hesitations",
            "word_choice": "Uses qualifiers and uncertain language",
            "emotional_consistency": "Emotions match claimed stress level",
            "detail_level": "Lacks specific details in key areas"
        },
        "risk_assessment": {
            "overall_risk": "medium",
            "risk_factors": ["Information gaps", "Inconsistent details"],
            "mitigation_suggestions": ["Verify claims", "Follow up interview"]
        },
        "manipulation_assessment": {
            "manipulation_score": 70,
            "manipulation_tactics": ["Gaslighting"],
            "manipulation_explanation": "Speaker attempts to distort reality.",
            "example_phrases": ["You're imagining things."]
        },
        "argument_analysis": {
            "argument_strengths": ["Clear examples provided"],
            "argument_weaknesses": ["Lacks statistical evidence"],
            "overall_argument_coherence_score": 65
        },
        "speaker_attitude": {
            "respect_level_score": 40,
            "sarcasm_detected": True,
            "sarcasm_confidence_score": 80,
            "tone_indicators_respect_sarcasm": ["Excessive politeness", "Contradictory statements"]
        },
        "enhanced_understanding": {
            "key_inconsistencies": ["Timeline of events doesn't match"],
            "areas_of_evasiveness": ["Questions about finances"],
            "suggested_follow_up_questions": ["Can you clarify the dates?", "What was your exact role?"],
            "unverified_claims": ["Claimed to be an expert."]
        }
    }

    mock_gemini_response_invalid = {
        "speaker_transcripts": {"Speaker 1": "This is a test transcript"},
        "red_flags_per_speaker": {"Speaker 1": ["Inconsistent details"]},
        "credibility_score": "high", # Invalid type
        "confidence_level": "super_high", # Invalid value
        "gemini_summary": { # Missing some fields, some invalid
            "tone": ["Should be string", "not list"],
            "motivation": "Okay",
            # credibility missing
            "emotional_state": 123, # Invalid type
        },
        "recommendations": "Should be a list", # Invalid type
        "linguistic_analysis": { # Missing many fields
            "word_count": "low" # Invalid type
        },
        "risk_assessment": {
            "overall_risk": "catastrophic", # Invalid value
            "risk_factors": "Should be list"
            # mitigation_suggestions missing
        },
        "manipulation_assessment": {
            "manipulation_score": "very high indeed", # Invalid type
            "manipulation_tactics": "Gaslighting as a string", # Invalid type
            "manipulation_explanation": True, # Invalid type
            # example_phrases missing
        },
        "argument_analysis": {
            "argument_strengths": [123, "Valid point"], # Invalid item type
            "overall_argument_coherence_score": 150 # Out of range
            # argument_weaknesses missing
        },
        "speaker_attitude": {
            "respect_level_score": -20, # Missing, will be defaulted, then this is out of range if not handled by default first
            "sarcasm_detected": "maybe not", # Invalid type
            # sarcasm_confidence_score missing
            "tone_indicators_respect_sarcasm": {"key": "value"} # Invalid type
        },
        "enhanced_understanding": {
            "key_inconsistencies": True, # Invalid type
            "suggested_follow_up_questions": [1, 2, 3], # Invalid item types
            # areas_of_evasiveness missing
            # unverified_claims missing
        }
    }
        # Test the validation function directly
    import sys
    sys.path.append('backend')
    from services.gemini_service import validate_and_structure_gemini_response
    
    test_transcript = "This is a test transcript for validation"
    validated_response = validate_and_structure_gemini_response(mock_gemini_response, test_transcript)
    
    print("[PASS] Validation completed! Checking results...")
    print("=" * 60)
    
    # Check if list-to-string conversion worked
    key_concerns = validated_response.get('gemini_summary', {}).get('key_concerns', '')
    strengths = validated_response.get('gemini_summary', {}).get('strengths', '')
    
    print(f"[TOOL] List-to-String Conversion Test:")
    print(f"   Original key_concerns type: {type(mock_gemini_response['gemini_summary']['key_concerns'])}")
    print(f"   Validated key_concerns type: {type(key_concerns)}")
    print(f"   Validated key_concerns value: {key_concerns}")
    print()
    print(f"   Original strengths type: {type(mock_gemini_response['gemini_summary']['strengths'])}")
    print(f"   Validated strengths type: {type(strengths)}")
    print(f"   Validated strengths value: {strengths}")
    print()
    
    # Check all required fields
    required_fields = [
        'speaker_transcripts', 'red_flags_per_speaker', 'credibility_score',
        'confidence_level', 'gemini_summary', 'recommendations', 
        'linguistic_analysis', 'risk_assessment',
        'manipulation_assessment', 'argument_analysis',
        'speaker_attitude', 'enhanced_understanding'
    ]
    
    print("📋 Required Fields Validation (Valid Mock):")
    all_present_valid = True
    for field in required_fields:
        status = "[PASS]" if field in validated_response and validated_response[field] is not None else "[FAIL]"
        if not (field in validated_response and validated_response[field] is not None):
            all_present_valid = False
        print(f"   {status} {field}")
    
    print()
    print(f"[TARGET] Credibility Score: {validated_response.get('credibility_score')} (type: {type(validated_response.get('credibility_score'))})")
    print(f"[DATA] Confidence Level: {validated_response.get('confidence_level')}")
    print(f"[WARN]  Risk Level: {validated_response.get('risk_assessment', {}).get('overall_risk')}")

    # --- Detailed checks for new valid sections ---
    print("\n" + "=" * 30 + " VALID MOCK NEW SECTIONS " + "=" * 30)

    # Manipulation Assessment
    ma_data = validated_response.get('manipulation_assessment', {})
    print("\n[TEST] Manipulation Assessment Validation:")
    print(f"   Present: {'[PASS]' if ma_data else '[FAIL]'}")
    score = ma_data.get('manipulation_score')
    print(f"   manipulation_score type: {type(score)}, Value: {score}, In Range: {'[PASS]' if isinstance(score, int) and 0 <= score <= 100 else '[FAIL]'}")
    tactics = ma_data.get('manipulation_tactics')
    tactics_is_list = isinstance(tactics, list)
    tactics_items_all_str = False
    if tactics_is_list:
        tactics_items_all_str = all(isinstance(i, str) for i in tactics)
    print(f"   manipulation_tactics type: {type(tactics)}, Items all str: {tactics_items_all_str} {'[PASS]' if tactics_is_list else '[FAIL]'}")
    explanation = ma_data.get('manipulation_explanation')
    print(f"   manipulation_explanation type: {type(explanation)} {'[PASS]' if isinstance(explanation, str) else '[FAIL]'}")
    phrases = ma_data.get('example_phrases')
    phrases_items_all_str = isinstance(phrases, list) and all(isinstance(i, str) for i in phrases)
    print(f"   example_phrases type: {type(phrases)}, Items all str: {phrases_items_all_str} {'[PASS]' if isinstance(phrases, list) else '[FAIL]'}")

    # Argument Analysis
    aa_data = validated_response.get('argument_analysis', {})
    print("\n[TEST] Argument Analysis Validation:")
    print(f"   Present: {'[PASS]' if aa_data else '[FAIL]'}")
    strengths_aa = aa_data.get('argument_strengths')
    strengths_items_all_str = isinstance(strengths_aa, list) and all(isinstance(i, str) for i in strengths_aa or [])
    print(f"   argument_strengths type: {type(strengths_aa)}, Items all str: {strengths_items_all_str} {'[PASS]' if isinstance(strengths_aa, list) else '[FAIL]'}")
    weaknesses_aa = aa_data.get('argument_weaknesses')
    weaknesses_items_all_str = isinstance(weaknesses_aa, list) and all(isinstance(i, str) for i in weaknesses_aa or [])
    print(f"   argument_weaknesses type: {type(weaknesses_aa)}, Items all str: {weaknesses_items_all_str} {'[PASS]' if isinstance(weaknesses_aa, list) else '[FAIL]'}")
    coherence_score = aa_data.get('overall_argument_coherence_score')
    print(f"   overall_argument_coherence_score type: {type(coherence_score)}, Value: {coherence_score}, In Range: {'[PASS]' if isinstance(coherence_score, int) and 0 <= coherence_score <= 100 else '[FAIL]'}")

    # Speaker Attitude
    sa_data = validated_response.get('speaker_attitude', {})
    print("\n[TEST] Speaker Attitude Validation:")
    print(f"   Present: {'[PASS]' if sa_data else '[FAIL]'}")
    respect_score = sa_data.get('respect_level_score')
    print(f"   respect_level_score type: {type(respect_score)}, Value: {respect_score}, In Range: {'[PASS]' if isinstance(respect_score, int) and 0 <= respect_score <= 100 else '[FAIL]'}")
    sarcasm_detected = sa_data.get('sarcasm_detected')
    print(f"   sarcasm_detected type: {type(sarcasm_detected)} {'[PASS]' if isinstance(sarcasm_detected, bool) else '[FAIL]'}")
    sarcasm_confidence = sa_data.get('sarcasm_confidence_score')
    print(f"   sarcasm_confidence_score type: {type(sarcasm_confidence)}, Value: {sarcasm_confidence}, In Range: {'[PASS]' if isinstance(sarcasm_confidence, int) and 0 <= sarcasm_confidence <= 100 else '[FAIL]'}")
    tone_indicators = sa_data.get('tone_indicators_respect_sarcasm')
    tone_items_all_str = isinstance(tone_indicators, list) and all(isinstance(i, str) for i in tone_indicators or [])
    print(f"   tone_indicators_respect_sarcasm type: {type(tone_indicators)}, Items all str: {tone_items_all_str} {'[PASS]' if isinstance(tone_indicators, list) else '[FAIL]'}")

    # Enhanced Understanding
    eu_data = validated_response.get('enhanced_understanding', {})
    print("\n[TEST] Enhanced Understanding Validation:")
    print(f"   Present: {'[PASS]' if eu_data else '[FAIL]'}")
    inconsistencies = eu_data.get('key_inconsistencies')
    print(f"   key_inconsistencies type: {type(inconsistencies)}, Items type: {'<class \'str\'>' if all(isinstance(i, str) for i in inconsistencies) else 'MIXED/WRONG'} {'[PASS]' if isinstance(inconsistencies, list) else '[FAIL]'}")
    evasiveness = eu_data.get('areas_of_evasiveness')
    print(f"   areas_of_evasiveness type: {type(evasiveness)}, Items type: {'<class \'str\'>' if all(isinstance(i, str) for i in evasiveness) else 'MIXED/WRONG'} {'[PASS]' if isinstance(evasiveness, list) else '[FAIL]'}")
    follow_up = eu_data.get('suggested_follow_up_questions')
    print(f"   suggested_follow_up_questions type: {type(follow_up)}, Items type: {'<class \'str\'>' if all(isinstance(i, str) for i in follow_up) else 'MIXED/WRONG'} {'[PASS]' if isinstance(follow_up, list) else '[FAIL]'}")
    unverified = eu_data.get('unverified_claims')
    print(f"   unverified_claims type: {type(unverified)}, Items type: {'<class \'str\'>' if all(isinstance(i, str) for i in unverified) else 'MIXED/WRONG'} {'[PASS]' if isinstance(unverified, list) else '[FAIL]'}")

    print("\n" + "=" * 28 + " INVALID MOCK NEW SECTIONS " + "=" * 28)
    validated_invalid_response = validate_and_structure_gemini_response(mock_gemini_response_invalid, test_transcript)

    # Default values from gemini_service.py's default_structure for new fields
    default_manip_score = 0
    default_manip_tactics = []
    default_arg_coh_score = 0
    default_respect_score = 50 # As per Pydantic model
    default_sarc_detected = False
    default_sarc_conf_score = 0
    default_list = []

    # Manipulation Assessment (Invalid)
    ma_invalid = validated_invalid_response.get('manipulation_assessment', {})
    print("\n[TEST] Invalid Manipulation Assessment - Default Application:")
    score_inv_ma = ma_invalid.get('manipulation_score')
    print(f"   manipulation_score type: {type(score_inv_ma)}, Value: {score_inv_ma} (Defaulted from 'very high indeed') {'[PASS]' if score_inv_ma == default_manip_score else '[FAIL] Default Applied Incorrectly'}")
    tactics_inv_ma = ma_invalid.get('manipulation_tactics')
    print(f"   manipulation_tactics type: {type(tactics_inv_ma)}, Value: {tactics_inv_ma} (Defaulted from string) {'[PASS]' if tactics_inv_ma == default_manip_tactics else '[FAIL] Default Applied Incorrectly'}")
    explanation_inv_ma = ma_invalid.get('manipulation_explanation')
    print(f"   manipulation_explanation type: {type(explanation_inv_ma)}, Value: '{explanation_inv_ma}' (Defaulted from bool) {'[PASS]' if explanation_inv_ma == 'N/A' else '[FAIL] Default Applied Incorrectly'}")
    phrases_inv_ma = ma_invalid.get('example_phrases')
    print(f"   example_phrases type: {type(phrases_inv_ma)}, Value: {phrases_inv_ma} (Defaulted from missing) {'[PASS]' if phrases_inv_ma == default_list else '[FAIL] Default Applied Incorrectly'}")

    # Argument Analysis (Invalid)
    aa_invalid = validated_invalid_response.get('argument_analysis', {})
    print("\n[TEST] Invalid Argument Analysis - Default Application:")
    strengths_inv_aa = aa_invalid.get('argument_strengths') # List with int
    print(f"   argument_strengths type: {type(strengths_inv_aa)}, Value: {strengths_inv_aa} (Items Defaulted to str) {'[PASS]' if all(isinstance(i,str) for i in strengths_inv_aa) and strengths_inv_aa[0]=='123' else '[FAIL] Default/Conversion Applied Incorrectly'}")
    weaknesses_inv_aa = aa_invalid.get('argument_weaknesses')
    print(f"   argument_weaknesses type: {type(weaknesses_inv_aa)}, Value: {weaknesses_inv_aa} (Defaulted from missing) {'[PASS]' if weaknesses_inv_aa == default_list else '[FAIL] Default Applied Incorrectly'}")
    coh_score_inv_aa = aa_invalid.get('overall_argument_coherence_score')
    print(f"   overall_argument_coherence_score type: {type(coh_score_inv_aa)}, Value: {coh_score_inv_aa} (Defaulted from 150) {'[PASS]' if coh_score_inv_aa == 0 else '[FAIL] Default Applied Incorrectly (expected 0 for out of range)'}") # Assuming 0-100 range sets to 0 or 100 if out of bounds, or default if type wrong. The default is 0.

    # Speaker Attitude (Invalid)
    sa_invalid = validated_invalid_response.get('speaker_attitude', {})
    print("\n[TEST] Invalid Speaker Attitude - Default Application:")
    respect_inv_sa = sa_invalid.get('respect_level_score') # Missing, should be 50
    print(f"   respect_level_score type: {type(respect_inv_sa)}, Value: {respect_inv_sa} (Defaulted from missing or out of range -20) {'[PASS]' if respect_inv_sa == default_respect_score else '[FAIL] Default Applied Incorrectly'}")
    sarc_detected_inv_sa = sa_invalid.get('sarcasm_detected')
    print(f"   sarcasm_detected type: {type(sarc_detected_inv_sa)}, Value: {sarc_detected_inv_sa} (Defaulted from 'maybe not') {'[PASS]' if sarc_detected_inv_sa == default_sarc_detected else '[FAIL] Default Applied Incorrectly'}")
    sarc_conf_inv_sa = sa_invalid.get('sarcasm_confidence_score')
    print(f"   sarcasm_confidence_score type: {type(sarc_conf_inv_sa)}, Value: {sarc_conf_inv_sa} (Defaulted from missing) {'[PASS]' if sarc_conf_inv_sa == default_sarc_conf_score else '[FAIL] Default Applied Incorrectly'}")
    tone_ind_inv_sa = sa_invalid.get('tone_indicators_respect_sarcasm')
    print(f"   tone_indicators_respect_sarcasm type: {type(tone_ind_inv_sa)}, Value: {tone_ind_inv_sa} (Defaulted from dict) {'[PASS]' if tone_ind_inv_sa == default_list else '[FAIL] Default Applied Incorrectly'}")

    # Enhanced Understanding (Invalid)
    eu_invalid = validated_invalid_response.get('enhanced_understanding', {})
    print("\n[TEST] Invalid Enhanced Understanding - Default Application:")
    incons_inv_eu = eu_invalid.get('key_inconsistencies')
    print(f"   key_inconsistencies type: {type(incons_inv_eu)}, Value: {incons_inv_eu} (Defaulted from bool) {'[PASS]' if incons_inv_eu == default_list else '[FAIL] Default Applied Incorrectly'}")
    evas_inv_eu = eu_invalid.get('areas_of_evasiveness')
    print(f"   areas_of_evasiveness type: {type(evas_inv_eu)}, Value: {evas_inv_eu} (Defaulted from missing) {'[PASS]' if evas_inv_eu == default_list else '[FAIL] Default Applied Incorrectly'}")
    follow_up_inv_eu = eu_invalid.get('suggested_follow_up_questions') # list of int
    print(f"   suggested_follow_up_questions type: {type(follow_up_inv_eu)}, Value: {follow_up_inv_eu} (Items Defaulted to str) {'[PASS]' if all(isinstance(i,str) for i in follow_up_inv_eu) and follow_up_inv_eu[0]=='1' else '[FAIL] Default/Conversion Applied Incorrectly'}")
    unverified_inv_eu = eu_invalid.get('unverified_claims')
    print(f"   unverified_claims type: {type(unverified_inv_eu)}, Value: {unverified_inv_eu} (Defaulted from missing) {'[PASS]' if unverified_inv_eu == default_list else '[FAIL] Default Applied Incorrectly'}")

    # Final Success/Failure
    # Basic check, can be made more robust by checking each assertion
    num_checks_passed = sum(1 for line in open('test_validation.py').readlines() if '[PASS]' in line) # Approximation
    num_checks_failed = sum(1 for line in open('test_validation.py').readlines() if '[FAIL]' in line) # Approximation
    
    if all_present_valid and isinstance(key_concerns, str) and isinstance(strengths, str) and num_checks_failed == 0 : # num_checks_failed needs to be calculated based on actual test results
        print("\n[SUCCESS] SUCCESS: Structured output validation system working correctly for existing and new fields!")
        print("[PASS] All required fields present in valid mock.")
        print("[PASS] List-to-string conversion working for gemini_summary.")
        print("[PASS] Data types and defaults correctly applied for new fields in both valid and invalid mocks.")
    else:
        print(f"\n[FAIL] ISSUES DETECTED in validation system. Review checks above. Failed checks approx: {num_checks_failed}")
    
    print("\n📖 Complete Validated Response (from valid mock):")
    print(json.dumps(validated_response, indent=2))

if __name__ == "__main__":
    test_analyze_with_mock_transcript()
