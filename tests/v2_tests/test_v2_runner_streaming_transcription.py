import pytest
import asyncio
from typing import AsyncGenerator

from backend.services.v2_services.runner import V2AnalysisRunner
from backend.services.v2_services.transcription_service import TranscriptionService

pytestmark = pytest.mark.unit


class DummyStreamingClient:
    async def transcribe_stream(self, audio_bytes: bytes):
        # simple generator that simulates streaming partial updates
        yield {"interim": True, "partial_transcript": "partial 1"}
        await asyncio.sleep(0)
        yield {"interim": True, "partial_transcript": "partial 2"}
        await asyncio.sleep(0)
        yield {"interim": False, "transcript": "final transcript"}

    async def transcribe(self, audio_bytes: bytes):
        return "final transcript"


@pytest.mark.asyncio
async def test_runner_streams_transcript():
    dummy = DummyStreamingClient()
    # Build a runner that uses a transcription service with the dummy client
    factories = [
        lambda ctx: TranscriptionService(gemini_client=dummy)
    ]
    runner = V2AnalysisRunner(gemini_client=dummy, service_factories=factories)

    events = []
    async for event in runner.stream_run("", audio=b"dummy", meta={}):
        events.append(event)
        if event.get('event') == 'analysis.done':
            break

    # We should have seen at least one transcript update (interim) and final
    transcript_updates = [e for e in events if e.get('service') == 'transcript']
    assert len(transcript_updates) >= 2
    assert any(e.get('payload', {}).get('transcript') == "final transcript" for e in transcript_updates)
