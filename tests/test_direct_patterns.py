#!/usr/bin/env python3
"""
Direct test of enhanced linguistic patterns
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.linguistic_service import analyze_linguistic_patterns

def test_patterns():
    test_cases = [
        {
            "name": "Original Recording",
            "text": "that's pretty impressive Ben's mom used to live inside of a mountain right out here right out here on this mountain in Oakville",
            "duration": 37.33
        },
        {
            "name": "Repetition Test",
            "text": "Well, I was right out here, right out here on the mountain. The whole thing, the whole thing was confusing.",
            "duration": 15.0
        },
        {
            "name": "Hesitation Test", 
            "text": "Um, well, you know, I think maybe, like, it was around 8 PM or so, you understand?",
            "duration": 12.0
        },
        {
            "name": "Certainty Test",
            "text": "I absolutely know for certain that I definitely saw him there. Without doubt, I'm 100 percent sure.",
            "duration": 10.0
        },
        {
            "name": "Formality Test",
            "text": "Thank you kindly sir, I respectfully submit that furthermore, this matter requires careful consideration.",
            "duration": 8.0
        }
    ]
    
    for test_case in test_cases:
        print(f"\n[TEST] Testing: {test_case['name']}")
        print(f"Text: {test_case['text']}")
        print("=" * 80)
        
        result = analyze_linguistic_patterns(test_case['text'], test_case['duration'])
        
        print(f"[DATA] Quantitative Metrics:")
        print(f"  Word Count: {result.get('word_count', 'N/A')}")
        print(f"  Hesitation Count: {result.get('hesitation_count', 'N/A')}")
        print(f"  Qualifier Count: {result.get('qualifier_count', 'N/A')}")
        print(f"  Certainty Count: {result.get('certainty_count', 'N/A')}")
        print(f"  Repetition Count: {result.get('repetition_count', 'N/A')}")
        print(f"  Formality Score: {result.get('formality_score', 'N/A')}")
        print(f"  Complexity Score: {result.get('complexity_score', 'N/A'):.1f}")
        print(f"  Confidence Ratio: {result.get('confidence_ratio', 'N/A')}")
        print(f"  Speech Rate: {result.get('speech_rate_wpm', 'N/A')} WPM")

if __name__ == "__main__":
    test_patterns()

