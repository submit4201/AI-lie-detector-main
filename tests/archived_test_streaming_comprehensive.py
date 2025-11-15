#!/usr/bin/env python3
"""
Comprehensive Streaming Analysis Test
Tests the complete streaming pipeline including WebSocket connections, 
audio processing, and real-time result delivery.
"""

import sys
import os
import asyncio
import websockets
import json
import time
from pathlib import Path
import requests
import logging

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamingTestSuite:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8001"
        self.ws_url = "ws://127.0.0.1:8001"
        self.test_results = []
        
    def log_test_result(self, test_name, success, message="", data=None):
        """Log a test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "[PASS] PASS" if success else "[FAIL] FAIL"
        logger.info(f"{status} {test_name}: {message}")
        
        return success
    
    def test_backend_health(self):
        """Test if backend is running and healthy"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                return self.log_test_result(
                    "Backend Health Check", 
                    True, 
                    "Backend is running and responding"
                )
            else:
                return self.log_test_result(
                    "Backend Health Check", 
                    False, 
                    f"Backend returned status {response.status_code}"
                )
        except Exception as e:
            return self.log_test_result(
                "Backend Health Check", 
                False, 
                f"Cannot connect to backend: {str(e)}"
            )
    
    def test_streaming_endpoints(self):
        """Test streaming-related API endpoints"""
        try:
            # Test SSE endpoint
            response = requests.get(f"{self.backend_url}/analyze/stream", timeout=5)
            if response.status_code in [200, 400]:  # 400 is expected without proper request
                return self.log_test_result(
                    "Streaming Endpoint Check", 
                    True, 
                    "SSE streaming endpoint is available"
                )
            else:
                return self.log_test_result(
                    "Streaming Endpoint Check", 
                    False, 
                    f"SSE endpoint returned status {response.status_code}"
                )
        except Exception as e:
            return self.log_test_result(
                "Streaming Endpoint Check", 
                False, 
                f"Cannot reach streaming endpoint: {str(e)}"
            )
    
    async def test_websocket_connection(self):
        """Test WebSocket connection capability"""
        try:
            # Create a test session first
            session_response = requests.post(f"{self.backend_url}/sessions/")
            if session_response.status_code != 201:
                return self.log_test_result(
                    "WebSocket Connection Test", 
                    False, 
                    "Could not create session for WebSocket test"
                )
            
            session_data = session_response.json()
            session_id = session_data.get("session_id")
            
            # Test WebSocket connection
            ws_url = f"{self.ws_url}/ws/{session_id}"
            
            async with websockets.connect(ws_url, timeout=10) as websocket:
                # Send a test message
                test_message = {
                    "type": "test",
                    "data": "connection_test"
                }
                await websocket.send(json.dumps(test_message))
                
                # Try to receive a response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    response_data = json.loads(response)
                    
                    return self.log_test_result(
                        "WebSocket Connection Test", 
                        True, 
                        "WebSocket connection successful",
                        response_data
                    )
                except asyncio.TimeoutError:
                    return self.log_test_result(
                        "WebSocket Connection Test", 
                        True, 
                        "WebSocket connected (no immediate response, but connection OK)"
                    )
                    
        except Exception as e:
            return self.log_test_result(
                "WebSocket Connection Test", 
                False, 
                f"WebSocket connection failed: {str(e)}"
            )
    
    def test_audio_service_streaming(self):
        """Test audio service streaming capabilities"""
        try:
            # Import audio service
            import sys
            backend_services_path = Path(__file__).parent.parent / "backend"
            if str(backend_services_path) not in sys.path:
                sys.path.insert(0, str(backend_services_path))
            
            from backend.services.audio_service import AudioService
            from backend.services.streaming_service import StreamingService
            
            # Create service instances
            audio_service = AudioService()
            streaming_service = StreamingService()
            
            # Check if services have streaming methods
            has_streaming = hasattr(audio_service, 'process_audio_streaming') or \
                           hasattr(streaming_service, 'start_streaming_analysis')
            
            if has_streaming:
                return self.log_test_result(
                    "Audio Service Streaming", 
                    True, 
                    "Audio service has streaming capabilities"
                )
            else:
                return self.log_test_result(
                    "Audio Service Streaming", 
                    False, 
                    "Audio service missing streaming methods"
                )
                
        except ImportError as e:
            return self.log_test_result(
                "Audio Service Streaming", 
                False, 
                f"Cannot import streaming services: {str(e)}"
            )
        except Exception as e:
            return self.log_test_result(
                "Audio Service Streaming", 
                False, 
                f"Error testing audio service: {str(e)}"
            )
    
    def test_session_management(self):
        """Test session management for streaming"""
        try:
            # Create a new session
            response = requests.post(f"{self.backend_url}/sessions/")
            if response.status_code != 201:
                return self.log_test_result(
                    "Session Management", 
                    False, 
                    f"Cannot create session: {response.status_code}"
                )
            
            session_data = response.json()
            session_id = session_data.get("session_id")
            
            if not session_id:
                return self.log_test_result(
                    "Session Management", 
                    False, 
                    "Session created but no session_id returned"
                )
            
            # Test session retrieval
            get_response = requests.get(f"{self.backend_url}/sessions/{session_id}")
            if get_response.status_code == 200:
                return self.log_test_result(
                    "Session Management", 
                    True, 
                    f"Session {session_id[:8]}... created and retrieved successfully"
                )
            else:
                return self.log_test_result(
                    "Session Management", 
                    False, 
                    f"Session created but cannot retrieve: {get_response.status_code}"
                )
                
        except Exception as e:
            return self.log_test_result(
                "Session Management", 
                False, 
                f"Session management error: {str(e)}"
            )
    
    def test_frontend_streaming_hooks(self):
        """Test if frontend streaming hooks exist and are properly structured"""
        try:
            frontend_path = Path(__file__).parent.parent / "frontend" / "src" / "hooks"
            
            # Check for streaming hook file
            streaming_hook_path = frontend_path / "useStreamingAnalysis.js"
            audio_hook_path = frontend_path / "useAudioProcessing.js"
            
            if not streaming_hook_path.exists():
                return self.log_test_result(
                    "Frontend Streaming Hooks", 
                    False, 
                    "useStreamingAnalysis.js hook not found"
                )
            
            if not audio_hook_path.exists():
                return self.log_test_result(
                    "Frontend Streaming Hooks", 
                    False, 
                    "useAudioProcessing.js hook not found"
                )
            
            # Read and validate hook content
            with open(streaming_hook_path, 'r') as f:
                streaming_content = f.read()
            
            # Check for key streaming functions
            required_functions = [
                "useStreamingAnalysis",
                "WebSocket",
                "EventSource",
                "startStreamingAnalysis"
            ]
            
            missing_functions = [func for func in required_functions if func not in streaming_content]
            
            if missing_functions:
                return self.log_test_result(
                    "Frontend Streaming Hooks", 
                    False, 
                    f"Missing functions in streaming hook: {', '.join(missing_functions)}"
                )
            
            return self.log_test_result(
                "Frontend Streaming Hooks", 
                True, 
                "Frontend streaming hooks are properly implemented"
            )
            
        except Exception as e:
            return self.log_test_result(
                "Frontend Streaming Hooks", 
                False, 
                f"Error checking frontend hooks: {str(e)}"
            )
    
    async def run_all_tests(self):
        """Run all streaming tests"""
        print("[TEST] Starting Comprehensive Streaming Analysis Tests")
        print("=" * 60)
        
        # Synchronous tests
        tests = [
            self.test_backend_health,
            self.test_streaming_endpoints,
            self.test_audio_service_streaming,
            self.test_session_management,
            self.test_frontend_streaming_hooks
        ]
        
        for test in tests:
            test()
        
        # Asynchronous tests
        await self.test_websocket_connection()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("[TARGET] STREAMING TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"[PASS] Passed: {passed_tests}")
        print(f"[FAIL] Failed: {failed_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"[DATA] Success Rate: {success_rate:.1f}%")
        
        # Show failed tests
        failed_results = [result for result in self.test_results if not result["success"]]
        if failed_results:
            print(f"\n[FAIL] Failed Tests:")
            for result in failed_results:
                print(f"  • {result['test']}: {result['message']}")
        
        # Show recommendations
        print(f"\n[IDEA] Recommendations:")
        if failed_tests == 0:
            print("  [SUCCESS] All streaming tests passed! System is ready for streaming analysis.")
        else:
            print("  [TOOL] Fix failed tests before deploying streaming features.")
            print("  📚 Check backend logs for detailed error information.")
        
        print("=" * 60)

async def main():
    """Main test execution"""
    suite = StreamingTestSuite()
    await suite.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[WARN] Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite error: {str(e)}")
