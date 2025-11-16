import pytest

from backend.services.v2_services.service_registry import SERVICE_FACTORIES, REGISTERED_SERVICES, build_service_instances
from backend.services.v2_services.gemini_client import GeminiClientV2

pytestmark = pytest.mark.unit


def test_registered_factories_include_core_services():
    names = list(SERVICE_FACTORIES.keys())
    assert 'transcription' in names
    assert 'audio_analysis' in names
    assert 'quantitative_metrics' in names
    assert 'manipulation' in names
    assert 'argument' in names


def test_build_service_instances_default_context():
    # Don't try to construct the real GeminiClientV2 in unit tests; use a dummy
    class DummyClient:
        async def transcribe(self, audio):
            return "dummy"
        async def query_json(self, prompt, **kwargs):
            return {"text": "dummy"}

    client = DummyClient()
    services = build_service_instances(gemini_client=client, transcript="a", audio=b"bytes", meta={})
    # Ensure factories run and return service objects
    assert len(services) >= 1
    # Names set on service objects
    assert any(hasattr(s, 'serviceName') for s in services)
