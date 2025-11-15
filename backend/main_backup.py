from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Path
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
import speech_recognition as sr
from transformers import pipeline
import tempfile
import os
import requests
import json
import logging
import time
from datetime import datetime
import uuid
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app_description = """
The AI Lie Detector API provides endpoints for analyzing audio content to detect potential deception.
It offers features like speech-to-text transcription, emotion analysis, and advanced AI-driven analysis using Google Gemini.
Session management is included to maintain conversation context.

**Key Features**:
- Audio analysis with deception indicators.
- Session-based conversation history and contextual analysis.
- Detailed breakdown of results including emotion, credibility, and linguistic patterns.
"""

app = FastAPI(
    title="AI Lie Detector API",
    version="1.0.1",
    description=app_description,
    contact={
        "name": "API Support",
        "email": "support@example.com", # Replace with actual contact
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)


# --- Pydantic Models for API Documentation ---

class AudioQualityMetrics(BaseModel):
    duration: float = Field(..., description="Duration of the audio in seconds.")
    sample_rate: int = Field(..., description="Sample rate of the audio in Hz.")
    channels: int = Field(..., description="Number of audio channels.")
    loudness: float = Field(..., description="Loudness of the audio in dBFS.")
    quality_score: int = Field(..., description="Overall quality score (0-100).")

class EmotionScore(BaseModel):
    label: str = Field(..., description="Emotion label (e.g., 'anger', 'joy').")
    score: float = Field(..., description="Confidence score for the emotion (0.0-1.0).")

class GeminiSummary(BaseModel):
    tone: str = Field(..., description="Detailed analysis of speaker's tone and manner.")
    motivation: str = Field(..., description="Assessment of underlying motivations and intent.")
    credibility: str = Field(..., description="Specific credibility assessment with reasoning.")
    emotional_state: str = Field(..., description="Emotional consistency and authenticity analysis.")
    communication_style: str = Field(..., description="Communication patterns and verbal behaviors.")
    key_concerns: str = Field(..., description="Main red flags or concerns identified.")
    strengths: str = Field(..., description="Aspects that support credibility.")

class LinguisticAnalysis(BaseModel):
    speech_patterns: str = Field(..., description="Analysis of speech rhythm, pace, pauses.")
    word_choice: str = Field(..., description="Analysis of vocabulary and phrasing choices.")
    emotional_consistency: str = Field(..., description="Consistency between claimed emotions and expression.")
    detail_level: str = Field(..., description="Appropriate level of detail vs vagueness.")

class RiskAssessment(BaseModel):
    overall_risk: str = Field(..., description="Overall risk level (low/medium/high).")
    risk_factors: List[str] = Field(..., description="Specific risk factors identified.")
    mitigation_suggestions: List[str] = Field(..., description="Suggestions to mitigate identified risks.")

class SessionInsights(BaseModel):
    consistency_analysis: str
    behavioral_evolution: str
    risk_trajectory: str
    conversation_dynamics: str

class AnalyzeResponse(BaseModel):
    session_id: str = Field(..., description="Unique identifier for the conversation session.")
    transcript: str = Field(..., description="Transcribed text from the audio.")
    audio_quality: AudioQualityMetrics = Field(..., description="Metrics related to the audio quality.")
    emotion_analysis: List[EmotionScore] = Field(..., description="List of detected emotions and their scores.")
    speaker_transcripts: Dict[str, str] = Field(..., description="Transcript content separated by speaker.")
    red_flags_per_speaker: Dict[str, List[str]] = Field(..., description="Deception indicators found for each speaker.")
    credibility_score: int = Field(..., description="Overall credibility score (0-100).")
    confidence_level: str = Field(..., description="Analysis confidence level (e.g., 'high', 'medium').")
    gemini_summary: GeminiSummary = Field(..., description="Detailed summary from Gemini AI analysis.")
    recommendations: List[str] = Field(..., description="Actionable recommendations based on the analysis.")
    linguistic_analysis: LinguisticAnalysis = Field(..., description="Analysis of linguistic patterns.")
    risk_assessment: RiskAssessment = Field(..., description="Risk assessment details.")
    session_insights: Optional[SessionInsights] = Field(None, description="Insights based on conversation history within the session.")
    # deception_flags: Optional[List[str]] = Field(None, description="Overall deception flags (legacy, if still used).")


class NewSessionResponse(BaseModel):
    session_id: str = Field(..., description="Unique identifier for the newly created session.")
    message: str = Field(..., description="Confirmation message.")

class SessionHistoryItem(BaseModel):
    timestamp: datetime = Field(..., description="Timestamp of the analysis.")
    transcript: str = Field(..., description="Transcript of this analysis entry.")
    analysis: Dict[str, Any] = Field(..., description="A summary or key parts of the analysis result for this entry.") # Could be more specific if needed
    analysis_number: int = Field(..., description="Sequential number of this analysis in the session.")

class SessionHistoryResponse(BaseModel):
    session_id: str = Field(..., description="Session ID for the history.")
    history: List[SessionHistoryItem] = Field(..., description="List of analysis entries in the session.")

class DeleteSessionResponse(BaseModel):
    session_id: str = Field(..., description="ID of the deleted session.")
    message: str = Field(..., description="Confirmation message of deletion.")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Detailed error message.")


# --- Conversation History Management ---
class ConversationHistory:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        if not session_id:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now(),
                "history": [],
                "analysis_count": 0,
                # "context": {} # Context seems to be generated on the fly, not stored directly
            }
        return session_id
    
    def add_analysis(self, session_id: str, transcript: str, analysis_result: Dict[str, Any]):
        if session_id not in self.sessions:
            self.get_or_create_session(session_id) # Should not happen if session_id is from get_or_create_session
        
        session = self.sessions[session_id]
        session["analysis_count"] += 1

        # Storing a summary for history, not the full massive result, to prevent bloat
        history_entry = {
            "timestamp": datetime.now(),
            "transcript": transcript,
            "analysis_summary": { # Store a subset of the analysis for history
                "credibility_score": analysis_result.get("credibility_score"),
                "overall_risk": analysis_result.get("risk_assessment", {}).get("overall_risk"),
                "top_emotion": analysis_result.get("emotion_analysis", [{}])[0].get("label") if analysis_result.get("emotion_analysis") else None,
                # Consider adding other fields like 'deception_flags' to this summary
                # if they are crucial for generating 'recent_patterns' in get_session_context,
                # as _extract_patterns currently expects them in the 'analysis' dict.
            },
            "analysis_number": session["analysis_count"]
        }
        session["history"].append(history_entry)
        
        # Keep only last 10 analyses to prevent memory bloat
        if len(session["history"]) > 10:
            session["history"] = session["history"][-10:]

    def get_session_history_for_api(self, session_id: str) -> List[Dict[str, Any]]:
        session = self.sessions.get(session_id)
        if not session:
            return []
        return session.get("history", [])

    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            return {} # Or raise error
        
        session = self.sessions[session_id]
        # Ensure history items are correctly structured for _extract_patterns
        history_for_patterns = []
        for h_entry in session.get("history", []):
            # We need to reconstruct parts of the analysis structure that _extract_patterns expects
            # This is a bit of a workaround due to storing only summaries.
            # For full pattern analysis, storing more detailed history might be needed.
            reconstructed_analysis = {
                "deception_flags": h_entry.get("analysis_summary",{}).get("deception_flags", []), # Assuming this might be added to summary
                "emotion_analysis": [{"label": h_entry.get("analysis_summary",{}).get("top_emotion", "unknown"), "score": 1.0}] if h_entry.get("analysis_summary",{}).get("top_emotion") else [],
                "gemini_analysis": {"credibility_score": h_entry.get("analysis_summary",{}).get("credibility_score")} if h_entry.get("analysis_summary",{}).get("credibility_score") is not None else {}
            }
            history_for_patterns.append({"analysis": reconstructed_analysis})


        return {
            "previous_analyses": len(session.get("history", [])),
            "session_duration": (datetime.now() - session.get("created_at", datetime.now())).total_seconds() / 60,  # minutes
            "recent_transcripts": [h["transcript"] for h in session.get("history", [])[-3:]],
            "recent_patterns": self._extract_patterns(history_for_patterns[-5:])
        }
    
    def _extract_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, Any]: # history here expects items with an "analysis" key
        patterns: Dict[str, Any] = {
            "recurring_deception_flags": {},
            "emotion_trends": {},
            "credibility_trend": []
        }
        
        for entry in history: # entry is expected to be like {"analysis": actual_analysis_data}
            analysis = entry.get("analysis", {})
            
            flags = analysis.get("deception_flags", [])
            for flag in flags:
                flag_type = flag.split(":")[0] if ":" in flag else flag
                patterns["recurring_deception_flags"][flag_type] = patterns["recurring_deception_flags"].get(flag_type, 0) + 1
            
            emotions = analysis.get("emotion_analysis", []) # This expects list of emotion dicts
            if emotions and isinstance(emotions, list) and len(emotions) > 0:
                # emotion_data = emotions[0] if isinstance(emotions[0], list) else emotions
                # The above line seems problematic if emotions is already List[EmotionScore]
                # Assuming emotions is List[Dict] e.g. [{"label": "happy", "score": 0.9}]
                top_emotion = max(emotions, key=lambda x: x.get("score", 0)) if emotions else None
                if top_emotion:
                    emotion_name = top_emotion.get("label", "unknown")
                    patterns["emotion_trends"][emotion_name] = patterns["emotion_trends"].get(emotion_name, 0) + 1
            
            gemini_analysis = analysis.get("gemini_analysis", {}) # This expects {"credibility_score": X}
            if isinstance(gemini_analysis, dict) and "credibility_score" in gemini_analysis:
                patterns["credibility_trend"].append(gemini_analysis["credibility_score"])
        
        return patterns

# Global conversation history manager
conversation_history = ConversationHistory()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=7, return_all_scores=True)
gemini_api_key = os.getenv("GEMINI_API_KEY", "")  # fallback key

def query_gemini(transcript, flags, session_id: str = None):
    if not gemini_api_key:
        return {"error": "Missing Gemini API key"}

    # Get session context for conversation continuity
    session_context = conversation_history.get_session_context(session_id) if session_id else {}
    
    # Build enhanced prompt with conversation history
    base_prompt = f"""
    Analyze the transcript for deception, stress, and speaker separation. 

    CURRENT TRANSCRIPT:
    {transcript}

    RED FLAGS FROM PRIMARY ANALYSIS:
    {json.dumps(flags, indent=2)}
    """
    
    # Add conversation context if available
    if session_context and session_context.get("previous_analyses", 0) > 0:
        context_prompt = f"""
        
    CONVERSATION CONTEXT (Session Analysis #{session_context.get('previous_analyses', 0) + 1}):
    - Session Duration: {session_context.get('session_duration', 0):.1f} minutes
    - Previous Analyses: {session_context.get('previous_analyses', 0)}
    
    RECENT CONVERSATION HISTORY:
    {json.dumps(session_context.get('recent_transcripts', []), indent=2)}
    
    PATTERN ANALYSIS FROM SESSION:
    - Recurring Deception Patterns: {json.dumps(session_context.get('recent_patterns', {}).get('recurring_deception_flags', {}), indent=2)}
    - Emotional Trends: {json.dumps(session_context.get('recent_patterns', {}).get('emotion_trends', {}), indent=2)}
    - Credibility Score Trend: {session_context.get('recent_patterns', {}).get('credibility_trend', [])}
    
    INSTRUCTIONS FOR CONTEXTUAL ANALYSIS:
    - Compare current statement with previous statements in this session
    - Look for consistency/inconsistency patterns across the conversation
    - Note any escalation or de-escalation in deception indicators
        - Consider if the speaker is becoming more or less credible over time
    - Identify if they are reinforcing previous statements or contradicting them    """
        base_prompt += context_prompt
    
    full_prompt = base_prompt + """
    
    You MUST return a valid JSON response with the following EXACT structure. Do not include any text before or after the JSON:

    {
        "speaker_transcripts": {"Speaker 1": "text content for this speaker"},
        "red_flags_per_speaker": {"Speaker 1": ["specific deception indicators found"]},
        "credibility_score": 75,
        "confidence_level": "high",
        "gemini_summary": {
            "tone": "detailed analysis of speaker's tone and manner",
            "motivation": "assessment of underlying motivations and intent",
            "credibility": "specific credibility assessment with reasoning",
            "emotional_state": "emotional consistency and authenticity analysis",
            "communication_style": "communication patterns and verbal behaviors",
            "key_concerns": "main red flags or concerns identified",
            "strengths": "aspects that support credibility"
        },
        "recommendations": [
            "specific actionable recommendation 1",
            "specific actionable recommendation 2"
        ],
        "linguistic_analysis": {
            "speech_patterns": "analysis of speech rhythm, pace, pauses",
            "word_choice": "analysis of vocabulary and phrasing choices",
            "emotional_consistency": "consistency between claimed emotions and expression",
            "detail_level": "appropriate level of detail vs vagueness"
        },
        "risk_assessment": {
            "overall_risk": "low/medium/high",
            "risk_factors": ["specific risk factor 1", "specific risk factor 2"],
            "mitigation_suggestions": ["suggestion 1", "suggestion 2"]
        }
    }

    CRITICAL REQUIREMENTS:
    - Return ONLY valid JSON, no markdown formatting, no ```json blocks
    - All string values must be meaningful, not placeholder text
    - credibility_score must be integer 0-100
    - confidence_level must be: "very_low", "low", "medium", "high", "very_high"
    - overall_risk must be: "low", "medium", "high"
    - All arrays must contain at least 1 meaningful item
    - All object fields must be present and non-empty
    """# Correct Gemini API URL and authentication
    gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 3072  # Increased for more detailed contextual analysis
        }
    }
    try:
        response = requests.post(gemini_api_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            gemini_response = response.json()
            logger.info(f"Gemini API response structure: {json.dumps(gemini_response, indent=2)[:500]}...")
            
            # Safely navigate the response structure
            if 'candidates' not in gemini_response:
                return {"error": "No candidates in Gemini response", "gemini_raw_response": gemini_response}
            
            candidates = gemini_response['candidates']
            if not isinstance(candidates, list) or len(candidates) == 0:
                return {"error": "Invalid candidates structure in Gemini response", "gemini_raw_response": gemini_response}
            
            candidate = candidates[0]
            if 'content' not in candidate:
                return {"error": "No content in Gemini candidate", "gemini_raw_response": gemini_response}
            
            content = candidate['content']
            if 'parts' not in content:
                return {"error": "No parts in Gemini content", "gemini_raw_response": gemini_response}
            
            parts = content['parts']
            if not isinstance(parts, list) or len(parts) == 0:
                return {"error": "Invalid parts structure in Gemini content", "gemini_raw_response": gemini_response}
            
            part = parts[0]
            if 'text' not in part:
                return {"error": "No text in Gemini part", "gemini_raw_response": gemini_response}
            
            text = part['text']
            
            # Remove markdown code block formatting if present
            if text.strip().startswith('```json'):
                text = text.strip()
                # Find the JSON content between ```json and ```
                start = text.find('```json') + 7
                end = text.rfind('```')
                if end > start:
                    text = text[start:end].strip()
            elif text.strip().startswith('```'):
                text = text.strip()
                # Handle generic code blocks
                start = text.find('```') + 3
                end = text.rfind('```')
                if end > start:
                    text = text[start:end].strip()
            
            try:
                return json.loads(text)
            except json.JSONDecodeError as e:
                return {
                    "error": f"Failed to parse Gemini JSON response: {str(e)}",
                    "gemini_text": text,
                    "gemini_raw_response": gemini_response
                }
        else:
            return {"error": f"Gemini API error: {response.status_code} - {response.text}"}
    except Exception as e:
        logger.error(f"Exception in query_gemini: {str(e)}")
        return {"error": f"Gemini request error: {str(e)}"}

def validate_and_structure_gemini_response(raw_response, transcript, session_context=None):
    """
    Validate and ensure structured response from Gemini API with fallbacks
    """
    default_structure = {
        "speaker_transcripts": {"Speaker 1": transcript},
        "red_flags_per_speaker": {"Speaker 1": []},
        "credibility_score": 50,
        "confidence_level": "medium",
        "gemini_summary": {
            "tone": "Analysis pending - technical issue encountered",
            "motivation": "Unable to determine - requires manual review",
            "credibility": "Inconclusive - technical analysis limitation",
            "emotional_state": "Analysis incomplete",
            "communication_style": "Requires further analysis",
            "key_concerns": "Technical analysis limitation",
            "strengths": "Unable to assess automatically"
        },
        "recommendations": [
            "Manual review recommended due to technical analysis limitations",
            "Consider re-running analysis with different audio quality"
        ],
        "linguistic_analysis": {
            "speech_patterns": "Analysis incomplete",
            "word_choice": "Requires manual review",
            "emotional_consistency": "Unable to assess",
            "detail_level": "Analysis pending"
        },
        "risk_assessment": {
            "overall_risk": "medium",
            "risk_factors": ["Technical analysis limitation"],
            "mitigation_suggestions": ["Manual review recommended"]
        }
    }
    
    # If raw_response has an error, return structured default
    if isinstance(raw_response, dict) and raw_response.get('error'):
        logger.warning(f"Gemini API error, using default structure: {raw_response.get('error')}")
        return default_structure
    
    # Validate required top-level fields
    required_fields = ['speaker_transcripts', 'red_flags_per_speaker', 'credibility_score', 
                      'gemini_summary', 'recommendations', 'linguistic_analysis', 'risk_assessment']
    
    validated_response = {}
    
    for field in required_fields:
        if field in raw_response:
            validated_response[field] = raw_response[field]
        else:
            validated_response[field] = default_structure[field]
            logger.warning(f"Missing field '{field}' in Gemini response, using default")
    
    # Validate and fix credibility_score
    try:
        score = int(validated_response['credibility_score'])
        validated_response['credibility_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        validated_response['credibility_score'] = 50
        logger.warning("Invalid credibility_score, defaulting to 50")
    
    # Validate confidence_level
    valid_confidence_levels = ["very_low", "low", "medium", "high", "very_high"]
    if validated_response.get('confidence_level') not in valid_confidence_levels:
        validated_response['confidence_level'] = "medium"
    
    # Validate gemini_summary structure
    required_summary_fields = ['tone', 'motivation', 'credibility', 'emotional_state', 
                              'communication_style', 'key_concerns', 'strengths']
    
    if not isinstance(validated_response['gemini_summary'], dict):
        validated_response['gemini_summary'] = default_structure['gemini_summary']
    else:
        for summary_field in required_summary_fields:
            if summary_field not in validated_response['gemini_summary'] or not validated_response['gemini_summary'][summary_field]:
                validated_response['gemini_summary'][summary_field] = default_structure['gemini_summary'][summary_field]
    
    # Validate risk_assessment
    if not isinstance(validated_response['risk_assessment'], dict):
        validated_response['risk_assessment'] = default_structure['risk_assessment']
    else:
        valid_risk_levels = ["low", "medium", "high"]
        if validated_response['risk_assessment'].get('overall_risk') not in valid_risk_levels:
            validated_response['risk_assessment']['overall_risk'] = "medium"
        
        if not isinstance(validated_response['risk_assessment'].get('risk_factors'), list):
            validated_response['risk_assessment']['risk_factors'] = default_structure['risk_assessment']['risk_factors']
        
        if not isinstance(validated_response['risk_assessment'].get('mitigation_suggestions'), list):
            validated_response['risk_assessment']['mitigation_suggestions'] = default_structure['risk_assessment']['mitigation_suggestions']
    
    # Ensure arrays are not empty
    if not isinstance(validated_response['recommendations'], list) or len(validated_response['recommendations']) == 0:
        validated_response['recommendations'] = default_structure['recommendations']
    
    # Add session insights if session context is available
    if session_context and len(session_context.get('previous_analyses', [])) > 0:
        validated_response['session_insights'] = raw_response.get('session_insights', {
            "consistency_analysis": "Multiple analyses available for comparison",
            "behavioral_evolution": "Tracking patterns across conversation",
            "risk_trajectory": "Monitoring risk changes over time",
            "conversation_dynamics": "Analyzing ongoing conversation patterns"
        })
    
    return validated_response

# Audio quality assessment function
def assess_audio_quality(audio_segment):
    """Assess the quality of the audio for better analysis"""
    quality_metrics = {
        "duration": len(audio_segment) / 1000.0,  # seconds
        "sample_rate": audio_segment.frame_rate,
        "channels": audio_segment.channels,
        "loudness": audio_segment.dBFS,
        "quality_score": 0
    }
    
    # Calculate quality score
    if quality_metrics["duration"] >= 1.0:  # At least 1 second
        quality_metrics["quality_score"] += 25
    if quality_metrics["sample_rate"] >= 16000:  # Good sample rate
        quality_metrics["quality_score"] += 25
    if quality_metrics["loudness"] > -30:  # Not too quiet
        quality_metrics["quality_score"] += 25
    if quality_metrics["channels"] >= 1:  # Has audio channels
        quality_metrics["quality_score"] += 25
    
    return quality_metrics

# Main analyze endpoint
@app.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"],
          summary="Analyze Audio File",
          description="Uploads an audio file and performs a comprehensive analysis for deception, emotion, and other speech patterns. Returns detailed results including a transcript, audio quality assessment, emotion scores, and AI-driven insights.",
          responses={
              200: {"description": "Successful analysis"},
              400: {"model": ErrorResponse, "description": "Invalid input (e.g., not an audio file, file too short)."},
              422: {"model": ErrorResponse, "description": "Validation error (e.g., invalid file type by content)."}, # FastAPI's default for validation
              500: {"model": ErrorResponse, "description": "Internal server error during analysis."}
          })
async def analyze_audio(
    audio: UploadFile = File(..., description="Audio file to be analyzed (WAV, MP3, OGG, WEBM). Max size 10MB."),
    session_id: Optional[str] = Form(None, description="Optional session ID for conversation continuity. If not provided, a new session may be created implicitly depending on server logic.")
):
    try:
        logger.info(f"Starting analysis for session: {session_id if session_id else 'New/Implicit Session'}")
          # Validate file type
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Get or create session
        if not session_id:
            session_id = conversation_history.get_or_create_session()
        else:
            conversation_history.get_or_create_session(session_id)
        
        # Get or create session
        if not session_id:
            session_id = conversation_history.get_or_create_session()
        else:
            conversation_history.get_or_create_session(session_id)

        audio_content = await audio.read()
        # File size check (approximate, as UploadFile might have already spooled to disk for large files)
        # Consider that audio.size is available if a SpooledTemporaryFile was used by FastAPI
        file_size = audio.size if hasattr(audio, 'size') and audio.size is not None else len(audio_content)

        logger.info(f"Received audio file: {audio.filename or 'unnamed'}, Content-Type: {audio.content_type}, Size: {file_size} bytes")

        if file_size > 15 * 1024 * 1024: # Approx 15MB limit warning
            logger.warning(f"File size {file_size} bytes exceeds 15MB. This might lead to performance issues.")
            # Optionally, raise HTTPException for very large files if strict limits are needed
            # raise HTTPException(status_code=413, detail="File too large. Maximum size is 15MB.")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename or "")[1] or ".tmp") as temp_audio:
            temp_audio.write(audio_content)
            temp_audio_path = temp_audio.name
        del audio_content # Free memory if possible

        try:
            # Convert audio to a standard format using pydub
            audio_segment = AudioSegment.from_file(temp_audio_path)
            
            # Assess audio quality
            audio_quality = assess_audio_quality(audio_segment)
            logger.info(f"Audio quality metrics: {audio_quality}")
            
            # Convert to WAV for speech recognition
            wav_path = temp_audio_path.replace('.wav', '_converted.wav')
            audio_segment.export(wav_path, format="wav")
            
            # Speech recognition
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                try:
                    transcript = recognizer.recognize_google(audio_data)
                    logger.info(f"Transcript generated: \"{transcript[:100]}...\"") # Log snippet                except sr.UnknownValueError:
                    logger.warning(f"Speech recognition: Could not understand audio from file {audio.filename or 'unnamed'}.")
                    raise HTTPException(status_code=400, detail="Could not understand the audio. Please ensure clear speech and good audio quality.")
                except sr.RequestError as e:
                    logger.error(f"Speech recognition service error for file {audio.filename or 'unnamed'}: {e}")
                    raise HTTPException(status_code=503, detail=f"Speech recognition service error: {e}") # 503 Service Unavailable

            if not transcript or len(transcript.strip()) < 10: # Check after attempting transcription
                logger.warning(f"Transcript too short or empty for file {audio.filename or 'unnamed'}: '{transcript}'")
                raise HTTPException(status_code=400, detail="Transcript too short or empty. Please provide longer audio with clear speech (min 10 characters after transcription).")

            # Emotion analysis
            try:
                emotions = emotion_classifier(transcript)
                if isinstance(emotions, list) and len(emotions) > 0:
                    emotion_scores = emotions[0] if isinstance(emotions[0], list) else emotions
                else:
                    emotion_scores = [{"label": "neutral", "score": 0.5}]
            except Exception as e:
                logger.warning(f"Emotion analysis failed: {e}")
                emotion_scores = [{"label": "neutral", "score": 0.5}]

            # Get session context for Gemini analysis
            session_context = conversation_history.get_session_context(session_id)
            
            # Query Gemini for comprehensive analysis
            logger.info("Querying Gemini for analysis...")
            gemini_response = query_gemini(transcript, session_context)
            
            # Validate and structure the Gemini response
            validated_analysis = validate_and_structure_gemini_response(gemini_response, session_context)
            
            logger.info("Analysis completed successfully")

            # Prepare final response
            result = {
                "session_id": session_id,
                "transcript": transcript,
                "audio_quality": audio_quality,
                "emotion_analysis": emotion_scores,
                **validated_analysis  # Include all validated structured fields
            }

            # Add to conversation history
            conversation_history.add_analysis(session_id, transcript, result) # result is a dict here
            
            return AnalyzeResponse(**result) # Validate and return with Pydantic model

        finally:
            # Clean up temporary files
            try:
                os.unlink(temp_audio_path)
                if 'wav_path' in locals():
                    os.unlink(wav_path)
            except OSError:
                logger.warning(f"Could not delete temporary file {temp_audio_path} or {locals().get('wav_path')}")


    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analysis endpoint: {str(e)}", exc_info=True)
        # Ensure this error is also in the defined ErrorResponse schema for consistency in docs
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during analysis: {str(e)}")


# Session management endpoints
@app.post("/session/new", response_model=NewSessionResponse, tags=["Session Management"],
          summary="Create New Session",
          description="Initializes a new conversation session and returns a unique session ID.",
          responses={
              500: {"model": ErrorResponse, "description": "Internal server error during session creation."}
          })
async def create_new_session_endpoint():
    session_id = conversation_history.get_or_create_session()
    return NewSessionResponse(session_id=session_id, message="New session created successfully.")

@app.get("/session/{session_id}/history", response_model=SessionHistoryResponse, tags=["Session Management"],
         summary="Get Session History",
         description="Retrieves the conversation history for a given session ID. History includes summaries of past analyses.",
         responses={
             404: {"model": ErrorResponse, "description": "Session not found."},
             500: {"model": ErrorResponse, "description": "Internal server error."}
         })
async def get_session_history_endpoint(session_id: str = Path(..., description="The ID of the session to retrieve history for.")):
    history_items = conversation_history.get_session_history_for_api(session_id)
    if not conversation_history.sessions.get(session_id) and not history_items : # Check if session ever existed or if history is empty for an existing session.
        #This condition might need refinement based on whether an empty history for an existing session is a 404 or empty list.
        #Assuming if session_id is not in .sessions, it's a 404.
        if session_id not in conversation_history.sessions:
            raise HTTPException(status_code=404, detail=f"Session ID '{session_id}' not found.")

    return SessionHistoryResponse(session_id=session_id, history=[SessionHistoryItem(**item) for item in history_items])

@app.delete("/session/{session_id}", response_model=DeleteSessionResponse, tags=["Session Management"],
            summary="Delete Session",
            description="Deletes all data associated with a given session ID.",
            responses={
                404: {"model": ErrorResponse, "description": "Session not found."},
                500: {"model": ErrorResponse, "description": "Internal server error."}
            })
async def delete_session_endpoint(session_id: str = Path(..., description="The ID of the session to delete.")):
    if not conversation_history.delete_session(session_id):
        raise HTTPException(status_code=404, detail=f"Session ID '{session_id}' not found or already deleted.")
    return DeleteSessionResponse(session_id=session_id, message="Session deleted successfully.")


@app.get("/", tags=["General"], summary="API Root/Health Check",
         description="Basic health check endpoint to confirm the API is running.")
async def root():
    return {"message": "AI Lie Detector API is running", "version": app.version}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
