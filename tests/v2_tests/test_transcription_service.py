import pytest
from unittest.mock import MagicMock, AsyncMock

from backend.services.v2_services.transcription_service import TranscriptionService

# Mark all tests in this file as unit tests
pytestmark = pytest.mark.unit

@pytest.fixture
def mock_gemini_client():
    """Fixture for a mocked GeminiClientV2."""
    client = MagicMock()
    client.transcribe = AsyncMock()
    return client

@pytest.mark.asyncio
async def test_transcription_with_audio(mock_gemini_client):
    """Test that the service calls the Gemini client's transcribe method when audio is provided."""
    mock_gemini_client.transcribe.return_value = "This is a test transcript."
    service = TranscriptionService(gemini_client=mock_gemini_client)
    
    audio_bytes = b"dummy_audio_data"
    result = await service.analyze(audio=audio_bytes)

    mock_gemini_client.transcribe.assert_called_once_with(audio_bytes)
    assert result["transcript"] == "This is a test transcript."
    assert result["errors"] is None
    assert result["service_name"] == "transcription"


@pytest.mark.asyncio
async def test_transcription_streaming_interim_and_final(mock_gemini_client):
    # Simulate async transcription returning a final transcript
    mock_gemini_client.transcribe.return_value = "Chunked result"
    service = TranscriptionService(gemini_client=mock_gemini_client)

    events = []
    async for ev in service.stream_analyze(audio=b"dummy_audio"):
        events.append(ev)

    # There should be an interim (first) and a final event
    assert len(events) >= 2
    assert events[0].get("interim") is True
    assert events[-1].get("interim") is False

@pytest.mark.asyncio
async def test_transcription_with_existing_transcript(mock_gemini_client):
    """Test that the service skips transcription if a transcript is already provided."""
    service = TranscriptionService(gemini_client=mock_gemini_client)
    
    result = await service.analyze(transcript="An existing transcript.")

    mock_gemini_client.transcribe.assert_not_called()
    assert result["transcript"] == "An existing transcript."
    assert result["errors"] is None

@pytest.mark.asyncio
async def test_transcription_no_audio_or_transcript(mock_gemini_client):
    """Test that the service returns an error if no audio or transcript is provided."""
    service = TranscriptionService(gemini_client=mock_gemini_client)
    
    result = await service.analyze()

    mock_gemini_client.transcribe.assert_not_called()
    assert result["transcript"] == ""
    assert result["errors"] is not None
    assert len(result["errors"]) == 1
    assert result["errors"][0]["error"] == "No audio data provided for transcription."

@pytest.mark.asyncio
async def test_transcription_client_failure(mock_gemini_client):
    """Test that the service handles exceptions from the Gemini client."""
    mock_gemini_client.transcribe.side_effect = Exception("Transcription API failed")
    service = TranscriptionService(gemini_client=mock_gemini_client)
    
    audio_bytes = b"dummy_audio_data"
    result = await service.analyze(audio=audio_bytes)

    assert result["transcript"] == ""
    assert result["errors"] is not None
    assert len(result["errors"]) == 1
    assert result["errors"][0]["error"] == "Transcription failed"
    assert "Transcription API failed" in result["errors"][0]["details"]
