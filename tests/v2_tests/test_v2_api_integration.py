import pytest
import os
import io
import wave
import math
import tempfile

from fastapi.testclient import TestClient

from backend.main import app

pytestmark = pytest.mark.integration

SKIP_MSG = "Integration tests require GEMINI_API_KEY set in environment"

def generate_sine_wave(duration_seconds=1.0, sample_rate=16000, frequency=440.0):
    num_samples = int(duration_seconds * sample_rate)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(num_samples):
            # simple sine wave
            value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            wf.writeframesraw(value.to_bytes(2, 'little', signed=True))
    return buf.getvalue()


@pytest.fixture(scope='module')
def client():
    return TestClient(app)


@pytest.mark.skipif(not os.getenv('GEMINI_API_KEY'), reason=SKIP_MSG)
def test_v2_analyze_integration(client):
    audio_bytes = generate_sine_wave()
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tf:
        tf.write(audio_bytes)
        tf.flush()
        tf_name = tf.name

    with open(tf_name, 'rb') as f:
        files = {'audio': ('test.wav', f, 'audio/wav')}
        response = client.post('/v2/analyze', files=files)

    assert response.status_code == 200
    data = response.json()
    assert 'transcript' in data
    assert isinstance(data['transcript'], str)

    # Basic sanity checks
    assert 'services' in data
    assert 'audio_analysis' in data['services'] or 'quantitative_metrics' in data['services'] or 'gemini' in data

    # Clean up file
    try:
        os.unlink(tf_name)
    except Exception:
        pass


@pytest.mark.skipif(not os.getenv('GEMINI_API_KEY'), reason=SKIP_MSG)
def test_v2_analyze_stream_integration(client):
    audio_bytes = generate_sine_wave(duration_seconds=1.0)
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tf:
        tf.write(audio_bytes)
        tf.flush()
        tf_name = tf.name

    with open(tf_name, 'rb') as f:
        files = {'audio': ('test.wav', f, 'audio/wav')}
        response = client.post('/v2/analyze/stream', files=files, stream=True)

    assert response.status_code == 200
    # Read first few lines from the SSE stream; should contain 'analysis.update' or 'analysis.done'
    found_event = False
    # Use iter_lines to consume a few segments
    try:
        for i, line in enumerate(response.iter_lines(decode_unicode=True)):
            if i > 50:
                break
            if line and 'analysis' in line:
                found_event = True
                break
    finally:
        try:
            response.close()
        except Exception:
            pass

    assert found_event, 'SSE streaming did not produce any analysis events'

    # Clean up file
    try:
        os.unlink(tf_name)
    except Exception:
        pass

