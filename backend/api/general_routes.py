from fastapi import APIRouter, Depends, HTTPException, Path, WebSocket, WebSocketDisconnect
from backend.models import AnalyzeResponse
import time
import os
from datetime import datetime

router = APIRouter()

@router.get(
    "/",
    tags=["General"],
    summary="API Root/Health Check",
    description="Basic health check endpoint to confirm the API is running."
)
async def root():
    # In main.py, this used app.version.
    # If app instance is not easily available here, a static message or version from elsewhere is fine.
    # For simplicity, returning a static message. If version is needed, it might require passing app or config.
    return {"message": "AI Lie Detector API is running"}

@router.get("/test-structured-output", response_model=AnalyzeResponse, tags=["Testing"])
async def test_structured_output():
    """Test endpoint that returns a complete structured response for frontend testing"""
    mock_response = {
        "session_id": "test-session-123",
        "speaker_name": "Test Speaker",
        "transcript": "This is a test transcript to verify the structured output display system is working correctly in the frontend application.",
        "audio_quality": {
            "duration": 5.2,
            "sample_rate": 44100,
            "channels": 1,
            "loudness": -20.5,
            "quality_score": 95
        },
        "emotion_analysis": [
            {"label": "neutral", "score": 0.7},
            {"label": "confidence", "score": 0.2},
            {"label": "slight_anxiety", "score": 0.1}
        ],
        "speaker_transcripts": {
            "Speaker 1": "This is a test transcript to verify the structured output display system is working correctly in the frontend application."
        },
        "red_flags_per_speaker": {
            "Speaker 1": [
                "Slightly elevated speech pace in middle section",
                "Brief pause before mentioning 'system'",
                "Minor vocal tension detected"
            ]
        },
        "credibility_score": 82,
        "confidence_level": "high",
        "gemini_summary": {
            "tone": "Professional and measured, with slight underlying tension suggesting awareness of being evaluated",
            "motivation": "Appears to be providing information for testing purposes with genuine intent to demonstrate system capabilities",
            "credibility": "High credibility overall with minor stress indicators typical of demonstration scenarios",
            "emotional_state": "Composed and focused, with slight performance anxiety which is normal for test scenarios",
            "communication_style": "Clear and articulate communication with professional vocabulary and structured delivery",
            "key_concerns": "Minor vocal tension suggests awareness of evaluation context; pace variations could indicate concentration on accuracy",
            "strengths": "Excellent clarity of speech; comprehensive information delivery; consistent tone throughout; professional presentation"
        },
        "recommendations": [
            "Continue with current communication approach as it demonstrates strong credibility",
            "Consider relaxation techniques if similar evaluation scenarios cause minor stress",
            "Maintain current level of detail and clarity in future communications"
        ],        "linguistic_analysis": {
            "speech_patterns": "Consistent rhythm with appropriate pauses; professional pacing with minor acceleration during technical terms",
            "word_choice": "Technical vocabulary used appropriately; precise language selection; professional terminology maintained throughout",
            "emotional_consistency": "Emotions align well with stated purpose; minor tension consistent with demonstration context",
            "detail_level": "Excellent level of detail provided; comprehensive coverage of topic without excessive elaboration",
            "word_count": 42,
            "hesitation_count": 2,
            "qualifier_count": 3,
            "certainty_count": 8,
            "filler_count": 1,
            "repetition_count": 0,
            "formality_score": 85,
            "complexity_score": 78,
            "avg_word_length": 5.2,
            "avg_words_per_sentence": 14.0,
            "sentence_count": 3,
            "confidence_ratio": 0.8
        },
        "risk_assessment": {
            "overall_risk": "low",
            "risk_factors": [
                "Minor performance anxiety in evaluation context",
                "Slight pace variations during technical descriptions"
            ],
            "mitigation_suggestions": [
                "No significant mitigation needed - patterns are normal for demonstration context",
                "Consider establishing comfort baseline before formal evaluations"
            ]
        },
        "session_insights": {
            "consistency_analysis": "First analysis in session - establishing baseline patterns for future comparison",
            "behavioral_evolution": "Initial session - no previous behavior patterns to compare",
            "risk_trajectory": "Starting at low risk level - good foundation for session",
            "conversation_dynamics": "Professional interaction with clear demonstration intent"
        }
    }
    
    return AnalyzeResponse(**mock_response)
