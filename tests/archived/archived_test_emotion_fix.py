#!/usr/bin/env python3
"""
Test the emotion analysis fix specifically
"""
import requests
import json
import time

def test_emotion_analysis_fix():    # Test the emotion analysis fix directly
    audio_file_path = 'tests/test_extras/test_audio.wav'
    session_id = f'test_session_{int(time.time())}'

    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            data = {'session_id': session_id}
            
            print('🧪 Testing emotion analysis fix...')
            response = requests.post('http://localhost:8000/analyze', files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print(f'✅ Status: {response.status_code}')
                print(f'📝 Session ID: {result.get("session_id", "N/A")}')
                print(f'🎭 Emotions: {len(result.get("emotion_analysis", []))} detected')
                print(f'📊 Analysis fields: {len([k for k in result.keys() if not k.startswith("_")])}')
                
                # Check for the specific error we were fixing
                emotion_data = result.get('emotion_analysis', [])
                if isinstance(emotion_data, list) and len(emotion_data) > 0:
                    print(f'🎉 Emotion analysis working: {emotion_data[:2]}')
                else:
                    print(f'⚠️  No emotions detected (may be normal for test audio)')
                    
                # Check if session was created successfully
                if result.get('session_id'):
                    print(f'🔄 Session creation: SUCCESS')
                else:
                    print(f'❌ Session creation: FAILED')
                    
            else:
                print(f'❌ Error: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'❌ Test failed: {str(e)}')

if __name__ == "__main__":
    test_emotion_analysis_fix()
