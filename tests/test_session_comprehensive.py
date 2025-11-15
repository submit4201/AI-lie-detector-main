#!/usr/bin/env python3
"""
Comprehensive test for session creation with real audio file.
"""

import requests
import json
import os

def test_full_session_workflow():
    """Test complete session workflow with real audio"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Complete Session Workflow")
    print("=" * 50)
    
    # Find a suitable audio file
    audio_files = [
        "p:\\python\\New folder (2)\\tests\\test_extras\\Recording.wav",
        "p:\\python\\New folder (2)\\tests\\test_extras\\5.wav",
        "p:\\python\\New folder (2)\\tests\\test_extras\\test_audio.wav"
    ]
    
    audio_file = None
    for file_path in audio_files:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:  # At least 1KB
            audio_file = file_path
            break
    
    if not audio_file:
        print("❌ No suitable audio file found for testing")
        return False
    
    print(f"✅ Using audio file: {audio_file}")
    print(f"   File size: {os.path.getsize(audio_file)} bytes")
    
    # Test 1: Create session
    print("\n1. Creating new session...")
    try:
        session_response = requests.post(f"{base_url}/session/new")
        if session_response.status_code == 200:
            session_data = session_response.json()
            session_id = session_data.get("session_id")
            print(f"✅ Session created: {session_id}")
        else:
            print(f"❌ Session creation failed: {session_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return False
    
    # Test 2: Upload and analyze
    print("\n2. Uploading audio for analysis...")
    try:
        with open(audio_file, "rb") as f:
            files = {"audio": ("test.wav", f, "audio/wav")}
            data = {"session_id": session_id}
            
            print("   Sending analysis request...")
            response = requests.post(f"{base_url}/analyze", files=files, data=data, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Analysis completed successfully!")
                
                # Check key components
                print(f"   Session ID: {result.get('session_id', 'Missing')}")
                print(f"   Transcript length: {len(result.get('transcript', ''))}")
                print(f"   Emotions detected: {len(result.get('emotion_analysis', []))}")
                print(f"   Credibility score: {result.get('credibility_score', 'Missing')}")
                
                # Check if we have the session creation error
                if 'error' in result and 'session' in result['error'].lower():
                    print(f"❌ Session error still present: {result['error']}")
                    return False
                
                return True
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                print(f"   Response: {response.text[:300]}...")
                
                # Check if this is the session error
                if 'session' in response.text.lower():
                    print("❌ Session-related error detected!")
                
                return False
                
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def check_backend_logs():
    """Check for any session-related errors in backend"""
    print("\n3. Checking for session-related issues...")
    
    try:
        # Test session service directly
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            print("✅ Backend health check passed")
        else:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Comprehensive Session Creation Test")
    print("Checking if the emotion analysis fix resolved session issues...")
    
    success = True
    success &= check_backend_logs()
    success &= test_full_session_workflow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS! Session creation and upload working correctly!")
        print("✅ The emotion analysis fix appears to have resolved the session issue.")
    else:
        print("❌ Session creation issues still exist.")
        print("Need to investigate further...")
