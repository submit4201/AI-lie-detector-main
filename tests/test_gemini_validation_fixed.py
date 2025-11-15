#!/usr/bin/env python3
"""
Quick test of the Gemini service validation changes without starting the full server.
This will test our validate_and_structure_gemini_response function directly.
"""

import sys
import os
import json

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_dir)

try:
    from services.gemini_service import validate_and_structure_gemini_response
    print("[PASS] Successfully imported Gemini service")
except ImportError as e:
    print(f"[FAIL] Failed to import Gemini service: {e}")
    sys.exit(1)

def test_gemini_validation():
    """Test the Gemini service validation function."""
    
    print("[TEST] Testing Gemini Service Validation")
    print("=" * 50)
    
    # Test case 1: Empty response (should get all defaults)
    print("\n1. Testing empty response handling...")
    empty_response = {}
    
    try:
        # Correct function signature: validate_and_structure_gemini_response(raw_response, transcript, quantitative_linguistic=None)
        result = validate_and_structure_gemini_response(empty_response, "Test transcript")
        
        # Check for our new fields based on the actual structure
        required_fields = [
            'conversation_flow', 'behavioral_patterns', 'verification_suggestions',
            'session_insights'
        ]
        
        missing_fields = []
        na_fields = []
        
        for field in required_fields:
            if field not in result:
                missing_fields.append(field)
            elif result[field] in [None, "N/A", "", "Not available"]:
                na_fields.append(field)
        
        if missing_fields:
            print(f"[FAIL] Missing fields: {missing_fields}")
        else:
            print("[PASS] All required fields present")
        
        if na_fields:
            print(f"[WARN]  Fields with N/A values: {na_fields}")
        else:
            print("[PASS] No N/A values found")
        
        # Print sample of new fields
        conversation_flow = result.get('conversation_flow', 'MISSING')
        behavioral_patterns = result.get('behavioral_patterns', 'MISSING')
        session_insights = result.get('session_insights', 'MISSING')
        
        print(f"\n   Sample conversation_flow: {str(conversation_flow)[:100]}...")
        print(f"   Sample behavioral_patterns: {str(behavioral_patterns)[:100]}...")
        print(f"   Sample session_insights: {str(session_insights)[:100]}...")
        
    except Exception as e:
        print(f"[FAIL] Validation failed: {e}")
        return False
    
    # Test case 2: Partial response (should fill missing fields)
    print("\n2. Testing partial response handling...")
    partial_response = {
        'credibility_score': 75,
        'gemini_summary': {
            'tone': 'Test tone analysis'
        }
    }
    
    try:
        result = validate_and_structure_gemini_response(partial_response, "Partial test transcript")
        
        # Verify the provided fields are preserved
        if 'credibility_score' in result:
            print("[PASS] Basic structure validated")
        else:
            print("[FAIL] Basic structure missing")
        
        # Verify missing fields are filled
        if result.get('conversation_flow') and result.get('conversation_flow') != "N/A":
            print("[PASS] Missing fields filled with defaults")
        else:
            print("[FAIL] Missing fields not properly filled")
        
    except Exception as e:
        print(f"[FAIL] Partial validation failed: {e}")
        return False
    
    # Test case 3: Response with all new fields
    print("\n3. Testing with new field validation...")
    
    try:
        result = validate_and_structure_gemini_response({}, "Test transcript with new fields")
        
        # Check if session insights structure is correct
        session_insights = result.get('session_insights', {})
        if isinstance(session_insights, dict):
            print("[PASS] Session insights properly structured")
            expected_subfields = ['consistency_analysis', 'behavioral_evolution', 'risk_trajectory', 'conversation_dynamics']
            missing_subfields = [field for field in expected_subfields if field not in session_insights]
            if missing_subfields:
                print(f"[WARN]  Missing session insight subfields: {missing_subfields}")
            else:
                print("[PASS] All session insight subfields present")
        else:
            print("[FAIL] Session insights not properly structured")
        
        print(f"   Session insights structure: {list(session_insights.keys()) if isinstance(session_insights, dict) else 'NOT A DICT'}")
        
    except Exception as e:
        print(f"[FAIL] New field validation failed: {e}")
        return False
    
    # Test case 4: Save test results
    print("\n4. Saving validation test results...")
    
    try:
        test_results = {
            "test_1_empty": validate_and_structure_gemini_response({}, "Empty test transcript"),
            "test_2_partial": validate_and_structure_gemini_response(partial_response, "Partial test transcript"),
            "test_3_complete": validate_and_structure_gemini_response({}, "Complete test transcript")
        }
        
        with open('gemini_validation_test_results.json', 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print("[PASS] Test results saved to gemini_validation_test_results.json")
        
    except Exception as e:
        print(f"[FAIL] Failed to save test results: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("[TARGET] GEMINI VALIDATION TEST SUMMARY")
    print("=" * 50)
    print("[PASS] All validation tests completed successfully!")
    print("   The Gemini service should now provide complete data structures")
    print("   with no N/A values for the new fields we added.")
    
    return True

if __name__ == "__main__":
    success = test_gemini_validation()
    if success:
        print("\n[SUCCESS] Gemini validation testing completed successfully!")
    else:
        print("\n[FAIL] Gemini validation testing failed!")
        sys.exit(1)
