import requests
import pytest


@pytest.mark.integration
def test_analyze_structure(client, temp_audio):
    with open(temp_audio, "rb") as f:
        files = {"audio": ("test.wav", f, "audio/wav")}
        resp = client.post("/analyze", files=files, data={"session_id": "test_session"})
    assert resp.status_code in (200, 400, 422)
    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, dict)
        assert any(k in data for k in ["linguistic_analysis", "transcript", "audio_quality"])
import json
import os
import time

API_URL = "http://localhost:8000"  # Ensure this matches your backend port from main.py
STREAMING_API_URL = f"{API_URL}/analyze/stream"
REST_API_URL = f"{API_URL}/analyze"
TEST_AUDIO_FILE = "P:/python/New folder (2)/tests/test_extras/trial_lie_005.mp3"  # Make sure this file exists in the tests directory

def get_api_structure():
    """
    Tests the structure of both REST and Streaming API responses.
    Saves the responses to JSON files for inspection.
    """
    print(f"🧪 Starting API Structure Test")
    print(f"Backend API URL: {API_URL}")

    # Create a dummy test_audio.wav if it doesn't exist for the test to run
    if not os.path.exists(TEST_AUDIO_FILE):
        print(f"⚠️ Test audio file '{TEST_AUDIO_FILE}' not found. Creating a dummy WAV file.")
        try:
            import wave
            with wave.open(TEST_AUDIO_FILE, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(44100)
                wf.writeframes(b'\x00\x00' * 44100) # 1 second of silence
            print(f"✅ Dummy '{TEST_AUDIO_FILE}' created successfully.")
        except Exception as e:
            print(f"❌ Error creating dummy WAV file: {e}")
            print("Please ensure a valid 'test_audio.wav' file is in the 'tests' directory.")
            return

    # 1. Test REST API Structure
    print("\n--- Testing REST API Structure ---")
    try:
        with open(TEST_AUDIO_FILE, 'rb') as f:
            files = {'audio': (TEST_AUDIO_FILE, f, 'audio/wav')}
            print(f"📤 Sending audio to REST API: {REST_API_URL}")
            response = requests.post(REST_API_URL, files=files, timeout=60)
            print(f"STATUS: {response.status_code}")

            if response.status_code == 200:
                rest_api_response_data = response.json()
                with open('rest_api_structure_response.json', 'w') as outfile:
                    json.dump(rest_api_response_data, outfile, indent=4)
                print("✅ REST API response saved to 'rest_api_structure_response.json'")
                # Print main keys for a quick check
                print("Main keys in REST response:", list(rest_api_response_data.keys()))
            else:
                print(f"❌ REST API request failed. Status: {response.status_code}")
                print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to REST API: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON from REST API response: {e}")
        print(f"Raw response: {response.text if 'response' in locals() else 'No response object'}")
    except Exception as e:
        print(f"❌ An unexpected error occurred during REST API test: {e}")

    # 2. Test Streaming API Structure
    print("\n--- Testing Streaming API Structure ---")
    all_streaming_events = []
    try:
        with open(TEST_AUDIO_FILE, 'rb') as f:
            files = {'audio': (TEST_AUDIO_FILE, f, 'audio/wav')}
            # Create a new session for the streaming test
            session_response = requests.post(f"{API_URL}/session/new", timeout=10)
            session_id = None
            if session_response.status_code == 200:
                session_id = session_response.json().get("session_id")
                print(f"Stream Test: Created session_id: {session_id}")
            else:
                print(f"Stream Test: Failed to create session: {session_response.status_code} {session_response.text}")
                # Fallback if session creation fails, though streaming might behave differently
                session_id = "test_streaming_session"


            data = {'session_id': session_id}
            print(f"📤 Sending audio to Streaming API: {STREAMING_API_URL} with session_id: {session_id}")

            with requests.post(STREAMING_API_URL, files=files, data=data, stream=True, timeout=60) as response:
                print(f"STATUS: {response.status_code}")
                if response.status_code == 200:
                    print("🎧 Streaming connection successful. Receiving events...")
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith('data:'):
                                try:
                                    event_data_str = decoded_line[len('data:'):].strip()
                                    event_data = json.loads(event_data_str)
                                    all_streaming_events.append(event_data)
                                    print(f"Received event type: {event_data.get('type')}, analysis_type: {event_data.get('analysis_type')}")
                                except json.JSONDecodeError as e:
                                    print(f"⚠️  Could not decode JSON from event: {event_data_str} - Error: {e}")
                                except Exception as e_inner:
                                    print(f"⚠️  Error processing streaming event: {e_inner} - Line: {decoded_line}")


                    if all_streaming_events:
                        with open('streaming_api_events_structure.json', 'w') as outfile:
                            json.dump(all_streaming_events, outfile, indent=4)
                        print(f"✅ Streaming API events saved to 'streaming_api_events_structure.json' ({len(all_streaming_events)} events)")
                        # Print types of events received for a quick check
                        event_types = set(evt.get('type') for evt in all_streaming_events)
                        analysis_types = set(evt.get('analysis_type') for evt in all_streaming_events if evt.get('analysis_type'))
                        print(f"Event types received: {event_types}")
                        print(f"Analysis types in events: {analysis_types}")

                    else:
                        print("⚠️ No streaming events received or processed.")
                else:
                    print(f"❌ Streaming API request failed. Status: {response.status_code}")
                    print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to Streaming API: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred during Streaming API test: {e}")

    print("\n🏁 API Structure Test Finished 🏁")

if __name__ == "__main__":
    get_api_structure()
