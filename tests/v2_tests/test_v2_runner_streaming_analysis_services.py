import pytest
import asyncio

from backend.services.v2_services.runner import V2AnalysisRunner
from backend.services.v2_services.transcription_service import TranscriptionService

pytestmark = pytest.mark.unit


class DummyStreamingClientForAnalysis:
    async def transcribe_stream(self, audio_bytes: bytes, *, context_prompt: str = None):
        # Emulate structured JSON streaming containing both transcription and manipulation
        await asyncio.sleep(0)
        yield {"interim": True, "partial_transcript": "part 1"}
        await asyncio.sleep(0)
        # Simulate JSON analysis being returned from model
        yield {"interim": True, "partial_transcript": "part 2"}
        await asyncio.sleep(0)
        yield {"interim": False, "transcript": "final", "analysis": {"manipulation": {"score": 0.8}}}

    async def transcribe(self, audio_bytes: bytes):
        return "final"


@pytest.mark.asyncio
async def test_runner_forwards_service_analysis_from_stream():
    dummy = DummyStreamingClientForAnalysis()
    factories = [
        lambda ctx: TranscriptionService(gemini_client=dummy)
    ]
    runner = V2AnalysisRunner(gemini_client=dummy, service_factories=factories)

    events = []
    async for ev in runner.stream_run('', audio=b'data', meta={'streaming_analysis': True}):
        events.append(ev)
        if ev.get('event') == 'analysis.done':
            break

    # Ensure we saw at least one partial and a final transcript
    assert any(e.get('service') == 'transcript' for e in events)
    assert any(e.get('service') == 'transcript' and e.get('payload', {}).get('transcript') == 'final' for e in events)
