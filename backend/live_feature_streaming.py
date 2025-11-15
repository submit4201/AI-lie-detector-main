# live_feature_streaming.py

import asyncio
import json
import websockets
from typing import Dict, Tuple
from .layer_3_feature_assembler import assemble_feature_vector  # Your layer 3 output

################################################################################
# CONFIGURATION
################################################################################

WS_SERVER_URI = "ws://localhost:8765"
AUDIO_PATH = "example.wav"  # This should point to your real audio input

################################################################################
# CLIENT THAT STREAMS LAYER 3 FEATURES TO WEBSOCKET SERVER
################################################################################

async def stream_layer3_features(uri: str, audio_path: str):
    print(f"Connecting to {uri} to stream features from {audio_path}...")
    features = assemble_feature_vector(audio_path)  # Full dict of metrics

    async with websockets.connect(uri) as websocket:
        # Phase 1: Calibration start (you can skip this if baseline is preloaded on server)
        await websocket.send(json.dumps({"status": "begin_calibration", "duration_sec": 1, "hz": 1}))
        await websocket.send(json.dumps({"status": "calibration_frame", "metrics": features}))

        await asyncio.sleep(1)
        await websocket.send(json.dumps({"status": "begin_scoring"}))

        # Simulate scoring stream (loop it, or iterate if multiple segments)
        for _ in range(100):
            await websocket.send(json.dumps({"status": "scoring_frame", "metrics": features}))
            await asyncio.sleep(0.5)

################################################################################
# MAIN
################################################################################

if __name__ == "__main__":
    try:
        asyncio.run(stream_layer3_features(WS_SERVER_URI, AUDIO_PATH))
    except KeyboardInterrupt:
        print("Stream interrupted by user.")
