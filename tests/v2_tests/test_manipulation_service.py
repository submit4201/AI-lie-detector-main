import pytest
from unittest.mock import MagicMock, AsyncMock

from backend.services.v2_services.manipulation_service import ManipulationService

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_manipulation_service_with_mocked_gemini():
    mock_client = MagicMock()
    mock_client.query_json = AsyncMock(return_value={"is_manipulative": True, "manipulation_score": 0.8})

    svc = ManipulationService(gemini_client=mock_client)
    result = await svc.analyze("This is test transcript that shows signs of manipulation.")

    assert result["service_name"] == "manipulation"
    assert result["gemini"]["is_manipulative"] is True


def test_manipulation_service_empty_transcript():
    svc = ManipulationService(gemini_client=None)
    # Calling analyze with an empty transcript returns a minimal structure
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(svc.analyze(""))
    assert res["service_name"] == "manipulation"
    assert res["gemini"] is None
