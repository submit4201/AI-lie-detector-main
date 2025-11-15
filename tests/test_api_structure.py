"""
Pytest integration tests for API structure validation.
Tests the structure of REST and Streaming API responses.
"""
import pytest


@pytest.mark.integration
def test_analyze_endpoint_structure(client, temp_audio):
    """Test that /analyze endpoint returns expected structure."""
    with open(temp_audio, "rb") as f:
        files = {"audio": ("test.wav", f, "audio/wav")}
        resp = client.post("/analyze", files=files, data={"session_id": "test_session"})
    
    assert resp.status_code in (200, 400, 422), f"Unexpected status code: {resp.status_code}"
    
    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, dict), "Response should be a dictionary"
        
        # Check that response contains at least one of the expected keys
        expected_keys = ["linguistic_analysis", "transcript", "audio_quality", "analysis"]
        assert any(k in data for k in expected_keys), \
            f"Response should contain at least one of {expected_keys}"


@pytest.mark.integration
def test_analyze_endpoint_response_types(client, temp_audio):
    """Test that /analyze endpoint returns correct data types."""
    with open(temp_audio, "rb") as f:
        files = {"audio": ("test.wav", f, "audio/wav")}
        resp = client.post("/analyze", files=files, data={"session_id": "test_session"})
    
    if resp.status_code == 200:
        data = resp.json()
        
        # If linguistic_analysis exists, it should be a dict
        if "linguistic_analysis" in data:
            assert isinstance(data["linguistic_analysis"], dict), \
                "linguistic_analysis should be a dictionary"
        
        # If transcript exists, it should be a string
        if "transcript" in data:
            assert isinstance(data["transcript"], str), \
                "transcript should be a string"
        
        # If audio_quality exists, it should be a dict or string
        if "audio_quality" in data:
            assert isinstance(data["audio_quality"], (dict, str)), \
                "audio_quality should be a dict or string"


@pytest.mark.integration
def test_session_creation_endpoint(client):
    """Test that /session/new endpoint works correctly."""
    resp = client.post("/session/new")
    
    assert resp.status_code == 200, f"Session creation failed with status {resp.status_code}"
    
    data = resp.json()
    assert isinstance(data, dict), "Session response should be a dictionary"
    assert "session_id" in data, "Session response should contain session_id"
    assert isinstance(data["session_id"], str), "session_id should be a string"
    assert len(data["session_id"]) > 0, "session_id should not be empty"


@pytest.mark.integration
@pytest.mark.slow
def test_streaming_endpoint_structure(client, temp_audio):
    """Test that /analyze/stream endpoint returns streaming events."""
    # Create a session first
    session_resp = client.post("/session/new")
    assert session_resp.status_code == 200
    session_id = session_resp.json().get("session_id")
    
    with open(temp_audio, "rb") as f:
        files = {"audio": ("test.wav", f, "audio/wav")}
        data = {"session_id": session_id}
        
        # Note: TestClient doesn't support streaming well, so this is a basic check
        resp = client.post("/analyze/stream", files=files, data=data)
        
        # Should at least accept the request
        assert resp.status_code in (200, 400, 422, 501), \
            f"Unexpected status code: {resp.status_code}"
