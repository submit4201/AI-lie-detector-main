#!/usr/bin/env python3
"""
Debug script to check the data structure being returned by the API
"""

import json
import requests
import os
import sys
sys.path.append('backend')
from services.gemini_service import validate_and_structure_gemini_response

def test_api_response():
    """Test the API response to see what data structure is being returned"""
    
    # Use the test audio file
    audio_file = r"H:\New folder\PAPAPAPEAPA\Documents\Videos\Deceptive\trial_lie_009.mp3"
    
    if not os.path.exists(audio_file):
        print(f"Audio file {audio_file} not found. Creating a dummy request to check data structure.")
        # Let's check the test endpoint instead
        try:
            response = requests.get("http://localhost:8001/test-structured-output")
            if response.status_code == 200:
                data = response.json()
                print("=== TEST STRUCTURED OUTPUT ===")
                print(json.dumps(data, indent=2))
                
                # Check for missing fields
                check_missing_fields(data)
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Could not connect to API: {e}")
        return
    
    # Test with actual audio file
    try:
        url = "http://localhost:8001/analyze"
        with open(audio_file, 'rb') as f:
            files = {'audio': f}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("=== ACTUAL API RESPONSE ===")
            print(json.dumps(data, indent=2))
            
            # Check for missing fields
            check_missing_fields(data)
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error testing API: {e}")

def check_missing_fields(data):
    """Check for missing or null fields in the data structure"""
    print("\n=== FIELD ANALYSIS ===")
    
    # List of fields that should be present and not null/empty
    expected_fields = {
        'session_insights': ['consistency_analysis', 'behavioral_evolution', 'risk_trajectory', 'conversation_dynamics'],
        'manipulation_assessment': ['manipulation_tactics', 'example_phrases'],
        'speaker_attitude': ['tone_indicators_respect_sarcasm'],
        'quantitative_metrics': ['hesitation_rate'],
        'conversation_flow': None,
        'behavioral_patterns': None,
        'verification_suggestions': None,
        'linguistic_analysis': ['hesitation_rate']
    }
    
    print("Checking for missing or null fields:")
    
    for field, subfields in expected_fields.items():
        if field not in data:
            print(f"[FAIL] Missing field: {field}")
        elif data[field] is None:
            print(f"[FAIL] Null field: {field}")
        elif subfields:
            if isinstance(data[field], dict):
                for subfield in subfields:
                    if subfield not in data[field]:
                        print(f"[FAIL] Missing subfield: {field}.{subfield}")
                    elif data[field][subfield] is None:
                        print(f"[FAIL] Null subfield: {field}.{subfield}")
                    elif isinstance(data[field][subfield], list) and len(data[field][subfield]) == 0:
                        print(f"[WARN]  Empty array: {field}.{subfield}")
                    else:
                        print(f"[PASS] OK: {field}.{subfield}")
            else:
                print(f"[FAIL] Field {field} is not a dict as expected: {type(data[field])}")
        else:
            print(f"[PASS] OK: {field}")

if __name__ == "__main__":
    test_api_response()
