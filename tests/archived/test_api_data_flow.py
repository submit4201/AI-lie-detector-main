import requests
import json

# Test the API endpoint directly
API_URL = "http://localhost:8001"

def test_api_upload():
    """Test uploading a small audio file to verify data structure"""
    
    # Use one of the existing test audio files
    audio_file_path = "test_audio.wav"
    try:
        with open(audio_file_path, 'rb') as f:
            files = {'audio': (audio_file_path, f, 'audio/wav')}
            
            print("📤 Sending audio file to API...")
            response = requests.post(f"{API_URL}/analyze", files=files)
            
            print(f"[PASS] Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("[DATA] API Response Structure:")
                print(f"  - transcript: {'[PASS]' if 'transcript' in result else '[FAIL]'}")
                print(f"  - speaker_transcripts: {'[PASS]' if 'speaker_transcripts' in result else '[FAIL]'}")
                print(f"  - credibility_score: {'[PASS]' if 'credibility_score' in result else '[FAIL]'}")
                print(f"  - audio_analysis: {'[PASS]' if 'audio_analysis' in result else '[FAIL]'}")
                print(f"  - emotion_analysis: {'[PASS]' if 'emotion_analysis' in result else '[FAIL]'}")
                
                # Save the complete response for inspection
                with open('api_test_response.json', 'w') as out_file:
                    json.dump(result, out_file, indent=2)
                print("💾 Full response saved to 'api_test_response.json'")
                
                return result
            else:
                print(f"[FAIL] API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
    
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return None

if __name__ == "__main__":
    test_api_upload()
