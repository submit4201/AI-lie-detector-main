import sys
import os
import math
import wave
import struct
from pathlib import Path
import pytest

# Ensure repository root is importable
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Try importing FastAPI app; tests that require it will skip if not importable
try:
    from backend.main import app as fastapi_app
except Exception:
    fastapi_app = None

@pytest.fixture(scope="session")
def project_root():
    return REPO_ROOT

@pytest.fixture(scope="session")
def app():
    if fastapi_app is None:
        pytest.skip("FastAPI app not importable; skipping integration tests that require app")
    return fastapi_app

@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient
    return TestClient(app)

@pytest.fixture
async def async_client(app):
    import httpx
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def temp_audio(tmp_path):
    """Generate a tiny WAV file (sine tone) for audio-related tests."""
    path = tmp_path / "test_tone.wav"
    nchannels = 1
    sampwidth = 2
    framerate = 16000
    duration = 0.2  # seconds
    frequency = 440.0

    nframes = int(framerate * duration)
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(nchannels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(framerate)
        for i in range(nframes):
            value = int(32767.0 * 0.1 * math.sin(2.0 * math.pi * frequency * (i / framerate)))
            wf.writeframes(struct.pack('<h', value))

    yield str(path)

@pytest.fixture
def session_factory(client):
    def _create_session():
        res = client.post('/session/new')
        assert res.status_code == 200
        data = res.json()
        return data.get('session_id')
    return _create_session

@pytest.fixture
def monkeypatch_model_pipeline(monkeypatch):
    """Monkeypatch transformers.pipeline to return deterministic outputs for tests."""
    def fake_pipeline(task, model=None, **kwargs):
        def classifier(text, **_kw):
            # return format compatible with return_all_scores=True or single output
            return [[{"label": "neutral", "score": 0.9}]]
        return classifier

    try:
        monkeypatch.setattr('transformers.pipeline', fake_pipeline)
    except Exception:
        # If transformers isn't installed, skip monkeypatching
        pass
    return monkeypatch

@pytest.fixture
def mock_gemini():
    """Stub external LLM HTTP calls using respx if available."""
    try:
        import respx  # type: ignore
        import httpx  # type: ignore
    except Exception:
        pytest.skip("respx/httpx not installed")
    with respx.mock(assert_all_called=False) as rx:
        rx.route(method="POST").mock(return_value=httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "stubbed"}]}}]}))
        yield rx


@pytest.fixture
def skip_if_no_external():
    def _skip(module_name: str):
        import importlib
        try:
            importlib.import_module(module_name)
        except Exception:
            pytest.skip(f"{module_name} not available; skipping")
    return _skip


def pytest_configure(config):
    # register markers for clarity
    config.addinivalue_line("markers", "unit: unit tests (fast)")
    config.addinivalue_line("markers", "integration: integration tests (require server/resources)")
    config.addinivalue_line("markers", "slow: slow tests")
