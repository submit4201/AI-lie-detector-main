#!/usr/bin/env python3
"""
Enhanced Session Insights Demo
Shows the new intelligent session analysis with better data visualization
"""

import requests
import json
import time
from pathlib import Path

def demo_enhanced_session_insights():
    base_url = "http://localhost:8000"
    
    print("[LAUNCH] Enhanced Session Insights Demo")
    print("=" * 50)
    
    # Create a new session
    print("\n1. Creating new session...")
    response = requests.post(f"{base_url}/session/new")
    if response.status_code != 200:
        print(f"[FAIL] Failed to create session: {response.status_code}")
        return
    
    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"[PASS] Created session: {session_id}")
    
    # Simulate multiple analyses with different credibility patterns
    test_scenarios = [
        {
            "name": "Initial Statement",
            "expected_credibility": 65,
            "description": "Subject appears confident but shows some defensive language"
        },
        {
            "name": "Follow-up Questions", 
            "expected_credibility": 45,
            "description": "Credibility drops as inconsistencies emerge"
        },
        {
            "name": "Detailed Inquiry",
            "expected_credibility": 35,
            "description": "Further decline as deception indicators increase"
        },
        {
            "name": "Final Confrontation",
            "expected_credibility": 25,
            "description": "Significant credibility loss with clear deception patterns"
        }
    ]
    
    # Check if we have test audio files
    audio_files = [
        "test_audio.wav",
        "Recording.wav", 
        "5.wav"
    ]
    
    available_audio = []
    for audio_file in audio_files:
        if Path(audio_file).exists():
            available_audio.append(audio_file)
    
    if not available_audio:
        print("[FAIL] No audio files found for testing")
        return
    
    print(f"\n2. Running {len(test_scenarios)} analysis scenarios...")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n   [DATA] Scenario {i}: {scenario['name']}")
        
        # Use available audio files cyclically
        audio_file = available_audio[(i-1) % len(available_audio)]
        
        try:
            with open(audio_file, 'rb') as f:
                files = {'audio': f}
                data = {'session_id': session_id}
                
                response = requests.post(
                    f"{base_url}/analyze", 
                    files=files, 
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    credibility = result.get('credibility_score', 'N/A')
                    
                    print(f"      [PASS] Analysis complete - Credibility: {credibility}%")
                    
                    # Check for session insights (available from 2nd analysis onwards)
                    if i >= 2 and 'session_insights' in result:
                        insights = result['session_insights']
                        print(f"      [BRAIN] Session insights generated:")
                        
                        for insight_type, insight_text in insights.items():
                            insight_name = insight_type.replace('_', ' ').title()
                            print(f"         • {insight_name}: {insight_text[:80]}...")
                    
                else:
                    print(f"      [FAIL] Analysis failed: {response.status_code}")
                    
        except Exception as e:
            print(f"      [FAIL] Error in scenario {i}: {str(e)}")
        
        # Small delay between analyses
        time.sleep(1)
    
    # Get final session history
    print(f"\n3. Retrieving session analytics...")
    response = requests.get(f"{base_url}/session/{session_id}/history")
    
    if response.status_code == 200:
        history = response.json()
        print(f"[PASS] Session complete with {len(history.get('history', []))} analyses")
        
        # Display session summary
        history_items = history.get('history', [])
        if history_items:
            print(f"\n[PROGRESS] Session Summary:")
            print(f"   • Total Analyses: {len(history_items)}")
            
            credibility_scores = [item.get('analysis', {}).get('credibility_score', 0) for item in history_items]
            if credibility_scores:
                avg_credibility = sum(credibility_scores) / len(credibility_scores)
                initial_score = credibility_scores[0]
                final_score = credibility_scores[-1]
                trend = final_score - initial_score
                
                print(f"   • Average Credibility: {avg_credibility:.1f}%")
                print(f"   • Credibility Trend: {trend:+.1f}% ({initial_score}% → {final_score}%)")
                print(f"   • Trend Direction: {'[PROGRESS] Improving' if trend > 10 else '📉 Declining' if trend < -10 else '[DATA] Stable'}")
        
        print(f"\n[TARGET] Enhanced Session Insights Features:")
        print(f"   [MAGIC] Intelligent AI Analysis (replaces placeholder text)")
        print(f"   [DATA] Interactive Analytics Dashboard")
        print(f"   📅 Visual Timeline with Progression")
        print(f"   🎨 Enhanced UI with Gradient Cards")
        print(f"   [PROGRESS] Real-time Credibility Charting")
        print(f"   [SEARCH] Hover Interactions and Tooltips")
        
    else:
        print(f"[FAIL] Failed to get session history: {response.status_code}")
    
    print(f"\n🌟 Demo Complete!")
    print(f"   Frontend URL: http://localhost:3000")
    print(f"   Test the enhanced session insights with session ID: {session_id}")

if __name__ == "__main__":
    demo_enhanced_session_insights()
