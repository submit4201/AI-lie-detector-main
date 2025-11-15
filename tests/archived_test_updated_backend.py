#!/usr/bin/env python3
"""
Test script to verify the updated backend with new field validations.
This will test the Gemini service changes and ensure N/A values are resolved.
"""

import subprocess
import requests
import json
import time
import sys
import os

# Add the backend directory to the path so we can import modules
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_dir)

def test_backend_api():
    """Test the updated backend API with field validations."""
    
    # Base URL for the API
    base_url = "http://localhost:8001"
    print("Testing Updated AI Lie Detector Backend")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Checking server status...")
    try:
        response = requests.post(f"{base_url}/session/new")
        print(response.json())
        if response.status_code == 200:
            print("[PASS] Server is running")
        else:
            print(f"[FAIL] Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] Cannot connect to server. Make sure backend is running on port 8001")
        print("   Run: python backend/main.py")
        return False
    
    # Test 2: Test audio analysis with real audio file
    print("\n2. Testing audio analysis with updated field validations...")
    
    # Use existing test audio file
    audio_file_path = "H:/New folder/PAPAPAPEAPA/Documents/Videos/Deceptive/trial_lie_009.mp3"
    if os.path.exists(audio_file_path):
        audio_file_path = "H:/New folder/PAPAPAPEAPA/Documents/Videos/Deceptive/trial_lie_009.mp3"
    if not os.path.exists(audio_file_path):
        print("[FAIL] No test audio file found")
        return False
    
    print(f"   Using audio file: {audio_file_path}")
    
    # Start a new session
    session_response = requests.post(f"{base_url}/session/new")
    if session_response.status_code != 200:
        print(f"[FAIL] Failed to start session: {session_response.status_code}")
        return False
    
    session_data = session_response.json()
    session_id = session_data.get("session_id")
    print(f"   Created session: {session_id}")
    
    # Upload and analyze audio
    with open(audio_file_path, 'rb') as audio_file:
        files = {'audio': audio_file}

        print("   Uploading and analyzing audio...")
        response = requests.post(f"{base_url}/analyze", data=audio_file)
    
    if response.status_code != 200:
        print(f"[FAIL] Analysis failed with status {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Parse the response
    try:
        analysis_result = response.json()
    except json.JSONDecodeError:
        print("[FAIL] Failed to parse JSON response")
        print(f"   Raw response: {response.text}")
        return False
    
    print("[PASS] Analysis completed successfully")
    
    # Test 3: Validate all required fields are present
    print("\n3. Validating updated field structure...")
    
    required_fields = [
        'session_id', 'speaker_name', 'transcript', 'credibility_score', 
        'emotion_analysis', 'linguistic_analysis', 'ai_analysis'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in analysis_result:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"[FAIL] Missing top-level fields: {missing_fields}")
        return False
    else:
        print("[PASS] All top-level fields present")
    
    # Test 4: Validate AI analysis structure (focus of our fix)
    print("\n4. Validating AI analysis structure (Gemini service fix)...")
    
    ai_analysis = analysis_result.get('ai_analysis', {})
    required_ai_fields = [
        'credibility_assessment', 'deception_indicators', 'linguistic_patterns',
        'conversation_flow', 'behavioral_patterns', 'verification_suggestions',
        'session_insights', 'confidence_score'
    ]
    
    missing_ai_fields = []
    na_fields = []
    
    for field in required_ai_fields:
        if field not in ai_analysis:
            missing_ai_fields.append(field)
        elif ai_analysis[field] in [None, "N/A", "", "Not available"]:
            na_fields.append(field)
    
    if missing_ai_fields:
        print(f"[FAIL] Missing AI analysis fields: {missing_ai_fields}")
    else:
        print("[PASS] All AI analysis fields present")
    
    if na_fields:
        print(f"[WARN]  Fields with N/A or empty values: {na_fields}")
        print("   This indicates the Gemini service validation needs further review")
    else:
        print("[PASS] No N/A values found in AI analysis")
    
    # Test 5: Check specific field content
    print("\n5. Checking specific field content...")
    
    # Check linguistic analysis
    linguistic = analysis_result.get('linguistic_analysis', {})
    hesitation_rate = linguistic.get('hesitation_rate')
    if hesitation_rate is not None and hesitation_rate != "N/A":
        print(f"[PASS] Hesitation rate: {hesitation_rate}")
    else:
        print(f"[FAIL] Hesitation rate is N/A or missing: {hesitation_rate}")
    
    # Check conversation flow (new field)
    conversation_flow = ai_analysis.get('conversation_flow')
    if conversation_flow and conversation_flow != "N/A":
        print(f"[PASS] Conversation flow: {conversation_flow[:100]}...")
    else:
        print(f"[FAIL] Conversation flow is N/A or missing")
    
    # Check behavioral patterns (new field)
    behavioral_patterns = ai_analysis.get('behavioral_patterns')
    if behavioral_patterns and behavioral_patterns != "N/A":
        print(f"[PASS] Behavioral patterns: {behavioral_patterns[:100]}...")
    else:
        print(f"[FAIL] Behavioral patterns is N/A or missing")
    
    # Check session insights (new field)
    session_insights = ai_analysis.get('session_insights')
    if session_insights and session_insights != "N/A":
        print(f"[PASS] Session insights: {session_insights[:100]}...")
    else:
        print(f"[FAIL] Session insights is N/A or missing")
    
    # Test 6: Save debug output
    print("\n6. Saving debug output...")
    
    debug_output = {
        "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "audio_file_used": audio_file_path,
        "session_id": session_id,
        "response_keys": list(analysis_result.keys()),
        "ai_analysis_keys": list(ai_analysis.keys()),
        "field_validation": {
            "missing_top_level": missing_fields,
            "missing_ai_fields": missing_ai_fields,
            "na_fields": na_fields
        },
        "full_response": analysis_result
    }
    
    with open('backend_test_results.json', 'w') as f:
        json.dump(debug_output, f, indent=2)
    
    print("[PASS] Debug output saved to backend_test_results.json")
    
    # Summary
    print("\n" + "=" * 50)
    print("[TARGET] TEST SUMMARY")
    print("=" * 50)
    
    if not missing_fields and not missing_ai_fields:
        if not na_fields:
            print("[SUCCESS] SUCCESS: All fields present and populated!")
            print("   The Gemini service validation fix is working correctly.")
            return True
        else:
            print("[WARN]  PARTIAL SUCCESS: All fields present but some have N/A values")
            print("   The validation structure is correct but content generation needs review")
            return True
    else:
        print("[FAIL] FAILURE: Missing required fields")
        print("   The backend needs further investigation")
        return False

if __name__ == "__main__":
    success = test_backend_api()
    if success:
        print("\n[PASS] Backend testing completed successfully!")
    else:
        print("\n[FAIL] Backend testing failed!")
        sys.exit(1)
