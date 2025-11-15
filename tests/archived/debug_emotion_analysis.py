#!/usr/bin/env python3
"""
Debug script to test emotion analysis and identify the "NAND" issue
"""

import requests
import json
import sys
import os

def test_emotion_analysis():
    """Test the emotion analysis endpoint with a sample audio file"""
    
    # Check if test audio file exists
    test_files = [
        "test_audio.wav",
        "5.wav", 
        "test.wav"
    ]
    
    audio_file_path = None
    for file in test_files:
        if os.path.exists(file):
            audio_file_path = file
            break
    
    if not audio_file_path:
        print("[FAIL] No test audio file found. Please ensure you have a test audio file.")
        return
    
    print(f"🎵 Testing with audio file: {audio_file_path}")
    # Test the analyze endpoint
    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {'audio': (audio_file_path, audio_file, 'audio/wav')}
            data = {'session_id': 'debug-session-001'}
            
            print("📤 Sending request to backend...")
            response = requests.post(
                'http://localhost:8000/analyze',
                files=files,
                data=data,
                timeout=60
            )
            
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n[SEARCH] DEBUGGING EMOTION ANALYSIS DATA:")
                print("=" * 50)
                
                # Check emotion_analysis structure
                emotion_analysis = result.get('emotion_analysis', [])
                print(f"Emotion Analysis Type: {type(emotion_analysis)}")
                print(f"Emotion Analysis Length: {len(emotion_analysis) if hasattr(emotion_analysis, '__len__') else 'N/A'}")
                print(f"Emotion Analysis Content: {emotion_analysis}")
                
                if emotion_analysis:
                    print("\n[DATA] Individual Emotions:")
                    for i, emotion in enumerate(emotion_analysis):
                        print(f"  {i}: {type(emotion)} = {emotion}")
                        if isinstance(emotion, dict):
                            label = emotion.get('label', 'UNKNOWN')
                            score = emotion.get('score', 0)
                            print(f"      Label: '{label}' | Score: {score}")
                
                # Check if there are nested arrays
                if emotion_analysis and isinstance(emotion_analysis[0], list):
                    print("\n[WARN]  NESTED ARRAY DETECTED!")
                    nested_emotions = emotion_analysis[0]
                    print(f"Nested emotions: {nested_emotions}")
                    for i, emotion in enumerate(nested_emotions):
                        print(f"  Nested {i}: {type(emotion)} = {emotion}")
                
                # Check other relevant fields
                print(f"\n📋 Other Analysis Fields:")
                print(f"Transcript: {result.get('transcript', 'N/A')[:100]}...")
                print(f"Credibility Score: {result.get('credibility_score', 'N/A')}")
                print(f"Confidence Level: {result.get('confidence_level', 'N/A')}")
                
                # Save full response for analysis
                with open('debug_response.json', 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Full response saved to debug_response.json")
                
            else:
                print(f"[FAIL] Request failed with status {response.status_code}")
                print(f"Error response: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Request error: {e}")
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")

def test_emotion_classifier_directly():
    """Test the emotion classifier directly to see raw output"""
    try:
        from transformers import pipeline
        
        print("\n🔬 TESTING EMOTION CLASSIFIER DIRECTLY:")
        print("=" * 50)
        
        # Initialize the same classifier as in main.py
        emotion_classifier = pipeline(
            "text-classification", 
            model="j-hartmann/emotion-english-distilroberta-base", 
            top_k=7, 
            return_all_scores=True
        )
        
        test_text = "Hello, my name is John and I am telling the truth about everything."
        
        print(f"Test text: '{test_text}'")
        result = emotion_classifier(test_text)
        
        print(f"Raw classifier result type: {type(result)}")
        print(f"Raw classifier result: {result}")
        
        # Process the result as done in main.py
        if isinstance(result, list) and len(result) > 0:
            emotion_scores = result[0] if isinstance(result[0], list) else result
        else:
            emotion_scores = [{"label": "neutral", "score": 0.5}]
            
        print(f"Processed emotion_scores: {emotion_scores}")
        
    except Exception as e:
        print(f"[FAIL] Direct classifier test failed: {e}")

if __name__ == "__main__":
    print("[LAUNCH] EMOTION ANALYSIS DEBUG SCRIPT")
    print("=" * 40)
    
    # Test the API
    test_emotion_analysis()
    
    # Test the classifier directly
    test_emotion_classifier_directly()
    
    print("\n[PASS] Debug script completed!")
