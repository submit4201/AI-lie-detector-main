#!/usr/bin/env python3
"""
Simple Streaming Test
Quick test to validate streaming functionality is working
"""

import sys
import os
import requests
import json
import time
from pathlib import Path

# Test configuration
BACKEND_URL = "http://127.0.0.1:8000"  # Updated to match the running server
TEST_AUDIO = Path(__file__).parent / "test_extras" / "test_audio.wav"

def test_streaming_endpoint():
    """Test the streaming analysis endpoint"""
    print("[TEST] Testing Streaming Analysis Endpoint...")
    
    # Check if audio file exists
    if not TEST_AUDIO.exists():
        print(f"[FAIL] Test audio file not found: {TEST_AUDIO}")
        return False
    
    print(f"[FILE] Using test audio: {TEST_AUDIO}")
    
    try:
        # Test streaming endpoint
        files = {"audio": open(TEST_AUDIO, "rb")}
        data = {"session_id": "test_streaming_simple"}
        
        print("[LAUNCH] Sending streaming request...")
        response = requests.post(
            f"{BACKEND_URL}/analyze/stream",
            files=files,
            data=data,
            stream=True,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"[FAIL] Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print("[PASS] Streaming response received!")
        print("[DATA] Processing streaming data...")
        
        # Process streaming response
        events_received = 0
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                        events_received += 1
                        
                        event_type = data.get('type', 'unknown')
                        print(f"  [MSG] Event {events_received}: {event_type}")
                        
                        if event_type == 'progress':
                            step = data.get('step', 'unknown')
                            progress = data.get('progress', 0)
                            total = data.get('total', 0)
                            print(f"    [PROGRESS] Progress: {step} ({progress}/{total})")
                        
                        elif event_type == 'result':
                            analysis_type = data.get('analysis_type', 'unknown')
                            print(f"    [MAGIC] Result: {analysis_type}")
                        
                        elif event_type == 'error':
                            message = data.get('message', 'Unknown error')
                            print(f"    [WARN]  Error: {message}")
                        
                        elif event_type == 'complete':
                            print(f"    [SUCCESS] Analysis Complete!")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"    [WARN]  Failed to parse JSON: {e}")
                        
        print(f"[PASS] Streaming test completed! Received {events_received} events")
        return events_received > 0
        
    except Exception as e:
        print(f"[FAIL] Streaming test failed: {e}")
        return False
    finally:
        files["audio"].close()

def test_health_endpoint():
    """Test health endpoint"""
    print("[TEST] Testing Health Endpoint...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"[PASS] Backend is healthy: {health_data['status']}")
            print(f"   [TOOL] Services: {', '.join(health_data.get('services', {}).keys())}")
            return True
        else:
            print(f"[FAIL] Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Health check error: {e}")
        return False

def main():
    """Run all streaming tests"""
    print("[TARGET] Starting Simple Streaming Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Health check
    if test_health_endpoint():
        tests_passed += 1
    
    print()
    
    # Test 2: Streaming functionality
    if test_streaming_endpoint():
        tests_passed += 1
    
    print()
    print("=" * 50)
    print(f"🏁 Tests Completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("[SUCCESS] All tests passed! Streaming is working correctly.")
        return True
    else:
        print("[WARN]  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    main()
