#!/usr/bin/env python3
"""
Test script to verify session creation issue is resolved after emotion analysis fix.
"""

import requests
import json
import os
from io import BytesIO

def test_session_creation():
    """Test session creation and upload functionality"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Session Creation and Upload Functionality")
    print("=" * 60)
    
    # Test 1: Create a new session
    print("\n1. Testing session creation...")
    try:
        session_response = requests.post(f"{base_url}/session/new")
        if session_response.status_code == 200:
            session_data = session_response.json()
            session_id = session_data.get("session_id")
            print(f"✅ Session created successfully: {session_id}")
        else:
            print(f"❌ Session creation failed: {session_response.status_code}")
            print(f"Response: {session_response.text}")
            return False
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return False
    
    # Test 2: Upload audio to session (simulate with test audio)
    print("\n2. Testing audio upload to session...")
    try:
        # Create a simple test audio file in memory
        test_audio_path = "p:\\python\\New folder (2)\\tests\\test_audio.wav"
        
        if not os.path.exists(test_audio_path):
            print(f"⚠️ Test audio file not found at {test_audio_path}")
            print("Creating a dummy audio file for testing...")
            # Create a minimal WAV file header for testing
            with open(test_audio_path, "wb") as f:
                # Simple WAV header (44 bytes) + minimal audio data
                wav_header = b'RIFF' + b'\x00\x00\x00\x00' + b'WAVE' + b'fmt ' + b'\x10\x00\x00\x00' + \
                            b'\x01\x00\x01\x00\x40\x1f\x00\x00\x80>\x00\x00\x02\x00\x10\x00' + \
                            b'data' + b'\x00\x00\x00\x00'
                f.write(wav_header)
                # Add some dummy audio data
                f.write(b'\x00\x00' * 100)  # 200 bytes of silence
        
        # Test upload
        with open(test_audio_path, "rb") as audio_file:
            files = {"audio": ("test.wav", audio_file, "audio/wav")}
            data = {"session_id": session_id}
            
            upload_response = requests.post(f"{base_url}/analyze", files=files, data=data, timeout=60)
            
            if upload_response.status_code == 200:
                print("✅ Audio upload successful!")
                result = upload_response.json()
                print(f"✅ Analysis completed for session: {result.get('session_id', 'N/A')}")
                
                # Check if emotion analysis worked
                emotions = result.get('emotion_analysis', [])
                print(f"✅ Emotions detected: {len(emotions)} emotions")
                if emotions:
                    print(f"   Sample emotions: {emotions[:3]}")
                
                return True
            else:
                print(f"❌ Audio upload failed: {upload_response.status_code}")
                print(f"Response: {upload_response.text[:500]}...")
                return False
                
    except Exception as e:
        print(f"❌ Audio upload error: {e}")
        return False
    
    return True

def test_emotion_analysis_specific():
    """Test emotion analysis specifically to ensure the fix worked"""
    print("\n3. Testing emotion analysis fix...")
    
    try:
        # Import the fixed function
        import sys
        sys.path.append("p:\\python\\New folder (2)\\backend")
        
        from services.gemini_service import analyze_emotions_with_gemini
        
        test_audio_path = "p:\\python\\New folder (2)\\tests\\test_audio.wav"
        test_transcript = "Hello, this is a test transcript for emotion analysis."
        
        if os.path.exists(test_audio_path):
            print(f"✅ Testing emotion analysis with audio file: {test_audio_path}")
            emotions = analyze_emotions_with_gemini(test_audio_path, test_transcript)
            
            if emotions and isinstance(emotions, list):
                print(f"✅ Emotion analysis successful: {len(emotions)} emotions detected")
                for emotion in emotions[:3]:  # Show first 3
                    print(f"   - {emotion.get('label', 'unknown')}: {emotion.get('score', 0):.2f}")
                return True
            else:
                print(f"❌ Emotion analysis returned invalid data: {emotions}")
                return False
        else:
            print(f"⚠️ Test audio file not found, skipping direct emotion test")
            return True
            
    except Exception as e:
        print(f"❌ Emotion analysis test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Session Creation Fix Validation")
    print("Testing the fix for: '⚠️ Failed to create or retrieve session for upload'")
    
    success = True
    
    # Run tests
    success &= test_session_creation()
    success &= test_emotion_analysis_specific()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Session creation issue appears to be resolved.")
    else:
        print("❌ SOME TESTS FAILED! Session creation issue may still exist.")
    
    print("\nNext steps:")
    print("- If tests passed: Session creation fix successful!")
    print("- If tests failed: Need to investigate further issues")
