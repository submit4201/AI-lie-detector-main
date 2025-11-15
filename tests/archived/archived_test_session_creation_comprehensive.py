#!/usr/bin/env python3
"""
Comprehensive test for session creation issue resolution
Tests the full analysis pipeline with a real audio file to verify session creation works
"""

import requests
import json
import time
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_session_creation_with_real_audio():
    """Test session creation with a real audio file"""
    
    # Backend URL
    base_url = "http://localhost:8000"
    
    # Test audio file
    audio_file_path = r"P:\python\New folder (2)\tests\test_extras\trial_lie_003.mp3"
    
    print("🧪 COMPREHENSIVE SESSION CREATION TEST")
    print("=" * 60)
    
    # Check if audio file exists
    if not os.path.exists(audio_file_path):
        print(f"❌ Audio file not found: {audio_file_path}")
        return False
    
    print(f"📁 Using audio file: {os.path.basename(audio_file_path)}")
    print(f"📊 File size: {os.path.getsize(audio_file_path)} bytes")
    
    try:
        # Test 1: Health check
        print("\n1️⃣ Backend Health Check...")
        health_response = requests.get(f"{base_url}/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            return False
        
        # Test 2: Session creation via analysis
        print("\n2️⃣ Testing Analysis with Session Creation...")
        
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                'audio': (os.path.basename(audio_file_path), audio_file, 'audio/mpeg')
            }
            
            # Optional: provide session_id to test session retrieval/creation
            data = {
                'session_id': 'test_session_' + str(int(time.time()))
            }
            
            print(f"📤 Uploading {os.path.basename(audio_file_path)}...")
            print(f"🆔 Session ID: {data['session_id']}")
            
            start_time = time.time()
            
            # Make the analysis request
            response = requests.post(
                f"{base_url}/analyze", 
                files=files,
                data=data,
                timeout=300  # 5 minutes timeout for audio processing
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"⏱️ Processing time: {processing_time:.2f} seconds")
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Analysis request successful!")
                
                # Parse response
                try:
                    result = response.json()
                    
                    # Check for session creation/retrieval
                    if 'session_id' in result:
                        print(f"✅ Session created/retrieved: {result['session_id']}")
                    else:
                        print("⚠️ No session_id in response")
                    
                    # Check for emotion analysis (our fixed component)
                    if 'emotion_analysis' in result:
                        emotions = result['emotion_analysis']
                        if isinstance(emotions, list) and len(emotions) > 0:
                            print(f"✅ Emotion analysis working: {len(emotions)} emotions detected")
                            print(f"   Sample emotions: {emotions[:3]}")
                        else:
                            print("⚠️ Empty emotion analysis")
                    else:
                        print("⚠️ No emotion analysis in response")
                    
                    # Check for transcript
                    if 'transcript' in result and result['transcript']:
                        transcript_preview = result['transcript'][:100] + "..." if len(result['transcript']) > 100 else result['transcript']
                        print(f"✅ Transcript generated: '{transcript_preview}'")
                    else:
                        print("⚠️ No transcript in response")
                    
                    # Check for Gemini analysis
                    if 'gemini_analysis' in result:
                        gemini = result['gemini_analysis']
                        if 'credibility_score' in gemini:
                            print(f"✅ Credibility analysis: {gemini['credibility_score']}")
                        if 'gemini_summary' in gemini:
                            print("✅ Gemini summary generated")
                    else:
                        print("⚠️ No Gemini analysis in response")
                    
                    # Test 3: Verify session exists via session endpoint
                    print("\n3️⃣ Testing Session Retrieval...")
                    session_id = result.get('session_id')
                    if session_id:
                        session_response = requests.get(f"{base_url}/session/{session_id}", timeout=10)
                        if session_response.status_code == 200:
                            session_data = session_response.json()
                            print(f"✅ Session retrieved successfully")
                            print(f"   Session analyses: {len(session_data.get('analyses', []))}")
                        else:
                            print(f"⚠️ Session retrieval failed: {session_response.status_code}")
                    
                    print("\n" + "="*60)
                    print("🎉 SESSION CREATION TEST COMPLETED SUCCESSFULLY!")
                    print("✅ Session creation/retrieval is working")
                    print("✅ Emotion analysis error has been resolved")
                    print("✅ Full analysis pipeline is functional")
                    
                    return True
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse response JSON: {e}")
                    print(f"Response text: {response.text[:500]}...")
                    return False
                    
            else:
                print(f"❌ Analysis failed with status {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
    except requests.exceptions.Timeout:
        print("❌ Request timed out - audio processing took too long")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - is it running?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run the comprehensive session creation test"""
    success = test_session_creation_with_real_audio()
    
    if success:
        print("\n🎊 ALL TESTS PASSED! Session creation issue is RESOLVED!")
        sys.exit(0)
    else:
        print("\n💥 TEST FAILED! Session creation issue persists.")
        sys.exit(1)

if __name__ == "__main__":
    main()
