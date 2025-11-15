import pytest


@pytest.mark.integration
def test_api_response_basic(client, temp_audio):
    with open(temp_audio, "rb") as f:
        files = {"audio": ("test.wav", f, "audio/wav")}
        resp = client.post("/analyze", files=files, data={"session_id": "test_session"})
    assert resp.status_code in (200, 400, 422)
    if resp.status_code == 200:
        data = resp.json()
        assert "linguistic_analysis" in data or "transcript" in data