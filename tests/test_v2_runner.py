import asyncio
from typing import Dict, Any, Optional, Iterable

import pytest

from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.runner import V2AnalysisRunner


class _StubGeminiClient:
    """Lightweight stub that mimics the Gemini client's transcript helper."""

    def __init__(self, transcript_text: str = "auto transcript") -> None:
        self._transcript_text = transcript_text
        self.calls = 0

    async def transcribe(self, audio: bytes, mime_type: Optional[str] = None) -> str:  # pragma: no cover - exercised in tests
        self.calls += 1
        return self._transcript_text


class _FakeService(AnalysisService):
    """Deterministic AnalysisService for exercising the runner orchestration."""

    serviceName = "fake_metrics"
    serviceVersion = "test-1.0"

    def __init__(
        self,
        *,
        service_name: str,
        delay: float = 0.0,
        transcript: str = "",
        audio_data: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(transcript=transcript, audio_data=audio_data, meta=meta)
        self.serviceName = service_name
        self.delay = delay
        self.serviceVersion = "test-1.0"

    async def analyze(self, transcript: str, audio: Optional[bytes], meta: Dict[str, Any]):
        if self.delay:
            await asyncio.sleep(self.delay)

        tokens = transcript.split()
        payload = {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {"token_count": len(tokens)},
            "gemini": {
                "interaction_metrics": {
                    "overall_sentiment_label": "neutral",
                    "question_to_statement_ratio": meta.get("question_ratio_override"),
                }
            },
            "errors": None,
        }
        return payload


def _build_runner(
    *,
    service_names: Iterable[str],
    delays: Optional[Dict[str, float]] = None,
    gemini_client: Optional[_StubGeminiClient] = None,
) -> V2AnalysisRunner:
    delays = delays or {}
    gemini_client = gemini_client or _StubGeminiClient()

    def _make_factory(name: str):
        def _factory(context: Dict[str, Any]) -> AnalysisService:
            return _FakeService(
                service_name=name,
                delay=delays.get(name, 0.0),
                transcript=context.get("transcript", ""),
                audio_data=context.get("audio"),
                meta=context.get("meta"),
            )

        return _factory

    factories = [_make_factory(name) for name in service_names]
    return V2AnalysisRunner(gemini_client=gemini_client, service_factories=factories)


@pytest.mark.unit
def test_runner_generates_transcript_when_missing():
    """Runner should auto-generate a transcript when only audio bytes are provided."""

    stub_client = _StubGeminiClient(transcript_text="generated from audio")
    runner = _build_runner(service_names=["quantitative_metrics"], gemini_client=stub_client)

    result = asyncio.run(
        runner.run(
            transcript="",
            audio=b"binary audio",
            meta={"session_id": "runner-test", "question_ratio_override": 0.42},
        )
    )

    assert result["transcript"] == "generated from audio"
    assert result["meta"]["transcript_auto_generated"] is True
    assert "quantitative_metrics" in result["services"]
    service_payload = result["services"]["quantitative_metrics"]
    assert service_payload["local"]["token_count"] == 3  # generated transcript has 3 words
    assert service_payload["gemini"]["interaction_metrics"]["question_to_statement_ratio"] == 0.42
    assert stub_client.calls == 1


@pytest.mark.unit
def test_stream_run_emits_incremental_events():
    """stream_run should surface transcript, progress, and completion events in order."""

    runner = _build_runner(
        service_names=["alpha", "beta"],
        delays={"beta": 0.01},
        gemini_client=_StubGeminiClient(transcript_text="hello world"),
    )

    async def _collect_events():
        collected = []
        async for event in runner.stream_run("stream me", audio=None, meta={"session_id": "stream-test"}):
            collected.append(event)
        return collected

    events = asyncio.run(_collect_events())

    assert events[0]["event"] == "analysis.update"
    assert events[0]["service"] == "transcript"
    assert events[-1]["event"] == "analysis.done"

    update_events = [evt for evt in events if evt["event"] == "analysis.update" and evt.get("service") != "transcript"]
    assert {evt["service"] for evt in update_events} == {"alpha", "beta"}

    progress_events = [evt for evt in events if evt["event"] == "analysis.progress"]
    assert progress_events[-1]["completed"] == progress_events[-1]["total"] == 2

    aggregate = events[-1]["payload"]
    assert aggregate["transcript"] == "stream me"
    assert set(aggregate["services"].keys()) == {"alpha", "beta"}
    assert aggregate["meta"]["transcript_auto_generated"] is False