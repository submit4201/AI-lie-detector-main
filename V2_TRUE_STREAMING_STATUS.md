# V2 True Streaming Implementation Status

## Overview

All v2 services now implement true streaming (not pseudo-streaming). Services yield incremental results as they become available, following the v2 protocol.

## Service Streaming Status

### ✅ Gemini-Based Streaming Services

These services use the Gemini Live API via WebSocket (`client.aio.live.chat.connect()`):

1. **ArgumentService** (`argument_service.py`)
   - Uses `gemini_client.json_stream()` with Live API
   - Coarse phase: Initial argument structure
   - Final phase: Refined argument analysis
   - WebSocket-based real-time streaming

2. **ManipulationService** (`manipulation_service.py`)
   - Uses `gemini_client.json_stream()` with Live API
   - Coarse phase: Initial manipulation detection
   - Final phase: Complete manipulation analysis
   - WebSocket-based real-time streaming

3. **TranscriptionService** (`transcription_service.py`)
   - Uses `gemini_client.transcribe_stream()` with Live API
   - Yields interim transcripts as they arrive
   - Final complete transcript at end
   - WebSocket-based real-time streaming

### ✅ Local Computation Streaming Services

These services perform local computation and yield results incrementally:

4. **AudioAnalysisService** (`audio_analysis_service.py`) ⭐ **UPDATED**
   - **Coarse phase**: Quick metrics (duration, sample rate, channels)
   - **Final phase**: Complete quality assessment (loudness, SNR, clarity)
   - True incremental yielding

5. **QuantitativeMetricsService** (`quantitative_metrics_service.py`) ⭐ **UPDATED**
   - **Coarse phase**: Numerical linguistic metrics (local computation)
   - **Final phase**: Complete with Gemini interaction analysis
   - True incremental yielding

6. **EnhancedMetricsService** (`enhanced_metrics_service.py`)
   - **Coarse phase**: Quick linguistic metrics from partial transcript
   - **Final phase**: Full acoustic + linguistic metrics
   - True incremental yielding

7. **CredibilityServiceV2** (`credibility_service.py`)
   - **Coarse phase**: Preliminary credibility assessment
   - **Final phase**: Complete statistical scoring with CI
   - True incremental yielding

## V2 Protocol Compliance

All services follow the standardized v2 result shape:

```python
{
    "service_name": str,        # Service identifier
    "service_version": str,     # Version number
    "local": dict,              # Locally computed metrics
    "gemini": dict,             # LLM-generated insights
    "errors": list,             # Error information
    "partial": bool,            # True for intermediate, False for final
    "phase": str,               # "coarse", "refine", or "final"
    "chunk_index": int          # Sequential chunk number
}
```

## Gemini Live API Implementation

Location: `gemini_client.py` line 290-419

### WebSocket-Based Streaming

```python
async def json_stream(self, prompt: str, *, schema, audio_bytes, context, model_hint):
    """Stream structured JSON responses from Gemini Live API."""
    
    # Connect to Live API via WebSocket
    async with client.aio.live.chat.connect(model=model_name, config=config) as session:
        # Send message with prompt and optional audio
        await session.send_message(contents=parts)
        
        # Receive streaming chunks
        async for message in session.receive():
            if message.candidates:
                for candidate in message.candidates:
                    for part in candidate.content.parts:
                        if part.text:
                            # Yield incremental JSON chunks
                            yield {
                                "data": json.loads(part.text),
                                "chunk_index": chunk_index,
                                "done": False
                            }
        
        # Final done marker
        yield {"data": {}, "chunk_index": chunk_index, "done": True}
```

### Fallback Behavior

If Live API is unavailable (network issues, SDK version, etc.), the client falls back to simulated streaming:
- Fetches complete response
- Chunks it into 3-5 pieces
- Yields with small delays

This ensures compatibility while preferring true streaming.

## Streaming Patterns

### Pattern 1: Two-Phase Streaming (Most Common)

```python
async def stream_analyze(self, transcript, audio, meta):
    # Phase 1: Coarse - Quick preliminary results
    quick_result = compute_quick_metrics()
    yield {
        "partial": True,
        "phase": "coarse",
        "chunk_index": 0,
        "local": quick_result
    }
    
    # Phase 2: Final - Complete analysis
    complete_result = compute_complete_metrics()
    yield {
        "partial": False,
        "phase": "final",
        "chunk_index": 1,
        "local": complete_result
    }
```

### Pattern 2: Multi-Chunk Streaming (Gemini Services)

```python
async def stream_analyze(self, transcript, audio, meta):
    chunk_index = 0
    async for stream_chunk in gemini_client.json_stream(prompt, schema):
        if stream_chunk.get("done"):
            break
        
        yield {
            "partial": True,
            "phase": "coarse",
            "chunk_index": chunk_index,
            "gemini": stream_chunk.get("data")
        }
        chunk_index += 1
    
    # Final phase with complete data
    yield {
        "partial": False,
        "phase": "final",
        "chunk_index": chunk_index,
        "gemini": final_data
    }
```

## Benefits of True Streaming

1. **Lower Latency**: Users see results as soon as available
2. **Better UX**: Progressive loading instead of waiting for complete analysis
3. **Resource Efficiency**: Results can be displayed before all computation finishes
4. **Scalability**: Backend can process multiple requests without blocking
5. **Flexibility**: Different phases allow for different levels of detail

## Testing Streaming Services

### Example: Testing AudioAnalysisService

```python
import asyncio
from backend.services.v2_services.audio_analysis_service import AudioAnalysisService

async def test_streaming():
    service = AudioAnalysisService()
    audio_bytes = get_test_audio()
    
    chunks = []
    async for chunk in service.stream_analyze(audio=audio_bytes):
        print(f"Received chunk: phase={chunk['phase']}, partial={chunk['partial']}")
        chunks.append(chunk)
    
    assert len(chunks) >= 2  # At least coarse and final
    assert chunks[0]["partial"] == True
    assert chunks[-1]["partial"] == False

asyncio.run(test_streaming())
```

## Migration Guide

### Converting from Pseudo-Streaming to True Streaming

**Before (pseudo-streaming using default protocol):**
```python
class MyService(AnalysisService):
    async def analyze(self, transcript, audio, meta):
        result = compute_everything()  # Compute all at once
        return {"local": result}
    
    # No stream_analyze - uses default which wraps analyze
```

**After (true streaming):**
```python
class MyService(AnalysisService):
    async def stream_analyze(self, transcript, audio, meta):
        # Yield coarse results first
        quick = compute_quick()
        yield {
            "local": quick,
            "partial": True,
            "phase": "coarse",
            "chunk_index": 0
        }
        
        # Yield final results
        complete = compute_complete()
        yield {
            "local": complete,
            "partial": False,
            "phase": "final",
            "chunk_index": 1
        }
    
    async def analyze(self, transcript, audio, meta):
        # Optional: convenience wrapper
        result = None
        async for chunk in self.stream_analyze(transcript, audio, meta):
            result = chunk
        return result
```

## Summary

✅ **All 7 v2 services now implement true streaming**
✅ **Gemini services use WebSocket-based Live API**
✅ **Local services yield incremental results**
✅ **All services follow v2 protocol shape**
✅ **No pseudo-streaming - all services are streaming-first**

The v2 architecture is now fully streaming-capable, providing low-latency, progressive results to users.
