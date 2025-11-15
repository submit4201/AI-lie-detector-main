#!/usr/bin/env python3

import requests
import json
import time
import os

def test_streaming_endpoint():
    """Test the /analyze/stream endpoint with a real audio file"""
    
    # API endpoint
    stream_url = "http://localhost:8000/analyze/stream"
    regular_url = "http://localhost:8000/analyze"
    
    # Check if test audio file exists
    test_files = ["test_audio.wav", "tests/test_audio.wav", "trial_lie_003.mp3"]
    audio_file_path = None
    
    for file_path in test_files:
        if os.path.exists(file_path):
            audio_file_path = file_path
            break
    
    if not audio_file_path:
        print("[FAIL] ERROR: No test audio file found!")
        return False
    
    print("🔄 STREAMING ANALYSIS INTEGRATION TEST")
    print("=" * 60)
    print(f"📤 Testing streaming endpoint: {stream_url}")
    print(f"🎵 Using audio file: {audio_file_path}")
    print(f"⚡ Testing Server-Sent Events (SSE) streaming")
    
    try:
        # Test 1: Streaming Endpoint
        print("\n[TEST 1] Testing Streaming Analysis Endpoint")
        print("-" * 40)
        
        with open(audio_file_path, "rb") as audio_file:
            files = {
                "audio": (audio_file_path, audio_file, "audio/wav")
            }
            data = {
                "session_id": None  # Let server create session
            }
            
            print(f"🚀 Starting streaming analysis...")
            start_time = time.time()
            
            # Make streaming request
            response = requests.post(stream_url, files=files, data=data, stream=True, timeout=120)
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📋 Content-Type: {response.headers.get('content-type', 'Unknown')}")
            
            if response.status_code == 200:
                print("[PASS] ✅ Streaming endpoint is accessible")
                
                # Parse SSE events
                events_received = 0
                progress_updates = 0
                analysis_results = {}
                
                print("\n📡 Reading Server-Sent Events:")
                print("-" * 30)
                
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])  # Remove 'data: ' prefix
                            events_received += 1
                            
                            if data.get('type') == 'progress':
                                progress_updates += 1
                                step = data.get('step', 'Unknown')
                                progress = data.get('progress', 0)
                                total = data.get('total', 5)
                                print(f"   📈 Progress: {step} ({progress}/{total})")
                            
                            elif data.get('type') == 'result':
                                analysis_type = data.get('analysis_type')
                                analysis_results[analysis_type] = data.get('data')
                                print(f"   📊 Result: {analysis_type}")
                            
                            elif data.get('type') == 'complete':
                                print(f"   ✅ Analysis Complete")
                                break
                            
                            elif data.get('type') == 'error':
                                print(f"   ❌ Error: {data.get('message')}")
                                
                        except json.JSONDecodeError as e:
                            print(f"   ⚠️  JSON Parse Error: {e}")
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"\n📊 STREAMING ANALYSIS RESULTS:")
                print(f"   • Events Received: {events_received}")
                print(f"   • Progress Updates: {progress_updates}")
                print(f"   • Analysis Results: {len(analysis_results)}")
                print(f"   • Duration: {duration:.2f} seconds")
                
                # Validate streaming results
                expected_analyses = ['audio_quality', 'transcript', 'gemini_analysis', 'emotion_analysis', 'linguistic_analysis']
                
                print(f"\n📋 RESULT VALIDATION:")
                for analysis_type in expected_analyses:
                    if analysis_type in analysis_results:
                        print(f"   ✅ {analysis_type}: Available")
                    else:
                        print(f"   ❌ {analysis_type}: Missing")
                
                # Show sample results
                if 'transcript' in analysis_results:
                    transcript = analysis_results['transcript'].get('transcript', 'N/A')
                    print(f"\n📝 Sample Transcript: {transcript[:100]}...")
                
                if 'emotion_analysis' in analysis_results:
                    emotions = analysis_results['emotion_analysis']
                    if isinstance(emotions, list) and emotions:
                        print(f"🎭 Emotions Detected: {len(emotions)}")
                
                streaming_success = len(analysis_results) >= 3 and progress_updates >= 3
                print(f"\n[RESULT] Streaming Analysis: {'✅ PASS' if streaming_success else '❌ FAIL'}")
                
            else:
                print(f"[FAIL] ❌ Streaming endpoint failed with status {response.status_code}")
                print(f"📄 Response: {response.text}")
                return False
        
        # Test 2: Compare with Traditional Analysis
        print(f"\n[TEST 2] Comparing with Traditional Analysis")
        print("-" * 40)
        
        with open(audio_file_path, "rb") as audio_file:
            files = {
                "audio": (audio_file_path, audio_file, "audio/wav")
            }
            data = {
                "session_id": None
            }
            
            print(f"🔄 Running traditional analysis...")
            start_time = time.time()
            
            response = requests.post(regular_url, files=files, data=data, timeout=120)
            
            end_time = time.time()
            traditional_duration = end_time - start_time
            
            if response.status_code == 200:
                traditional_result = response.json()
                print(f"[PASS] ✅ Traditional analysis completed in {traditional_duration:.2f}s")
                
                # Compare key fields
                print(f"\n📊 COMPARISON:")
                print(f"   • Streaming Duration: {duration:.2f}s")
                print(f"   • Traditional Duration: {traditional_duration:.2f}s")
                print(f"   • Speed Difference: {((traditional_duration - duration) / traditional_duration * 100):.1f}% {'faster' if duration < traditional_duration else 'slower'}")
                
                # Check if we have key analysis components
                traditional_has_transcript = bool(traditional_result.get('transcript'))
                traditional_has_emotions = bool(traditional_result.get('emotion_analysis'))
                
                print(f"   • Traditional has transcript: {'✅' if traditional_has_transcript else '❌'}")
                print(f"   • Traditional has emotions: {'✅' if traditional_has_emotions else '❌'}")
                print(f"   • Streaming has transcript: {'✅' if 'transcript' in analysis_results else '❌'}")
                print(f"   • Streaming has emotions: {'✅' if 'emotion_analysis' in analysis_results else '❌'}")
                
            else:
                print(f"[FAIL] ❌ Traditional analysis failed with status {response.status_code}")
        
        # Test 3: WebSocket Connection Test
        print(f"\n[TEST 3] WebSocket Connection Test")
        print("-" * 40)
        
        try:
            import websocket
            
            # Test WebSocket connection
            ws_url = "ws://localhost:8000/ws/test-session-123"
            print(f"🔌 Testing WebSocket connection: {ws_url}")
            
            def on_message(ws, message):
                print(f"   📨 WebSocket Message: {message[:100]}...")
            
            def on_error(ws, error):
                print(f"   ❌ WebSocket Error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                print(f"   🔌 WebSocket Closed")
            
            def on_open(ws):
                print(f"   ✅ WebSocket Connected")
                ws.close()  # Close immediately after connecting
            
            ws = websocket.WebSocketApp(ws_url,
                                      on_open=on_open,
                                      on_message=on_message,
                                      on_error=on_error,
                                      on_close=on_close)
            
            ws.run_forever(timeout=5)
            
        except ImportError:
            print("   ⚠️  websocket-client not installed, skipping WebSocket test")
        except Exception as e:
            print(f"   ❌ WebSocket test failed: {e}")
        
        print(f"\n🎉 STREAMING INTEGRATION TEST COMPLETE")
        print("=" * 60)
        
        return streaming_success
        
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] ERROR: Request failed - {e}")
        return False
    except Exception as e:
        print(f"[FAIL] ERROR: Unexpected error - {e}")
        return False

if __name__ == "__main__":
    success = test_streaming_endpoint()
    print(f"\n🏁 FINAL RESULT: {'✅ SUCCESS' if success else '❌ FAILED'}")
    exit(0 if success else 1)
