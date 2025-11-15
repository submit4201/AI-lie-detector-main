#!/usr/bin/env python3
"""
Test script to validate the complete backend workflow with a real audio file.
This will test the entire pipeline from audio upload to final analysis results.
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
AUDIO_FILE_PATH = "tests/test_extras/test_audio.mp3"

def test_complete_workflow():
    print("=" * 60)
    print("TESTING COMPLETE BACKEND WORKFLOW WITH REAL AUDIO FILE")
    print("=" * 60)
    
    # Check if audio file exists
    audio_path = Path(AUDIO_FILE_PATH)
    if not audio_path.exists():
        print(f"[FAIL] ERROR: Audio file not found at {AUDIO_FILE_PATH}")
        return False
    
    print(f"[PASS] Audio file found: {audio_path.name} ({audio_path.stat().st_size / 1024 / 1024:.2f} MB)")
    
    try:
        # Step 1: Test backend health
        print("\n📡 Testing backend connection...")
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if health_response.status_code != 200:
            print(f"[FAIL] Backend health check failed: {health_response.status_code}")
            return False
        print("[PASS] Backend is running")
        
        # Step 2: Upload and analyze audio file
        print(f"\n🎵 Uploading and analyzing audio file: {audio_path.name}")
        
        with open(audio_path, 'rb') as audio_file:
            files = {'audio': (audio_path.name, audio_file, 'audio/mpeg')}
            
            print("📤 Sending file to backend...")
            start_time = time.time()
            
            analyze_response = requests.post(
                f"{BACKEND_URL}/analyze",
                files=files,
                timeout=300  # 5 minute timeout for analysis
            )
            
            analysis_time = time.time() - start_time
            print(f"[TIME]  Analysis completed in {analysis_time:.2f} seconds")
        
        if analyze_response.status_code != 200:
            print(f"[FAIL] Analysis failed with status {analyze_response.status_code}")
            print(f"Response: {analyze_response.text}")
            return False
        
        # Step 3: Parse and validate response
        print("\n[DATA] Parsing analysis results...")
        
        try:
            analysis_data = analyze_response.json()
        except json.JSONDecodeError as e:
            print(f"[FAIL] Failed to parse JSON response: {e}")
            print(f"Raw response: {analyze_response.text[:500]}...")
            return False
        
        # Save response for debugging
        with open("real_audio_analysis_results.json", "w") as f:
            json.dump(analysis_data, f, indent=2)
        print("💾 Analysis results saved to real_audio_analysis_results.json")
        
        # Step 4: Validate data structure and check for N/A values
        print("\n[SEARCH] Validating data structure...")
        
        success = True
        na_issues = []
        missing_fields = []
        
        # Check for basic structure
        required_sections = [
            'speaker_transcripts', 'credibility_score', 'confidence_level',
            'gemini_summary', 'linguistic_analysis', 'risk_assessment',
            'manipulation_assessment', 'argument_analysis', 'speaker_attitude',
            'enhanced_understanding', 'session_insights', 'audio_analysis'
        ]
        
        for section in required_sections:
            if section not in analysis_data:
                missing_fields.append(section)
                success = False
            else:
                print(f"[PASS] {section}: Present")
        
        # Check for N/A values recursively
        def check_for_na_values(data, path=""):
            na_found = []
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    if value == "N/A" or (isinstance(value, str) and "N/A" in value):
                        na_found.append(current_path)
                    elif isinstance(value, (dict, list)):
                        na_found.extend(check_for_na_values(value, current_path))
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    current_path = f"{path}[{i}]"
                    if item == "N/A" or (isinstance(item, str) and "N/A" in item):
                        na_found.append(current_path)
                    elif isinstance(item, (dict, list)):
                        na_found.extend(check_for_na_values(item, current_path))
            return na_found
        
        na_issues = check_for_na_values(analysis_data)
        
        # Step 5: Display results summary
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"[NOTE] Transcript available: {'Yes' if analysis_data.get('speaker_transcripts') else 'No'}")
        print(f"[TARGET] Credibility Score: {analysis_data.get('credibility_score', 'N/A')}")
        print(f"🔒 Confidence Level: {analysis_data.get('confidence_level', 'N/A')}")
        print(f"[WARN]  Overall Risk: {analysis_data.get('overall_risk', 'N/A')}")
        
        # Gemini Summary
        gemini_summary = analysis_data.get('gemini_summary', {})
        print(f"\n[BRAIN] Gemini Analysis:")
        print(f"   Tone: {gemini_summary.get('tone', 'N/A')[:50]}...")
        print(f"   Credibility: {gemini_summary.get('credibility', 'N/A')[:50]}...")
        
        # Linguistic Analysis highlights
        linguistic = analysis_data.get('linguistic_analysis', {})
        print(f"\n[PROGRESS] Linguistic Metrics:")
        print(f"   Word Count: {linguistic.get('word_count', 'N/A')}")
        print(f"   Hesitation Count: {linguistic.get('hesitation_count', 'N/A')}")
        print(f"   Formality Score: {linguistic.get('formality_score', 'N/A')}")
        print(f"   Complexity Score: {linguistic.get('complexity_score', 'N/A')}")
        
        # Audio Analysis
        audio_analysis = analysis_data.get('audio_analysis', {})
        print(f"\n🎤 Audio Analysis:")
        print(f"   Vocal Confidence: {audio_analysis.get('vocal_confidence_level', 'N/A')}")
        print(f"   Voice Quality: {audio_analysis.get('voice_quality', 'N/A')[:50]}...")
        
        # Step 6: Report issues
        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)
        
        if missing_fields:
            print(f"[FAIL] Missing fields ({len(missing_fields)}):")
            for field in missing_fields:
                print(f"   - {field}")
            success = False
        else:
            print("[PASS] All required fields present")
        
        if na_issues:
            print(f"\n[WARN]  N/A values found ({len(na_issues)}):")
            for issue in na_issues[:10]:  # Show first 10
                print(f"   - {issue}")
            if len(na_issues) > 10:
                print(f"   ... and {len(na_issues) - 10} more")
            success = False
        else:
            print("[PASS] No N/A values found")
        
        print(f"\n{'[PASS] COMPLETE WORKFLOW TEST PASSED' if success else '[FAIL] COMPLETE WORKFLOW TEST FAILED'}")
        
        return success
        
    except requests.exceptions.ConnectionError:
        print("[FAIL] Could not connect to backend. Make sure it's running on http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("[FAIL] Request timed out. Analysis may be taking too long.")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    exit(0 if success else 1)
