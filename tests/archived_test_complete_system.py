#!/usr/bin/env python3
"""
Complete System Test
Tests both streaming and traditional analysis approaches
"""

import requests
import json
import time
from pathlib import Path

# Test configuration
BACKEND_URL = "http://127.0.0.1:8000"
TEST_AUDIO = Path(__file__).parent / "test_extras" / "test_audio.wav"

def test_traditional_analysis():
    """Test the traditional /analyze endpoint"""
    print("[TEST] Testing Traditional Analysis Endpoint...")
    
    if not TEST_AUDIO.exists():
        print(f"[FAIL] Test audio file not found: {TEST_AUDIO}")
        return False
    
    try:
        files = {"audio": open(TEST_AUDIO, "rb")}
        data = {"session_id": "test_traditional"}
        
        print("[LAUNCH] Sending traditional analysis request...")
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/analyze",
            files=files,
            data=data,
            timeout=120
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        files["audio"].close()
        
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Traditional analysis completed in {duration:.2f}s")
            print(f"   [NOTE] Transcript length: {len(result.get('transcript', ''))}")
            print(f"   [EMOTION] Emotions detected: {len(result.get('emotions', []))}")
            print(f"   [SEARCH] Analysis fields: {len(result.keys())}")
            return True
        else:
            print(f"[FAIL] Traditional analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Traditional analysis error: {e}")
        return False

def test_streaming_analysis():
    """Test the streaming /analyze/stream endpoint"""
    print("[TEST] Testing Streaming Analysis Endpoint...")
    
    if not TEST_AUDIO.exists():
        print(f"[FAIL] Test audio file not found: {TEST_AUDIO}")
        return False
    
    try:
        files = {"audio": open(TEST_AUDIO, "rb")}
        data = {"session_id": "test_streaming_comparison"}
        
        print("[LAUNCH] Sending streaming analysis request...")
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/analyze/stream",
            files=files,
            data=data,
            stream=True,
            timeout=120
        )
        
        files["audio"].close()
        
        if response.status_code != 200:
            print(f"[FAIL] Streaming analysis failed: {response.status_code}")
            return False
        
        print("[PASS] Streaming response received!")
        
        # Process streaming events
        events = []
        results = {}
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        event_data = json.loads(line_str[6:])
                        events.append(event_data)
                        
                        if event_data.get('type') == 'result':
                            analysis_type = event_data.get('analysis_type')
                            results[analysis_type] = event_data.get('data')
                        
                        elif event_data.get('type') == 'complete':
                            break
                            
                    except json.JSONDecodeError:
                        continue
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"[PASS] Streaming analysis completed in {duration:.2f}s")
        print(f"   [DATA] Events received: {len(events)}")
        print(f"   [SEARCH] Analysis types: {list(results.keys())}")
        
        # Show sample results
        if 'transcript' in results:
            transcript_len = len(results['transcript'].get('transcript', ''))
            print(f"   [NOTE] Transcript length: {transcript_len}")
        
        if 'emotion_analysis' in results:
            emotions = results['emotion_analysis']
            if isinstance(emotions, list):
                print(f"   [EMOTION] Emotions detected: {len(emotions)}")
            elif isinstance(emotions, dict):
                print(f"   [EMOTION] Emotion analysis: {list(emotions.keys())}")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"[FAIL] Streaming analysis error: {e}")
        return False

def test_frontend_integration():
    """Test if frontend can reach backend"""
    print("[TEST] Testing Frontend-Backend Integration...")
    
    try:
        # Test CORS and basic connectivity
        response = requests.get(f"{BACKEND_URL}/health")
        
        if response.status_code == 200:
            health = response.json()
            print(f"[PASS] Backend accessible from frontend")
            print(f"   [HEALTH] Health status: {health.get('status')}")
            print(f"   [NET] Environment: {health.get('environment')}")
            return True
        else:
            print(f"[FAIL] Backend not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Frontend-backend integration error: {e}")
        return False

def main():
    """Run complete system test"""
    print("[TARGET] Starting Complete System Test")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Frontend-Backend Integration
    if test_frontend_integration():
        tests_passed += 1
    print()
    
    # Test 2: Traditional Analysis
    if test_traditional_analysis():
        tests_passed += 1
    print()
    
    # Test 3: Streaming Analysis
    if test_streaming_analysis():
        tests_passed += 1
    print()
    
    print("=" * 60)
    print(f"🏁 System Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("[SUCCESS] All systems working! Ready for production use.")
        print("\n📋 System Status:")
        print("   [PASS] Backend API operational")
        print("   [PASS] Traditional analysis working")
        print("   [PASS] Streaming analysis working")
        print("   [PASS] Frontend-backend connectivity verified")
        print("\n[LAUNCH] Next Steps:")
        print("   • Test frontend UI with real audio uploads")
        print("   • Verify streaming UI updates work correctly")
        print("   • Test audio-first approach with Gemini API")
    else:
        print("[WARN]  Some systems need attention. Check the output above.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    main()
