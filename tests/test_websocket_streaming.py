#!/usr/bin/env python3
"""
WebSocket Streaming Test
Test WebSocket connections for real-time analysis updates
"""

import asyncio
import websockets
import json
import logging
import requests
from pathlib import Path

# Test configuration
WS_URL = "ws://127.0.0.1:8000/ws/test_websocket_session"
BACKEND_URL = "http://127.0.0.1:8000"
TEST_AUDIO = Path(__file__).parent / "test_extras" / "test_audio.wav"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    """Test WebSocket connection and real-time updates"""
    print("[TEST] Testing WebSocket Real-time Updates...")
    
    try:
        # Connect to WebSocket
        print(f"[CONNECT] Connecting to WebSocket: {WS_URL}")
        async with websockets.connect(WS_URL) as websocket:
            print("[PASS] WebSocket connected successfully!")
            
            # Start a streaming analysis in the background
            print("[LAUNCH] Starting background streaming analysis...")
            
            # Use requests to start streaming analysis
            files = {"audio": open(TEST_AUDIO, "rb")}
            data = {"session_id": "test_websocket_session"}
            
            # This will start the analysis and we should receive updates via WebSocket
            response = requests.post(
                f"{BACKEND_URL}/analyze/stream",
                files=files,
                data=data,
                stream=True,
                timeout=30
            )
            
            files["audio"].close()
            
            # Listen for WebSocket messages
            print("[LISTEN] Listening for WebSocket messages...")
            messages_received = 0
            
            try:
                while messages_received < 10:  # Limit to prevent infinite loop
                    # Wait for message with timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    messages_received += 1
                    
                    try:
                        data = json.loads(message)
                        msg_type = data.get('type', 'unknown')
                        analysis_type = data.get('analysis_type', '')
                        
                        print(f"  [MSG] WebSocket Message {messages_received}: {msg_type}")
                        if analysis_type:
                            print(f"    [SEARCH] Analysis Type: {analysis_type}")
                        
                    except json.JSONDecodeError:
                        print(f"  [WARN]  Non-JSON message: {message}")
                        
            except asyncio.TimeoutError:
                print("[TIMEOUT] No more messages received (timeout)")
            
            print(f"[PASS] WebSocket test completed! Received {messages_received} messages")
            return messages_received > 0
            
    except Exception as e:
        print(f"[FAIL] WebSocket test failed: {e}")
        return False

async def main():
    """Run WebSocket test"""
    print("[TARGET] Starting WebSocket Streaming Test")
    print("=" * 50)
    
    # Check if audio file exists
    if not TEST_AUDIO.exists():
        print(f"[FAIL] Test audio file not found: {TEST_AUDIO}")
        return False
    
    print(f"[FILE] Using test audio: {TEST_AUDIO}")
    
    # Test WebSocket functionality
    success = await test_websocket_connection()
    
    print("=" * 50)
    if success:
        print("[SUCCESS] WebSocket streaming test passed!")
    else:
        print("[WARN]  WebSocket streaming test failed!")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
