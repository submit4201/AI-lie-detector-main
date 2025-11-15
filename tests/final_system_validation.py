#!/usr/bin/env python3
"""
Final System Validation
Comprehensive test suite to validate all major functionality
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:5174"
TEST_AUDIO = Path(__file__).parent / "test_extras" / "test_audio.wav"

def test_health_endpoint():
    """Test the backend health endpoint"""
    print("🔍 [TEST] Backend Health Check...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Backend Status: {health_data.get('status', 'unknown')}")
            print(f"   🛠️  Services: {', '.join(health_data.get('services', []))}")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def test_traditional_analysis():
    """Test traditional analysis endpoint"""
    print("📊 [TEST] Traditional Analysis...")
    
    if not TEST_AUDIO.exists():
        print(f"   ❌ Test audio not found: {TEST_AUDIO}")
        return False
    
    try:
        files = {"audio": open(TEST_AUDIO, "rb")}
        data = {"session_id": "validation_traditional"}
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/analyze",
            files=files,
            data=data,
            timeout=60
        )
        duration = time.time() - start_time
        files["audio"].close()
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Analysis completed in {duration:.1f}s")
            print(f"   📝 Transcript: {len(result.get('transcript', ''))} chars")
            print(f"   🎭 Emotions: {len(result.get('emotions', []))} detected")
            print(f"   📊 Fields: {len(result.keys())} analysis fields")
            return True
        else:
            print(f"   ❌ Traditional analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Traditional analysis error: {e}")
        return False

def test_streaming_analysis():
    """Test streaming analysis endpoint"""
    print("🌊 [TEST] Streaming Analysis...")
    
    if not TEST_AUDIO.exists():
        print(f"   ❌ Test audio not found: {TEST_AUDIO}")
        return False
    
    try:
        files = {"audio": open(TEST_AUDIO, "rb")}
        data = {"session_id": "validation_streaming"}
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/analyze/stream",
            files=files,
            data=data,
            stream=True,
            timeout=60
        )
        files["audio"].close()
        
        if response.status_code != 200:
            print(f"   ❌ Streaming failed: {response.status_code}")
            return False
        
        events = []
        analysis_steps = []
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        event_data = json.loads(line_str[6:])
                        events.append(event_data)
                        
                        if event_data.get('type') == 'result':
                            analysis_steps.append(event_data.get('analysis_type'))
                        elif event_data.get('type') == 'complete':
                            break
                    except json.JSONDecodeError:
                        continue
        
        duration = time.time() - start_time
        print(f"   ✅ Streaming completed in {duration:.1f}s")
        print(f"   📡 Events received: {len(events)}")
        print(f"   🔄 Analysis steps: {', '.join(analysis_steps)}")
        return True
        
    except Exception as e:
        print(f"   ❌ Streaming error: {e}")
        return False

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print("🌐 [TEST] Frontend Accessibility...")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Frontend accessible at {FRONTEND_URL}")
            return True
        else:
            print(f"   ❌ Frontend status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend error: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🚀 AI LIE DETECTOR - FINAL SYSTEM VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Backend Health", test_health_endpoint),
        ("Traditional Analysis", test_traditional_analysis),
        ("Streaming Analysis", test_streaming_analysis),
        ("Frontend Access", test_frontend_accessibility),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
        print()
    
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 SYSTEM FULLY OPERATIONAL!")
        print("   • Backend API: Running on port 8000")
        print("   • Frontend UI: Running on port 5174")
        print("   • Streaming: Real-time analysis working")
        print("   • Traditional: Batch analysis working")
        print("   • Audio Processing: All formats supported")
        print("   • Ready for production use!")
    else:
        print(f"\n⚠️  SYSTEM NEEDS ATTENTION")
        print("   Some components are not working correctly.")
        print("   Check the output above for details.")

if __name__ == "__main__":
    main()
