import requests
import json

def test_linguistic_analysis():
    """Test the new linguistic analysis functionality"""
    
    # Use the existing test audio file (try WAV first)
    audio_file_path = "p:/python/New folder (2)/5.wav"
    
    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio': ('test.wav', audio_file, 'audio/wav')}
            
            print("Testing enhanced linguistic analysis...")
            response = requests.post(
                'http://localhost:8000/analyze',
                files=files
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("[PASS] Analysis successful!")
                print(f"Session ID: {result.get('session_id')}")
                print(f"Transcript length: {len(result.get('transcript', ''))}")
                
                # Check if linguistic analysis is present
                if 'linguistic_analysis' in result:
                    ling_analysis = result['linguistic_analysis']
                    print("\n[BRAIN] Linguistic Analysis Metrics:")
                    print(f"  Word Count: {ling_analysis.get('word_count', 'N/A')}")
                    print(f"  Hesitation Count: {ling_analysis.get('hesitation_count', 'N/A')}")
                    print(f"  Qualifier Count: {ling_analysis.get('qualifier_count', 'N/A')}")
                    print(f"  Certainty Count: {ling_analysis.get('certainty_count', 'N/A')}")
                    print(f"  Complexity Score: {ling_analysis.get('complexity_score', 'N/A')}")
                    print(f"  Speech Rate (WPM): {ling_analysis.get('speech_rate_wpm', 'N/A')}")
                    print(f"  Confidence Ratio: {ling_analysis.get('confidence_ratio', 'N/A')}")
                else:
                    print("[FAIL] Linguistic analysis not found in response")
                
                # Check other components
                print(f"\n[DATA] Other Analysis Components:")
                print(f"  Emotion Analysis: {'[PASS]' if 'emotion_analysis' in result else '[FAIL]'}")
                print(f"  Credibility Score: {result.get('credibility_score', 'N/A')}")
                print(f"  Audio Quality: {'[PASS]' if 'audio_quality' in result else '[FAIL]'}")
                print(f"  Gemini Summary: {'[PASS]' if 'gemini_summary' in result else '[FAIL]'}")
                print(f"  Risk Assessment: {'[PASS]' if 'risk_assessment' in result else '[FAIL]'}")
                
                return True
            else:
                print(f"[FAIL] Analysis failed with status {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
    except FileNotFoundError:
        print(f"[FAIL] Test audio file not found: {audio_file_path}")
        return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] Could not connect to backend server. Make sure it's running on port 8000.")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_linguistic_analysis()
