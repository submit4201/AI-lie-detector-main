#!/usr/bin/env python3
"""
Test script for the Session Insights Generator
"""

from backend.services.session_insights_service import SessionInsightsGenerator
from datetime import datetime

def test_session_insights():
    generator = SessionInsightsGenerator()
    
    # Mock session context
    session_context = {
        "previous_analyses": 2,
        "session_duration": 12.5,  # minutes
        "recent_transcripts": [
            "I didn't take the money from the cash register.",
            "Well, maybe I touched it but I didn't steal anything.",
            "Okay, I took some change but it was just a few dollars."
        ]
    }
    
    # Mock current analysis
    current_analysis = {
        "credibility_score": 45,
        "confidence_level": "Medium",
        "linguistic_analysis": {
            "hesitation_count": 12,
            "speech_rate_wpm": 135,
            "formality_score": 30
        },
        "emotion_analysis": [
            {"label": "nervous", "score": 0.8},
            {"label": "anxious", "score": 0.6}
        ],
        "risk_assessment": {"overall_risk": "High"},
        "deception_flags": ["contradictory_statements", "evasive_language", "emotional_inconsistency"]
    }
    
    # Mock session history
    session_history = [
        {
            "timestamp": datetime.now(),
            "transcript": "I didn't take the money from the cash register.",
            "analysis": {
                "credibility_score": 65,
                "confidence_level": "Medium", 
                "overall_risk": "Medium",
                "emotion_analysis": [{"label": "confident", "score": 0.7}],
                "linguistic_analysis": {
                    "hesitation_count": 3,
                    "speech_rate_wpm": 155,
                    "formality_score": 45
                },
                "risk_assessment": {"overall_risk": "Medium"},
                "deception_flags": ["defensive_language"]
            }
        },
        {
            "timestamp": datetime.now(),
            "transcript": "Well, maybe I touched it but I didn't steal anything.",
            "analysis": {
                "credibility_score": 50,
                "confidence_level": "Medium",
                "overall_risk": "Medium-High", 
                "emotion_analysis": [{"label": "uncertain", "score": 0.6}],
                "linguistic_analysis": {
                    "hesitation_count": 7,
                    "speech_rate_wpm": 145,
                    "formality_score": 35
                },
                "risk_assessment": {"overall_risk": "Medium-High"},
                "deception_flags": ["contradictory_statements", "qualifying_language"]
            }
        }
    ]
    
    # Generate insights
    insights = generator.generate_session_insights(session_context, current_analysis, session_history)
    
    print("=== SESSION INSIGHTS TEST ===")
    print(f"Generated {len(insights)} insights:")
    print()
    
    for key, value in insights.items():
        print(f"🔍 {key.replace('_', ' ').title()}:")
        print(f"   {value}")
        print()
    
    return insights

if __name__ == "__main__":
    insights = test_session_insights()
    print("✅ Test completed successfully!")
