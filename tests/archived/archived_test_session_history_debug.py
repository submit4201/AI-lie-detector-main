#!/usr/bin/env python3
"""
Session History Debug Test
Tests the specific workflow: Analysis Completion → Session History Loading
"""

import requests
import json
import time
import os
from pathlib import Path

def test_session_history_workflow():
    """Test session history loading after analysis completion"""
    base_url = "http://localhost:8000"
    
    print("🔍 SESSION HISTORY DEBUG TEST")
    print("=" * 50)
      # Test audio file path
    audio_file = Path("p:/python/New folder (2)/tests/test_extras/trial_lie_003.mp3")
    
    if not audio_file.exists():
        print(f"❌ Audio file not found: {audio_file}")
        print("   Available files in sample_audio:")
        sample_dir = audio_file.parent
        if sample_dir.exists():
            for f in sample_dir.glob("*"):
                print(f"   - {f.name}")
        return False
    
    # Step 1: Create session
    print("\n1️⃣ Creating new session...")
    try:
        session_response = requests.post(f"{base_url}/session/new")
        if session_response.status_code == 200:
            session_data = session_response.json()
            session_id = session_data.get("session_id")
            print(f"✅ Session created: {session_id}")
        else:
            print(f"❌ Session creation failed: {session_response.status_code}")
            print(f"   Response: {session_response.text}")
            return False
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return False
    
    # Step 2: Run analysis
    print(f"\n2️⃣ Running analysis with session ID: {session_id}")
    try:
        with open(audio_file, "rb") as f:
            files = {"audio": ("test.mp3", f, "audio/mp3")}
            data = {"session_id": session_id}
            
            print("   Sending analysis request...")
            analysis_response = requests.post(f"{base_url}/analyze", files=files, data=data, timeout=120)
            
            if analysis_response.status_code == 200:
                result = analysis_response.json()
                print("✅ Analysis completed successfully!")
                
                # Check key components
                returned_session_id = result.get('session_id')
                print(f"   Returned Session ID: {returned_session_id}")
                print(f"   Original Session ID: {session_id}")
                print(f"   Session ID Match: {returned_session_id == session_id}")
                print(f"   Transcript present: {bool(result.get('transcript'))}")
                print(f"   Credibility score: {result.get('credibility_score', 'Missing')}")
                
                # Check if session data is saved
                if 'session_insights' in result:
                    print("   ✅ Session insights present in response")
                else:
                    print("   ⚠️ No session insights in response (expected for first analysis)")
                
            else:
                print(f"❌ Analysis failed: {analysis_response.status_code}")
                print(f"   Response: {analysis_response.text[:500]}...")
                return False
                
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False
    
    # Step 3: Wait a moment for backend processing
    print(f"\n⏳ Waiting 2 seconds for backend processing...")
    time.sleep(2)
    
    # Step 4: Check session history immediately after analysis
    print(f"\n3️⃣ Loading session history...")
    try:
        history_response = requests.get(f"{base_url}/session/{session_id}/history")
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            history_items = history_data.get('history', [])
            
            print(f"✅ Session history loaded successfully!")
            print(f"   Session ID: {history_data.get('session_id')}")
            print(f"   History items count: {len(history_items)}")
            
            if len(history_items) > 0:
                print(f"   ✅ Session history contains {len(history_items)} item(s)")
                
                # Examine first history item
                first_item = history_items[0]
                print(f"\n📋 First History Item Details:")
                print(f"   Timestamp: {first_item.get('timestamp')}")
                print(f"   Transcript length: {len(first_item.get('transcript', ''))}")
                print(f"   Analysis data: {bool(first_item.get('analysis'))}")
                
                if first_item.get('analysis'):
                    analysis = first_item.get('analysis')
                    print(f"   Credibility score: {analysis.get('credibility_score')}")
                    print(f"   Risk level: {analysis.get('overall_risk')}")
                    print(f"   Top emotion: {analysis.get('top_emotion')}")
                
                return True
            else:
                print(f"❌ Session history is empty!")
                print(f"   This indicates the analysis data was not saved to session history")
                return False
                
        else:
            print(f"❌ Failed to load session history: {history_response.status_code}")
            print(f"   Response: {history_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Session history loading error: {e}")
        return False
    
    # Step 5: Test second analysis to verify session continuation
    print(f"\n4️⃣ Running second analysis to test session continuation...")
    try:
        with open(audio_file, "rb") as f:
            files = {"audio": ("test2.mp3", f, "audio/mp3")}
            data = {"session_id": session_id}
            
            analysis_response2 = requests.post(f"{base_url}/analyze", files=files, data=data, timeout=120)
            
            if analysis_response2.status_code == 200:
                result2 = analysis_response2.json()
                print("✅ Second analysis completed!")
                
                # Check for session insights (should appear after 2nd analysis)
                if 'session_insights' in result2:
                    print("   ✅ Session insights generated after second analysis")
                    insights = result2['session_insights']
                    for key, value in insights.items():
                        if value:
                            print(f"     {key}: {str(value)[:100]}...")
                else:
                    print("   ⚠️ No session insights after second analysis")
            else:
                print(f"❌ Second analysis failed: {analysis_response2.status_code}")
        
        # Check session history after second analysis
        time.sleep(2)
        history_response2 = requests.get(f"{base_url}/session/{session_id}/history")
        if history_response2.status_code == 200:
            history_data2 = history_response2.json()
            history_items2 = history_data2.get('history', [])
            print(f"   Session history now contains: {len(history_items2)} item(s)")
            
            if len(history_items2) >= 2:
                print("   ✅ Session history correctly updated with second analysis")
                return True
            else:
                print("   ❌ Session history not properly updated")
                return False
        
    except Exception as e:
        print(f"❌ Second analysis error: {e}")
        return False

def test_frontend_session_loading():
    """Test the frontend session loading workflow"""
    print(f"\n🌐 FRONTEND SESSION LOADING TEST")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # This would simulate what the frontend does:
    # 1. Create session
    # 2. Run analysis 
    # 3. Load session history
    
    print("This test simulates the frontend workflow:")
    print("1. useSessionManagement.createNewSession()")
    print("2. useAudioProcessing.handleUpload() with sessionId")  
    print("3. useSessionManagement.loadSessionHistory(sessionId)")
    print("\nThe issue might be in step 3 - let's verify the API endpoints...")
    
    # Test session endpoints directly
    try:
        # Test health endpoint
        health_response = requests.get(f"{base_url}/health")
        print(f"Health endpoint: {health_response.status_code}")
        
        # Test session creation
        session_response = requests.post(f"{base_url}/session/new")
        if session_response.status_code == 200:
            session_data = session_response.json()
            test_session_id = session_data.get("session_id")
            print(f"Session creation: ✅ {test_session_id}")
            
            # Test empty session history
            empty_history_response = requests.get(f"{base_url}/session/{test_session_id}/history")
            print(f"Empty session history: {empty_history_response.status_code}")
            
            if empty_history_response.status_code == 200:
                empty_data = empty_history_response.json()
                print(f"Empty history structure: {empty_data}")
            
        else:
            print(f"Session creation failed: {session_response.status_code}")
            
    except Exception as e:
        print(f"Frontend simulation error: {e}")

if __name__ == "__main__":
    print("Starting session history debug tests...\n")
    
    # Test 1: Full workflow
    workflow_success = test_session_history_workflow()
    
    # Test 2: Frontend simulation
    test_frontend_session_loading()
    
    print(f"\n📊 TEST SUMMARY")
    print("=" * 50)
    if workflow_success:
        print("✅ Session history workflow is working correctly")
        print("   The issue might be in the frontend component rendering or state management")
    else:
        print("❌ Session history workflow has issues")
        print("   The problem is in the backend session data saving/loading")
    
    print(f"\n💡 NEXT STEPS:")
    print("1. Check browser console for frontend errors")
    print("2. Verify sessionHistory state in React DevTools") 
    print("3. Check if loadSessionHistory is being called after analysis")
    print("4. Verify SessionHistorySection component is receiving data")
