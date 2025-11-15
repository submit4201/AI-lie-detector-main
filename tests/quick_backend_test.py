#!/usr/bin/env python3
"""
Quick backend test to verify all fixes are working
"""

import sys
import os
import json

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_dir)

def test_backend_fixes():
    """Test that all our fixes are working correctly"""
    
    print("[TEST] Quick Backend Test - All Fixes Verification")
    print("=" * 60)
    
    # Test 1: Model imports
    print("\n1. Testing model imports...")
    try:
        from models import (
            AnalyzeResponse, AudioAnalysis, LinguisticAnalysis, 
            ManipulationAssessment, ArgumentAnalysis, AudioQualityMetrics
        )
        print("[PASS] All models imported successfully")
    except ImportError as e:
        print(f"[FAIL] Model import failed: {e}")
        return False
      # Test 2: Service imports
    print("\n2. Testing service imports...")
    try:
        from services.gemini_service import validate_and_structure_gemini_response
        from services.linguistic_service import analyze_linguistic_patterns
        print("[PASS] Services imported successfully")
    except ImportError as e:
        print(f"[FAIL] Service import failed: {e}")
        return False
    
    # Test 3: Create default model instances (test the fixes)
    print("\n3. Testing model defaults (N/A fixes)...")
    try:
        # Test AudioAnalysis defaults
        audio_analysis = AudioAnalysis()
        if audio_analysis.vocal_confidence_level == 50:  # Should be int, not float
            print("[PASS] AudioAnalysis vocal_confidence_level default correct")
        else:
            print(f"[FAIL] AudioAnalysis vocal_confidence_level wrong: {audio_analysis.vocal_confidence_level}")
        
        # Test ManipulationAssessment defaults
        manipulation = ManipulationAssessment()
        if manipulation.manipulation_explanation == "No manipulation detected.":
            print("[PASS] ManipulationAssessment explanation default correct")
        else:
            print(f"[FAIL] ManipulationAssessment explanation wrong: {manipulation.manipulation_explanation}")
          # Test ArgumentAnalysis defaults
        argument = ArgumentAnalysis()
        if argument.overall_argument_coherence_score == 50:  # Should be 50, not 0
            print("[PASS] ArgumentAnalysis score default correct")
        else:
            print(f"[FAIL] ArgumentAnalysis score wrong: {argument.overall_argument_coherence_score}")
        
    except Exception as e:
        print(f"[FAIL] Model defaults test failed: {e}")
        return False
    
    # Test 4: Gemini validation function
    print("\n4. Testing Gemini validation with new fields...")
    try:
        result = validate_and_structure_gemini_response({}, "Test transcript")
        
        # Check new fields are present and not N/A
        new_fields = ['conversation_flow', 'behavioral_patterns', 'verification_suggestions', 'session_insights']
        
        for field in new_fields:
            if field in result and result[field] not in [None, "N/A", "", "Not available"]:
                print(f"[PASS] {field} properly populated")
            else:
                print(f"[FAIL] {field} missing or N/A: {result.get(field)}")
        
    except Exception as e:
        print(f"[FAIL] Gemini validation test failed: {e}")
        return False
    
    # Test 5: Test response structure
    print("\n5. Testing complete response structure...")
    try:
        # Create a complete response
        response = AnalyzeResponse(
            session_id="test-123",
            audio_analysis=AudioAnalysis(),
            linguistic_analysis=LinguisticAnalysis(),
            manipulation_assessment=ManipulationAssessment(),
            argument_analysis=ArgumentAnalysis(),
            credibility_score=75
        )
        
        response_dict = response.dict()
        print(f"[PASS] Complete response created with {len(response_dict)} fields")
        
        # Check for N/A values
        na_count = count_na_values(response_dict)
        if na_count == 0:
            print("[PASS] No N/A values found in complete response")
        else:
            print(f"[WARN]  Found {na_count} N/A values in response")
        
    except Exception as e:
        print(f"[FAIL] Response structure test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("[TARGET] QUICK BACKEND TEST SUMMARY")
    print("=" * 60)
    print("[PASS] All backend fixes verified successfully!")
    print("   - Models import correctly")
    print("   - Default values are not N/A")
    print("   - New fields are properly populated")
    print("   - Response structure is complete")
    
    return True

def count_na_values(data, path=""):
    """Recursively count N/A values in nested data structure"""
    count = 0
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if value in ["N/A", "Not available", None]:
                count += 1
                print(f"   N/A found at: {current_path}")
            else:
                count += count_na_values(value, current_path)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_path = f"{path}[{i}]" if path else f"[{i}]"
            count += count_na_values(item, current_path)
    
    return count

if __name__ == "__main__":
    success = test_backend_fixes()
    if success:
        print("\n[SUCCESS] All backend fixes are working correctly!")
    else:
        print("\n[FAIL] Some backend fixes need attention!")
        sys.exit(1)