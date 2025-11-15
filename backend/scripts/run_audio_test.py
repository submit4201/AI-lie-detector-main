#!/usr/bin/env python3
"""Generate a short WAV file and POST it to the local /analyze endpoint.
Saves `backend/test_audio.wav` and prints the HTTP response.
"""
import wave
import struct
import math
import requests
import time
from pathlib import Path


def generate_sine_wav(path: Path, duration_s=3.0, freq=220.0, sample_rate=16000):
    n_samples = int(duration_s * sample_rate)
    amplitude = 16000  # safe for 16-bit

    with wave.open(str(path), 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)

        for i in range(n_samples):
            t = float(i) / sample_rate
            sample = int(amplitude * math.sin(2 * math.pi * freq * t))
            wf.writeframes(struct.pack('<h', sample))


def post_audio(path: Path, url='http://127.0.0.1:8000/analyze'):
    # The /analyze endpoint expects the UploadFile form field to be named 'audio'
    files = {'audio': (path.name, open(path, 'rb'), 'audio/wav')}
    data = {'speaker_name': 'Test Speaker'}

    print(f"Posting audio to {url} -> {path}")
    try:
        r = requests.post(url, files=files, data=data, timeout=120)
    except Exception as e:
        print("Request failed:", e)
        raise

    print("Status:", r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text[:10000])


def main():
    out = Path(__file__).resolve().parents[1] / 'test_audio.wav'
    print("Generating WAV:", out)
    generate_sine_wav(out, duration_s=3.0, freq=220.0)
    # let server pick up file/time
    time.sleep(0.5)
    post_audio(out)


if __name__ == '__main__':
    main()
