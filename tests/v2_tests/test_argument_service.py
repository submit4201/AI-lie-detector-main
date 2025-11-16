import pytest
from unittest.mock import MagicMock, AsyncMock

from backend.services.v2_services.argument_service import ArgumentService

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_argument_service_with_mocked_gemini():
    mock_client = MagicMock()
    mock_client.query_json = AsyncMock(return_value={"arguments_present": True, "key_arguments": [{"claim": "A", "evidence": "B"}]})

    svc = ArgumentService(gemini_client=mock_client)
    result = await svc.analyze("Because A, therefore B")

    assert result["service_name"] == "argument"
    assert result["gemini"]["arguments_present"] is True


def test_argument_service_empty_transcript():
    svc = ArgumentService(gemini_client=None)
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(svc.analyze(""))
    assert res["service_name"] == "argument"
    assert res["gemini"] is None
