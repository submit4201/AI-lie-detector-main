import pytest
import asyncio

from backend.services.v2_services.gemini_client import GeminiClientV2


class DummyPart:
    def __init__(self, text: str):
        self.text = text


class DummyContent:
    def __init__(self, parts):
        self.parts = parts


class DummyCandidate:
    def __init__(self, content):
        self.content = content


class DummyMessage:
    def __init__(self, candidates):
        self.candidates = candidates


class DummySession:
    def __init__(self, messages):
        self._messages = messages

    async def send_message(self, contents):
        # Accept whatever is sent, no-op
        return

    async def receive(self):
        for m in self._messages:
            yield m


class DummyChat:
    def __init__(self, messages):
        self._messages = messages

    # Implement async context manager protocol directly on DummyChat
    async def __aenter__(self):
        self.session = DummySession(self._messages)
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        return False

    # Expose connect as a regular method returning the context manager itself,
    # matching the usage pattern `client.aio.live.chat.connect(...)` in the
    # Gemini client implementation.
    def connect(self, model=None):  # pragma: no cover - trivial adapter
        return self


class DummyAIO:
    def __init__(self, messages):
        self.live = type('L', (), {'chat': DummyChat(messages)})


class DummyClient:
    def __init__(self, messages):
        self.aio = DummyAIO(messages)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_transcribe_stream_yields_interim_and_final():
    # Create a small list of DummyMessages to emulate the SDK streaming
    messages = [
        DummyMessage([DummyCandidate(DummyContent([DummyPart('partial 1')]))]),
        DummyMessage([DummyCandidate(DummyContent([DummyPart('partial 2')]))]),
    ]

    dummy_client = DummyClient(messages)

    # Instantiate GeminiClientV2 but replace the _sdk_client with our dummy
    g = GeminiClientV2(api_key="test-key")
    g._sdk_client = dummy_client
    # Override transcribe with a simple async function to avoid SDK calls
    async def fake_transcribe(audio_bytes, **kwargs):
        return "final transcript"

    g.transcribe = fake_transcribe

    events = []
    async for ev in g.transcribe_stream(b"data"):
        events.append(ev)
        if ev.get('interim') is False:
            break

    # Expect at least two partials and final transcript
    assert any(e.get('partial_transcript') == 'partial 1' for e in events)
    assert any(e.get('partial_transcript') == 'partial 2' for e in events)
    assert any(e.get('interim') is False for e in events)
