import pytest
from pydub import AudioSegment
import numpy as np
import io

from backend.services.v2_services.audio_analysis_service import AudioAnalysisService

# Mark all tests in this file as unit tests
pytestmark = pytest.mark.unit

@pytest.fixture
def silent_audio_segment():
    """Fixture for a silent 1-second mono audio segment."""
    sample_rate = 16000
    duration_ms = 1000
    samples = np.zeros(int(sample_rate * duration_ms / 1000), dtype=np.int16)
    return AudioSegment(samples.tobytes(), frame_rate=sample_rate, sample_width=2, channels=1)

@pytest.fixture
def silent_audio_bytes(silent_audio_segment):
    """Fixture for silent audio as bytes."""
    byte_io = io.BytesIO()
    silent_audio_segment.export(byte_io, format="wav")
    return byte_io.getvalue()

@pytest.mark.asyncio
async def test_audio_analysis_with_valid_audio(silent_audio_bytes):
    """Test that the service correctly analyzes valid audio bytes."""
    service = AudioAnalysisService()
    result = await service.analyze(audio=silent_audio_bytes)

    assert result["service_name"] == "audio_analysis"
    assert result["errors"] is None
    
    local_results = result["local"]
    assert local_results["duration"] == 1.0
    assert local_results["sample_rate"] == 16000
    assert local_results["channels"] == 1
    assert local_results["loudness"] < 0  # Should be very low for silence

@pytest.mark.asyncio
async def test_audio_analysis_no_audio():
    """Test that the service returns an error if no audio is provided."""
    service = AudioAnalysisService()
    result = await service.analyze()

    assert result["errors"] is not None
    assert len(result["errors"]) == 1
    assert result["errors"][0]["error"] == "No audio data provided."

@pytest.mark.asyncio
async def test_audio_analysis_invalid_audio():
    """Test that the service handles invalid audio data gracefully."""
    service = AudioAnalysisService()
    invalid_audio_bytes = b"this is not audio"
    result = await service.analyze(audio=invalid_audio_bytes)

    assert result["errors"] is not None
    assert len(result["errors"]) == 1
    assert result["errors"][0]["error"] == "Audio processing failed"
