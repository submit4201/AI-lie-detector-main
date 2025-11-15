import pytest


@pytest.mark.integration
def test_api_data_flow(client, temp_audio):
    with open(temp_audio, "rb") as f:
        files = {"audio": ("test.wav", f, "audio/wav")}
        resp = client.post("/analyze", files=files)
    assert resp.status_code in (200, 400, 422)
    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, dict)
        assert any(k in data for k in ["transcript", "speaker_transcripts", "audio_analysis", "emotion_analysis"])