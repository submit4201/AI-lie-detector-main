#!/usr/bin/env python3
"""
Test script to verify the complete integration of new UI components
with the backend API for the AI Lie Detector application.
"""

import requests
import json
import time

def test_api_integration():
    """Test the complete API integration with all new components."""
    
    # Backend URL
    base_url = "http://localhost:8000"
    
    # Test text for analysis
    test_text = """
    I was at the store yesterday buying groceries. Well, actually, I think it was two days ago. 
    No wait, it was definitely yesterday because I remember seeing my neighbor there. 
    I bought milk, bread, and some other stuff. The prices were, um, reasonable I guess. 
    I mean, everything is so expensive these days, you know? But I definitely had enough money 
    to pay for everything. I always do my shopping there because they have the best selection.
    """
    
    print("[TEST] Testing Complete AI Lie Detector Integration")
    print("=" * 50)
    
    try:        # Test basic health check
        print("1. Testing API health...")
        health_response = requests.get(f"{base_url}/")
        if health_response.status_code == 200:
            print("[PASS] API is running successfully")
            print(f"   Response: {health_response.json().get('message', 'N/A')}")
        else:
            print("[FAIL] API health check failed")
            return
        
        # Test text analysis endpoint
        print("\n2. Testing text analysis endpoint...")
        analysis_data = {
            "text": test_text,
            "speaker_name": "Test Speaker"
        }
        
        analysis_response = requests.post(
            f"{base_url}/analyze_text",
            json=analysis_data,
            headers={"Content-Type": "application/json"}
        )
        
        if analysis_response.status_code == 200:
            print("[PASS] Text analysis endpoint working")
            result = analysis_response.json()
            
            # Check for new fields we added
            print("\n3. Checking for new UI component data...")
            
            # Check quantitative_metrics
            if "quantitative_metrics" in result:
                print("[PASS] quantitative_metrics field present")
                metrics = result["quantitative_metrics"]
                print(f"   - Speech rate: {metrics.get('speech_rate_words_per_minute', 'N/A')}")
                print(f"   - Formality score: {metrics.get('formality_score', 'N/A')}")
                print(f"   - Hesitation count: {metrics.get('hesitation_count', 'N/A')}")
            else:
                print("[FAIL] quantitative_metrics field missing")
              # Check audio_analysis
            if "audio_analysis" in result and result["audio_analysis"]:
                print("[PASS] audio_analysis field present")
                audio = result["audio_analysis"]
                print(f"   - Vocal confidence: {audio.get('vocal_confidence_level', 'N/A')}")
                print(f"   - Pitch analysis: {audio.get('pitch_analysis', 'N/A')[:50] if isinstance(audio.get('pitch_analysis'), str) else 'N/A'}...")
            else:
                print("[WARN]  audio_analysis field missing or empty (expected for text-only analysis)")
            
            # Check enhanced_understanding
            if "enhanced_understanding" in result:
                print("[PASS] enhanced_understanding field present")
                enhanced = result["enhanced_understanding"]
                print(f"   - Follow-up questions: {len(enhanced.get('suggested_follow_up_questions', []))}")
                print(f"   - Unverified claims: {len(enhanced.get('unverified_claims', []))}")
            else:
                print("[FAIL] enhanced_understanding field missing")
            
            # Check manipulation_assessment
            if "manipulation_assessment" in result:
                print("[PASS] manipulation_assessment field present")
                manipulation = result["manipulation_assessment"]
                print(f"   - Manipulation score: {manipulation.get('manipulation_score', 'N/A')}")
            else:
                print("[FAIL] manipulation_assessment field missing")
            
            # Check argument_analysis
            if "argument_analysis" in result:
                print("[PASS] argument_analysis field present")
                argument = result["argument_analysis"]
                print(f"   - Argument coherence: {argument.get('overall_argument_coherence_score', 'N/A')}")
            else:
                print("[FAIL] argument_analysis field missing")
            
            # Check speaker_attitude
            if "speaker_attitude" in result:
                print("[PASS] speaker_attitude field present")
                attitude = result["speaker_attitude"]
                print(f"   - Respect level: {attitude.get('respect_level_score', 'N/A')}")
                print(f"   - Sarcasm detected: {attitude.get('sarcasm_detected', 'N/A')}")
            else:
                print("[FAIL] speaker_attitude field missing")
            
            print(f"\n4. Overall Analysis Result:")
            print(f"   - Credibility Score: {result.get('credibility_score', 'N/A')}")
            print(f"   - Confidence Level: {result.get('confidence_level', 'N/A')}")
            print(f"   - Risk Assessment: {result.get('risk_assessment', {}).get('overall_risk', 'N/A')}")
            
            # Save the complete response for debugging
            with open("test_integration_response.json", "w") as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Complete response saved to 'test_integration_response.json'")
            
            print(f"\n[SUCCESS] Integration test completed successfully!")
            
        else:
            print(f"[FAIL] Text analysis failed with status: {analysis_response.status_code}")
            print(f"Response: {analysis_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("[FAIL] Could not connect to backend. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"[FAIL] Test failed with error: {str(e)}")

if __name__ == "__main__":
    test_api_integration()
