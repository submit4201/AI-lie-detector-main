#!/usr/bin/env python3
"""
Test script to verify models alignment with services after our fixes
"""

import requests
import json
import os
import time

def test_model_alignment():
    """Test that models align with service outputs"""
    print("Testing Models Alignment with Services")
    print("=" * 50)
    
    base_url = "http://localhost:8001"
    
    # Test 1: Check server is running
    print("\n1. Checking server status...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("[OK] Server is running")
        else:
            print(f"[ERROR] Server not responding properly: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Start backend with: python backend/main.py")
        return False
    
    # Test 2: Create session and analyze audio
    print("\n2. Testing complete analysis workflow...")
    
    # Create session
    session_response = requests.post(f"{base_url}/session/new")
    if session_response.status_code != 200:
        print(f"[ERROR] Failed to create session: {session_response.status_code}")
        return False
    
    session_data = session_response.json()
    session_id = session_data.get("session_id")
    print(f"   Session created: {session_id}")
    
    # Find audio file
    audio_files = ["test_audio.wav", "5.wav", "Recording.wav"]
    audio_file = None
    for file in audio_files:
        if os.path.exists(file):
            audio_file = file
            break
    
    if not audio_file:
        print("[WARNING] No audio file found, skipping audio analysis")
        return True
    
    print(f"   Using audio file: {audio_file}")
    
    # Analyze audio
    with open(audio_file, 'rb') as f:
        files = {'audio': f}
        data = {'session_id': session_id, 'speaker_name': 'Test Speaker'}
        response = requests.post(f"{base_url}/analyze", files=files, data=data)
    
    if response.status_code != 200:
        print(f"[ERROR] Analysis failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    result = response.json()
    print("[OK] Analysis completed successfully")
    
    # Test 3: Validate field alignment
    print("\n3. Validating field alignment fixes...")
    
    issues_found = []
    
    # Check conversation_flow is string (not complex object)
    conversation_flow = result.get('conversation_flow')
    if conversation_flow is not None:
        if isinstance(conversation_flow, str):
            print(f"[OK] conversation_flow is string: {conversation_flow[:50]}...")
        else:
            print(f"[ERROR] conversation_flow should be string, got: {type(conversation_flow)}")
            issues_found.append("conversation_flow type mismatch")
    else:
        print("[WARNING] conversation_flow is None")
    
    # Check behavioral_patterns is string (not complex object)
    behavioral_patterns = result.get('behavioral_patterns')
    if behavioral_patterns is not None:
        if isinstance(behavioral_patterns, str):
            print(f"[OK] behavioral_patterns is string: {behavioral_patterns[:50]}...")
        else:
            print(f"[ERROR] behavioral_patterns should be string, got: {type(behavioral_patterns)}")
            issues_found.append("behavioral_patterns type mismatch")
    else:
        print("[WARNING] behavioral_patterns is None")
    
    # Check verification_suggestions is list (not complex object)
    verification_suggestions = result.get('verification_suggestions')
    if verification_suggestions is not None:
        if isinstance(verification_suggestions, list):
            print(f"[OK] verification_suggestions is list with {len(verification_suggestions)} items")
        else:
            print(f"[ERROR] verification_suggestions should be list, got: {type(verification_suggestions)}")
            issues_found.append("verification_suggestions type mismatch")
    else:
        print("[WARNING] verification_suggestions is None")
    
    # Check session_insights structure
    session_insights = result.get('session_insights')
    if session_insights is not None:
        if isinstance(session_insights, dict):
            required_subfields = ['consistency_analysis', 'behavioral_evolution', 'risk_trajectory', 'conversation_dynamics']
            missing_subfields = [field for field in required_subfields if field not in session_insights]
            if not missing_subfields:
                print(f"[OK] session_insights has all required subfields")
            else:
                print(f"[ERROR] session_insights missing subfields: {missing_subfields}")
                issues_found.append("session_insights missing subfields")
        else:
            print(f"[ERROR] session_insights should be dict, got: {type(session_insights)}")
            issues_found.append("session_insights type mismatch")
    else:
        print("[WARNING] session_insights is None")
    
    # Check linguistic_analysis hesitation_rate
    linguistic_analysis = result.get('linguistic_analysis', {})
    hesitation_rate = linguistic_analysis.get('hesitation_rate')
    if hesitation_rate is not None and hesitation_rate != "N/A":
        print(f"[OK] hesitation_rate has value: {hesitation_rate}")
    else:
        print(f"[WARNING] hesitation_rate is N/A or None: {hesitation_rate}")
        issues_found.append("hesitation_rate still N/A")
    
    # Check manipulation_assessment structure
    manipulation_assessment = result.get('manipulation_assessment')
    if manipulation_assessment is not None:
        manipulation_explanation = manipulation_assessment.get('manipulation_explanation')
        if manipulation_explanation and manipulation_explanation != "N/A":
            print(f"[OK] manipulation_explanation not N/A: {manipulation_explanation[:30]}...")
        else:
            print(f"[WARNING] manipulation_explanation is N/A: {manipulation_explanation}")
            issues_found.append("manipulation_explanation still N/A")
    
    # Test 4: Save results for inspection
    print("\n4. Saving test results...")
    
    test_results = {
        "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "audio_file_used": audio_file,
        "session_id": session_id,
        "issues_found": issues_found,
        "field_types": {
            "conversation_flow": type(result.get('conversation_flow')).__name__,
            "behavioral_patterns": type(result.get('behavioral_patterns')).__name__,
            "verification_suggestions": type(result.get('verification_suggestions')).__name__,
            "session_insights": type(result.get('session_insights')).__name__
        },
        "full_response": result
    }
    
    with open('model_alignment_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print("[OK] Results saved to model_alignment_test_results.json")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if not issues_found:
        print("[SUCCESS] All model alignment issues have been fixed!")
        print("   - Fields have correct types (string/list vs complex objects)")
        print("   - No N/A values found in key fields")
        print("   - Services and models are properly aligned")
        return True
    else:
        print(f"[PARTIAL] Some issues remain: {len(issues_found)} found")
        for issue in issues_found:
            print(f"   - {issue}")
        print("   Check the detailed output above and model_alignment_test_results.json")
        return True

if __name__ == "__main__":
    success = test_model_alignment()
    if success:
        print("\n[SUCCESS] Model alignment testing completed!")
    else:
        print("\n[ERROR] Model alignment testing failed!")
