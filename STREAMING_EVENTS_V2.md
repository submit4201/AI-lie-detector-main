# V2 Streaming Events Documentation

## Overview

The v2 API provides real-time streaming analysis through Server-Sent Events (SSE). This document describes the event structure, orchestration flow, and per-service payloads.

## Endpoints

- **Snapshot**: `POST /v2/analyze` - Returns complete analysis results
- **Streaming**: `POST /v2/analyze/stream` - Returns SSE stream with incremental updates

## Event Types

### 1. `analysis.update`

Emitted when any service produces a result (partial or final).

```json
{
  "event": "analysis.update",
  "service": "<service_name>",
  "payload": {
    "service_name": "string",
    "service_version": "string",
    "local": {},
    "gemini": {},
    "errors": [],
    "partial": true|false,
    "phase": "coarse|refine|final",
    "chunk_index": 0
  }
}
```

**Fields:**

- `service`: Service identifier (e.g., "transcription", "manipulation", "argument")
- `payload.partial`: `true` for intermediate results, `false` for final
- `payload.phase`: Analysis phase - "coarse" for early/rough, "final" for complete
- `payload.chunk_index`: Sequential number for streaming chunks
- `payload.local`: Locally computed metrics and data
- `payload.gemini`: AI-generated insights and analysis
- `payload.errors`: Array of error objects if any issues occurred

### 2. `analysis.done`

Emitted once when all analysis is complete.

```json
{
  "event": "analysis.done",
  "payload": {
    "results": {
      "<service_name>": { /* final service result */ }
    },
    "meta": {
      "transcript_final": "string",
      "speaker_segments": [],
      "audio_summary": {},
      "quantitative_metrics": {}
    }
  }
}
```

## Orchestration Flow

The v2 runner uses phased orchestration for optimal streaming:

### Phase A: Input Preparation

- Create `AnalysisContext` with request data
- Initialize configuration and session context

### Phase B: Foundational Services (Parallel)

- **Transcription**: Stream audio→text with speaker diarization
- **Audio Analysis**: Extract prosody, quality metrics, vocal patterns

These run concurrently to minimize latency. Updates stream as available.

### Phase C: Quantitative Metrics

- Triggered when sufficient transcript is available (20+ words)
- Computes speech patterns, pauses, interruptions
- May emit partial metrics before final

### Phase D: Higher-Level Analysis (Parallel)

- **Manipulation Analysis**: Detect deception patterns, tactics
- **Argument Analysis**: Extract claims, fallacies, logical structure
- Both use accumulated context (transcript + audio + metrics)
- Stream coarse analysis first, then final detailed analysis

## Service-Specific Payloads

### TranscriptionService

**Partial Update:**

```json
{
  "service_name": "transcription",
  "partial": true,
  "phase": "coarse",
  "local": {
    "partial_transcript": "Current text so far..."
  }
}
```

**Final Update:**

```json
{
  "service_name": "transcription",
  "partial": false,
  "phase": "final",
  "local": {
    "transcript": "Complete transcribed text",
    "segments": [
      {"speaker": "Speaker 1", "start": 0.0, "end": 5.2, "text": "..."}
    ]
  }
}
```

### AudioAnalysisService

**Coarse Phase:**

```json
{
  "service_name": "audio_analysis",
  "partial": true,
  "phase": "coarse",
  "local": {
    "duration": 45.2,
    "quality_score": 85,
    "rms_level": -12.5
  }
}
```

**Final Phase:**

```json
{
  "service_name": "audio_analysis",
  "partial": false,
  "phase": "final",
  "local": {
    "duration": 45.2,
    "quality_metrics": { /* detailed metrics */ },
    "prosody_features": { /* pitch, tempo, etc */ }
  },
  "gemini": {
    "vocal_stress_indicators": [],
    "emotional_tone": "calm",
    "confidence_level": 0.85
  }
}
```

### QuantitativeMetricsService

```json
{
  "service_name": "quantitative_metrics",
  "partial": false,
  "phase": "final",
  "local": {
    "speaking_rate": 145,
    "pause_count": 12,
    "average_pause_duration": 0.8,
    "filler_words": 3,
    "interruption_count": 0
  }
}
```

### ManipulationService

**Coarse Phase (early partial transcript):**

```json
{
  "service_name": "manipulation",
  "partial": true,
  "phase": "coarse",
  "chunk_index": 0,
  "gemini": {
    "overall_risk_score": 35,
    "confidence": 0.6,
    "manipulation_patterns": [
      {
        "pattern": "guilt_tripping",
        "severity": "low",
        "evidence": "Use of phrases like 'after all I've done'"
      }
    ]
  }
}
```

**Final Phase (complete analysis):**

```json
{
  "service_name": "manipulation",
  "partial": false,
  "phase": "final",
  "gemini": {
    "overall_risk_score": 42,
    "confidence": 0.88,
    "manipulation_patterns": [
      /* complete list with detailed evidence */
    ],
    "tactics": ["guilt_tripping", "gaslighting"],
    "rationale": "Detailed explanation of assessment"
  }
}
```

### ArgumentService

**Coarse Phase:**

```json
{
  "service_name": "argument",
  "partial": true,
  "phase": "coarse",
  "gemini": {
    "claims": [
      {
        "claim": "Main assertion",
        "confidence": 0.7,
        "support": ["evidence 1"]
      }
    ],
    "argument_quality": {
      "coherence": 70,
      "evidence_strength": 65
    }
  }
}
```

**Final Phase:**

```json
{
  "service_name": "argument",
  "partial": false,
  "phase": "final",
  "gemini": {
    "claims": [
      /* complete claim structure with support/contradictions */
    ],
    "logical_fallacies": [
      {
        "type": "ad_hominem",
        "description": "Attack on character rather than argument",
        "location": "timestamp or quote"
      }
    ],
    "argument_quality": {
      "coherence": 75,
      "evidence_strength": 68,
      "logical_consistency": 72
    },
    "hesitations": ["um", "uh", "well"]
  }
}
```

## Client Implementation Example

### JavaScript/TypeScript

```javascript
const formData = new FormData();
formData.append('audio', audioBlob);
formData.append('session_id', sessionId);

const response = await fetch('/v2/analyze/stream', {
  method: 'POST',
  body: formData
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.substring(6));
      
      switch (data.event) {
        case 'analysis.update':
          handleServiceUpdate(data.service, data.payload);
          break;
        case 'analysis.done':
          handleAnalysisComplete(data.payload);
          break;
      }
    }
  }
}
```

### React Hook Example

```javascript
function useStreamingAnalysis(audioFile, sessionId) {
  const [services, setServices] = useState({});
  const [isComplete, setIsComplete] = useState(false);
  const [errors, setErrors] = useState([]);
  
  useEffect(() => {
    if (!audioFile) return;
    
    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('session_id', sessionId);
    
    const eventSource = new EventSource('/v2/analyze/stream', {
      method: 'POST',
      body: formData
    });
    
    eventSource.addEventListener('analysis.update', (e) => {
      const data = JSON.parse(e.data);
      setServices(prev => ({
        ...prev,
        [data.service]: data.payload
      }));
      
      if (data.payload.errors) {
        setErrors(prev => [...prev, ...data.payload.errors]);
      }
    });
    
    eventSource.addEventListener('analysis.done', (e) => {
      setIsComplete(true);
      eventSource.close();
    });
    
    return () => eventSource.close();
  }, [audioFile, sessionId]);
  
  return { services, isComplete, errors };
}
```

## AnalysisContext Structure

Services receive an `AnalysisContext` instance via `meta["analysis_context"]`:

```python
@dataclass
class AnalysisContext:
    # Transcript state
    transcript_partial: str = ""
    transcript_final: Optional[str] = None
    
    # Audio state
    audio_bytes: Optional[bytes] = None
    audio_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Metrics and results
    quantitative_metrics: Dict[str, Any] = field(default_factory=dict)
    service_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Speaker diarization
    speaker_segments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Session context (privacy-safe)
    session_summary: Optional[Dict[str, Any]] = None
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
```

## Error Handling

Services return errors in the `errors` field:

```json
{
  "errors": [
    {
      "error": "Service execution failed",
      "details": "Connection timeout to API"
    }
  ]
}
```

UI should:

- Display errors to users in a non-blocking way
- Continue showing results from successful services
- Allow retry for failed services if applicable

## Best Practices

### Backend Services

1. **Yield Early**: Emit coarse results as soon as possible
2. **Update Context**: Store final results in `ctx.service_results`
3. **Handle Errors**: Catch exceptions and return error payloads
4. **Respect Phases**: Use "coarse" for initial, "final" for complete
5. **Privacy**: Never log raw transcripts or audio in production

### Frontend

1. **Progressive Enhancement**: Show partial results immediately
2. **Loading States**: Indicate which services are still processing
3. **Graceful Degradation**: Handle missing services or errors
4. **Accessibility**: Use ARIA live regions for screen readers
5. **Performance**: Debounce rapid updates for smooth UI

## Migration from v1

Key differences:

- v1: Single-shot `POST /analyze` with batch processing
- v2: Streaming `POST /v2/analyze/stream` with incremental results
- v2 provides `AnalysisContext` for cross-service state
- v2 uses structured JSON schemas for consistent output
- v2 supports speaker diarization and audio-aware analysis

## Security Considerations

- Audio data is never logged
- Transcripts are sanitized in logs (only lengths/hashes)
- Session summaries are compact and privacy-safe
- CORS headers configured for authorized origins only
- Rate limiting recommended for production deployments
