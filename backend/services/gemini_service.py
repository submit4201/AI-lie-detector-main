import json
import requests
import logging
import base64
import os
import asyncio
from typing import Dict, Any, Optional, List
import httpx # Added
import json # Ensure json is imported for JSONDecodeError

from backend.config import GEMINI_API_KEY
from backend.services.json_utils import parse_gemini_response, safe_json_parse, create_fallback_response, extract_text_from_gemini_response

from backend.models import (
    ManipulationAssessment, ArgumentAnalysis, SpeakerAttitude, EnhancedUnderstanding,
    PsychologicalAnalysis, AudioAnalysis, InteractionMetrics, ConversationFlow,
    EmotionDetail, LinguisticAnalysis
)
from backend.services.manipulation_service import ManipulationService
from backend.services.argument_service import ArgumentService
from backend.services.speaker_attitude_service import SpeakerAttitudeService
from backend.services.enhanced_understanding_service import EnhancedUnderstandingService
from backend.services.psychological_service import PsychologicalService
from backend.services.audio_analysis_service import AudioAnalysisService
# from backend.services.interaction_metrics_service import InteractionMetricsService # File does not exist
from backend.services.conversation_flow_service import ConversationFlowService
# from backend.services.linguistic_service import analyze_linguistic_patterns # Causes circular import - import locally where needed

logger = logging.getLogger(__name__)

# Security: Utility function to sanitize sensitive data in logs
def _sanitize_for_logging(data: Any, max_length: int = 50) -> str:
    """
    Sanitize sensitive data for logging purposes.
    Returns a safe string representation without exposing sensitive content.
    """
    if data is None:
        return "None"
    
    data_type = type(data).__name__
    
    if isinstance(data, str):
        if len(data) > max_length:
            return f"<{data_type}: {len(data)} chars (truncated for security)>"
        return f"<{data_type}: {len(data)} chars>"
    elif isinstance(data, (dict, list)):
        return f"<{data_type}: {len(data)} items>"
    elif isinstance(data, bytes):
        return f"<bytes: {len(data)} bytes>"
    else:
        return f"<{data_type}>"

# Define GeminiService class
class GeminiService:
    async def query_gemini_for_raw_json(self, prompt: str, max_output_tokens: int = 2048) -> Optional[Dict[str, Any]]:
        logger.info(f"GeminiService.query_gemini_for_raw_json sending prompt {_sanitize_for_logging(prompt)}")
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not configured.")
            return None

        gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.5, 
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": max_output_tokens,
                "response_mime_type": "application/json", 
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(gemini_api_url, json=payload, headers=headers, timeout=120.0) 

            if response.status_code == 200:
                response_data = response.json()
                
                extracted_text = extract_text_from_gemini_response(response_data)
                if extracted_text:
                    parsed_json = safe_json_parse(extracted_text)
                    if isinstance(parsed_json, dict) and not parsed_json.get("error"):
                        logger.info("Successfully received and parsed JSON response from Gemini.")
                        return parsed_json
                    else:
                        logger.error(f"Failed to parse JSON from Gemini response or parsed data is an error. Parsed data structure: {_sanitize_for_logging(parsed_json)}")
                        return None 
                elif (response_data.get('candidates') and
                      response_data['candidates'][0].get('content') and
                      response_data['candidates'][0]['content'].get('parts') and
                      isinstance(response_data['candidates'][0]['content']['parts'][0], dict) and
                      "text" not in response_data['candidates'][0]['content']['parts'][0]):
                    
                    potential_json_obj = response_data['candidates'][0]['content']['parts'][0]
                    if isinstance(potential_json_obj, dict):
                         logger.info("Successfully received direct JSON object from Gemini.")
                         return potential_json_obj
                    else:
                        logger.error(f"Gemini response part was not a dict as expected for direct JSON. Part type: {_sanitize_for_logging(potential_json_obj)}")
                        return None
                else:
                    logger.error(f"Could not extract text or direct JSON from Gemini response. Response structure: {_sanitize_for_logging(response_data)}")
                    return None

            else:
                logger.error(f"Gemini API request failed with status code {response.status_code}")
                return None

        except httpx.ReadTimeout:
            logger.error("Gemini API request timed out.")
            return None
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting Gemini API: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from Gemini response: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred in query_gemini_for_raw_json: {e}", exc_info=True)
            return None

def query_gemini_with_audio(audio_path: str, transcript: str, flags: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Enhanced Gemini query that includes both audio data and transcript for more comprehensive analysis
    """
    if not GEMINI_API_KEY:
        logger.error("Missing Gemini API key. Cannot query Gemini.")
        return {"error": "Missing Gemini API key"}

    try:
        # Read and encode audio file
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
        
        # Encode audio to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Determine audio MIME type based on file extension
        file_ext = os.path.splitext(audio_path)[1].lower()
        mime_type_map = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg', 
            '.m4a': 'audio/mp4',
            '.ogg': 'audio/ogg',
            '.webm': 'audio/webm',
            '.flac': 'audio/flac'
        }
        mime_type = mime_type_map.get(file_ext, 'audio/wav')
        
        base_prompt = f"""
        Analyze the provided audio file for deception, stress, vocal patterns, and speaker characteristics.
        
        You have access to both the audio file and its transcription. Use the audio to analyze:
        - Vocal stress indicators (pitch variations, speaking rate changes)
        - Hesitation patterns and pause analysis
        - Voice quality and emotional undertones
        - Vocal authenticity vs. performance
        - Micro-expressions in speech
        - Breathing patterns and vocal tension
        
        TRANSCRIPT FOR REFERENCE:
        {transcript}

        INITIAL DECEPTION FLAGS DETECTED:
        {json.dumps(flags, indent=2)}
        """

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
        - Compare current vocal patterns with previous recordings in this session
        - Look for consistency/inconsistency patterns across the conversation  
        - Note any escalation or de-escalation in vocal stress indicators
        - Consider if the speaker's voice is becoming more or less authentic over time
        - Identify if vocal patterns support or contradict previous statements
        """
            base_prompt += context_prompt

        full_prompt = base_prompt + """

        Perform a comprehensive audio-based lie detection analysis and return a valid JSON response with the following EXACT structure:

        {
            "speaker_transcripts": {"Speaker 1": "text content for this speaker"},
            "red_flags_per_speaker": {"Speaker 1": ["specific vocal and behavioral deception indicators found"]},
            "credibility_score": 75,
            "confidence_level": "high",
            "gemini_summary": {
                "tone": "detailed analysis of speaker's vocal tone, pitch, and delivery",
                "motivation": "assessment of underlying motivations based on vocal cues and content",
                "credibility": "vocal authenticity assessment with specific reasoning",
                "emotional_state": "emotional consistency between voice and words",
                "communication_style": "vocal patterns, rhythm, and speaking style analysis",
                "key_concerns": "main vocal stress and deception indicators identified",
                "strengths": "vocal aspects that support credibility and authenticity"
            },
            "recommendations": [
                "specific actionable recommendation based on vocal analysis",
                "follow-up questions or verification steps"
            ],
            "linguistic_analysis": {
                "speech_patterns": "analysis of vocal rhythm, pace, pauses, hesitations",
                "word_choice": "vocabulary analysis combined with vocal delivery", 
                "emotional_consistency": "alignment between vocal emotion and content",
                "detail_level": "vocal confidence in details vs. vague responses"
            },
            "risk_assessment": {
                "overall_risk": "low/medium/high",
                "risk_factors": ["specific vocal risk indicators", "behavioral concerns from audio"],
                "mitigation_suggestions": ["verification steps", "follow-up recommendations"]
            },
            "audio_analysis": {
                "vocal_stress_indicators": "specific vocal stress patterns detected",
                "speaking_rate_variations": "changes in speaking speed and fluency",
                "pitch_analysis": "pitch variations and emotional undertones",
                "pause_patterns": "significant pauses, hesitations, or interruptions",
                "voice_quality": "overall voice quality and authenticity assessment"
            },
            "manipulation_assessment": {
                "manipulation_score": 0,
                "manipulation_tactics": ["e.g., gaslighting, guilt-tripping"],
                "manipulation_explanation": "explanation of manipulative tactics used",
                "example_phrases": ["specific phrases indicating manipulation"]
            },
            "argument_analysis": {
                "argument_strengths": ["speaker's strong points"],
                "argument_weaknesses": ["speaker's weak points"],
                "overall_argument_coherence_score": 0
            },
            "speaker_attitude": {
                "respect_level_score": 0,
                "sarcasm_detected": false,
                "sarcasm_confidence_score": 0,
                "tone_indicators_respect_sarcasm": ["words/phrases indicating respect/sarcasm"]
            },
            "enhanced_understanding": {
                "key_inconsistencies": ["list of contradictions"],
                "areas_of_evasiveness": ["topics speaker avoided"],
                "suggested_follow_up_questions": ["questions to ask for clarity"],
                "unverified_claims": ["claims needing fact-checking"]
            }
        }

        DETAILED INSTRUCTIONS FOR NEW SECTIONS:
        - Manipulation Assessment: Analyze for manipulative language. Provide a score (0-100 for manipulation likelihood), list identified tactics (e.g., gaslighting, guilt-tripping), explain why, and list example phrases.
        - Argument Analysis: Assess the strengths and weaknesses of the speaker's arguments. Provide lists for strengths and weaknesses, and an overall coherence score (0-100).
        - Speaker Attitude: Evaluate the speaker's tone for respect and sarcasm. Provide a respect score (0-100, high is respectful), indicate if sarcasm is detected (true/false) with a confidence score (0-100 if true), and list contributing tone indicators. Use audio cues heavily for this.
        - Enhanced Understanding: Identify elements for deeper insight. List key inconsistencies, areas of evasiveness, 2-3 suggested follow-up questions, and any unverified claims made by the speaker.

        CRITICAL REQUIREMENTS:
        - Return ONLY valid JSON, no markdown formatting, no ```json blocks
        - Use the audio file to enhance all analysis beyond just the transcript
        - All string values must be meaningful and based on actual audio analysis
        - credibility_score, manipulation_score, overall_argument_coherence_score, respect_level_score, sarcasm_confidence_score must be integers 0-100
        - confidence_level must be: "very_low", "low", "medium", "high", "very_high"
        - overall_risk must be: "low", "medium", "high"
        - sarcasm_detected must be boolean (true/false)
        - Include specific vocal observations in all analysis sections
        - All arrays must contain at least 1 meaningful item (use an empty array [] if no items apply, but ensure the field is present)
        - All new fields (manipulation_assessment, argument_analysis, speaker_attitude, enhanced_understanding) and their sub-fields are MANDATORY and must be correctly formatted.
        """

        gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [
                    {"text": full_prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": audio_base64
                        }
                    }
                ]
            }],            "generationConfig": {
                "temperature": 0.7,
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 4096  # Increased for detailed audio analysis
            }
        }
        
        logger.info(f"Sending audio analysis request to Gemini with {len(audio_data)} bytes of audio data")
        response = requests.post(gemini_api_url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            gemini_response = response.json()
            logger.info(f"Gemini audio analysis response received")
            
            # Use centralized JSON parsing
            result = parse_gemini_response(gemini_response, allow_partial=True)
            
            if result.get('error'):
                logger.warning(f"Gemini response parsing failed: {result.get('error')}")
                # Still return the result - it contains debug info
            else:
                logger.info("Successfully parsed Gemini audio analysis response")
            
            return result
        else:
            logger.error(f"Gemini API error: {response.status_code}")
            return create_fallback_response(f"Gemini API error: {response.status_code}", "API request failed")
            
    except Exception as e:
        logger.error(f"Exception in query_gemini_with_audio: {type(e).__name__}", exc_info=True)
        return {"error": f"Gemini audio analysis error: {str(e)}"}


def query_gemini(transcript: str, flags: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not GEMINI_API_KEY: # Check against placeholder
        logger.error("Missing Gemini API key. Cannot query Gemini.")
        return {"error": "Missing Gemini API key"}

    base_prompt = f"""
    Analyze the transcript for deception, stress, and speaker separation.

    CURRENT TRANSCRIPT:
    {transcript}

    RED FLAGS FROM PRIMARY ANALYSIS:
    {json.dumps(flags, indent=2)}
    """

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
        },
        "manipulation_assessment": {
            "manipulation_score": 0,
            "manipulation_tactics": ["e.g., gaslighting, guilt-tripping"],
            "manipulation_explanation": "explanation of manipulative tactics used",
            "example_phrases": ["specific phrases indicating manipulation"]
        },
        "argument_analysis": {
            "argument_strengths": ["speaker's strong points"],
            "argument_weaknesses": ["speaker's weak points"],
            "overall_argument_coherence_score": 0
        },
        "speaker_attitude": {
            "respect_level_score": 0,
            "sarcasm_detected": false,
            "sarcasm_confidence_score": 0,
            "tone_indicators_respect_sarcasm": ["words/phrases indicating respect/sarcasm"]
        },
        "enhanced_understanding": {
            "key_inconsistencies": ["list of contradictions"],
            "areas_of_evasiveness": ["topics speaker avoided"],
            "suggested_follow_up_questions": ["questions to ask for clarity"],
            "unverified_claims": ["claims needing fact-checking"]
        },
        "quantitative_metrics": {
            "speech_rate_words_per_minute": 0,
            "formality_score": 0,
            "hesitation_count": 0,
            "filler_word_frequency": 0,
            "repetition_count": 0,
            "sentence_length_variability": 0,
            "vocabulary_complexity": 0
        },
        "audio_analysis": {
            "vocal_stress_indicators": ["list of vocal stress signs"],
            "pitch_analysis": "analysis of pitch variations and consistency",
            "pause_patterns": "analysis of pauses and their significance",
            "vocal_confidence_level": 0,
            "speaking_pace_consistency": "analysis of pace variations"
        }
    }

    DETAILED INSTRUCTIONS FOR NEW SECTIONS (TEXT-ONLY ANALYSIS):
    - Manipulation Assessment: Analyze for manipulative language based on text. Provide a score (0-100 for manipulation likelihood), list identified tactics (e.g., gaslighting, guilt-tripping), explain why, and list example phrases.
    - Argument Analysis: Assess the strengths and weaknesses of the speaker's arguments from text. Provide lists for strengths and weaknesses, and an overall coherence score (0-100).
    - Speaker Attitude: Evaluate the speaker's tone for respect and sarcasm based on text. Provide a respect score (0-100, high is respectful), indicate if sarcasm is detected (true/false) with a confidence score (0-100 if true), and list contributing tone indicators. Acknowledge that text-only analysis for sarcasm is challenging.
    - Enhanced Understanding: Identify elements for deeper insight from text. List key inconsistencies, areas of evasiveness, 2-3 suggested follow-up questions, and any unverified claims made by the speaker.
    - Quantitative Metrics: Provide numerical assessments based on transcript analysis. Estimate speech rate (words per minute), formality score (0-100), hesitation count, filler word frequency per 100 words, repetition count, sentence length variability (0-100), and vocabulary complexity (0-100).
    - Audio Analysis: For text-only analysis, provide estimates based on transcript patterns. List vocal stress indicators inferred from text, analyze pitch patterns from punctuation and emphasis, assess pause patterns from transcript formatting, provide vocal confidence level (0-100), and analyze speaking pace consistency from text flow.

    CRITICAL REQUIREMENTS:
    - Return ONLY valid JSON, no markdown formatting, no ```json blocks    - All string values must be meaningful, not placeholder text
    - credibility_score, manipulation_score, overall_argument_coherence_score, respect_level_score, sarcasm_confidence_score, speech_rate_words_per_minute, formality_score, hesitation_count, filler_word_frequency, repetition_count, sentence_length_variability, vocabulary_complexity, vocal_confidence_level must be integers 0-100
    - confidence_level must be: "very_low", "low", "medium", "high", "very_high"
    - overall_risk must be: "low", "medium", "high"
    - sarcasm_detected must be boolean (true/false)
    - All arrays must contain at least 1 meaningful item (use an empty array [] if no items apply, but ensure the field is present)
    - All object fields must be present and non-empty, including all new fields (manipulation_assessment, argument_analysis, speaker_attitude, enhanced_understanding, quantitative_metrics, audio_analysis) and their sub-fields.
    """
    gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],        "generationConfig": {
            "temperature": 0.7,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 3072
        }
    }
    
    try:
        response = requests.post(gemini_api_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            gemini_response = response.json()
            logger.info(f"Gemini API response structure: {_sanitize_for_logging(gemini_response)}")

            # Use centralized JSON parsing
            result = parse_gemini_response(gemini_response, allow_partial=True)
            
            if result.get('error'):
                logger.warning(f"Gemini response parsing failed: {_sanitize_for_logging(result.get('error'))}")
                # Still return the result - it contains debug info
            else:
                logger.info("Successfully parsed Gemini response")
            
            return result
        else:
            logger.error(f"Gemini API error: {response.status_code}")
            return create_fallback_response(f"Gemini API error: {response.status_code}", "API request failed")
    except Exception as e:
        logger.error(f"Exception in query_gemini: {type(e).__name__}", exc_info=True)
        return create_fallback_response(f"Gemini request error", "API request failed")

def validate_and_structure_gemini_response(raw_response: Dict[str, Any], transcript: str) -> Dict[str, Any]:
    # check if raw_response is valid json
    if not isinstance(raw_response, dict):
        logger.error(f"Invalid raw_response type. Expected dict, got {type(raw_response).__name__}.")
        return {"error": "Invalid raw_response type"}
    # check if raw_response contains an error
    if 'error' in raw_response:
        logger.error(f"Error in raw_response: {_sanitize_for_logging(raw_response['error'])}")
        return {"error": raw_response['error']}
    print("raw_response", _sanitize_for_logging(raw_response))    # Define default structure to avoid KeyError when accessing raw_response[field]
    default_structure = {
        'speaker_transcripts': {"Speaker 1": "No transcript available"},
        'red_flags_per_speaker': {"Speaker 1": []},
        'credibility_score': 50,
        'confidence_level': "medium",
        'gemini_summary': {
            "tone": "Analysis not available",
            "motivation": "Analysis not available", 
            "credibility": "Analysis not available",
            "emotional_state": "Analysis not available",
            "communication_style": "Analysis not available",
            "key_concerns": "Analysis not available",
            "strengths": "Analysis not available"
        },
        'recommendations': ["Further analysis needed"],
        'linguistic_analysis': {
            # Quantitative metrics
            "word_count": 0,
            "hesitation_count": 0,
            "qualifier_count": 0,
            "certainty_count": 0,
            "filler_count": 0,
            "repetition_count": 0,
            "formality_score": 50.0,
            "complexity_score": 50.0,
            "avg_word_length": 5.0,
            "avg_words_per_sentence": 10.0,
            "sentence_count": 0,
            "speech_rate_wpm": None,
            "hesitation_rate": None,
            "confidence_ratio": 0.5,
            # Descriptive analysis
            "speech_patterns": "Analysis not available",
            "word_choice": "Analysis not available",
            "emotional_consistency": "Analysis not available", 
            "detail_level": "Analysis not available",
            # New analysis fields
            "pause_analysis": "Analysis not available",
            "filler_word_analysis": "Analysis not available",
            "repetition_analysis": "Analysis not available",
            "hesitation_analysis": "Analysis not available",
            "qualifier_analysis": "Analysis not available",
            "certainty_analysis": "Analysis not available",
            "formality_analysis": "Analysis not available",
            "complexity_analysis": "Analysis not available",
            "avg_word_length_analysis": "Analysis not available",
            "avg_words_per_sentence_analysis": "Analysis not available",
            "sentence_count_analysis": "Analysis not available",
            "overall_linguistic_analysis": "Analysis not available"
        },
        'risk_assessment': {
            "overall_risk": "medium",
            "risk_factors": ["Insufficient data"],
            "mitigation_suggestions": ["Collect more information"]
        },
        'manipulation_assessment': {
            "manipulation_score": 0,
            "manipulation_tactics": [],
            "manipulation_explanation": "No manipulation detected.",
            "example_phrases": []
        },
        'argument_analysis': {
            "argument_strengths": ["Analysis needed"],
            "argument_weaknesses": ["Analysis needed"],
            "overall_argument_coherence_score": 50
        },
        'speaker_attitude': {
            "respect_level_score": 50,
            "sarcasm_detected": False,
            "sarcasm_confidence_score": 0,
            "tone_indicators_respect_sarcasm": []
        },
        'enhanced_understanding': {
            "key_inconsistencies": [],
            "areas_of_evasiveness": [],
            "suggested_follow_up_questions": ["Ask for clarification"],
            "unverified_claims": []
        },
        'conversation_flow': "Analysis not available",
        'behavioral_patterns': "Analysis not available", 
        'verification_suggestions': ["Request additional information"],
        'session_insights': {
            "overall_session_assessment": "Analysis in progress",
            "trust_building_indicators": "Analysis not available",
            "concern_escalation": "Analysis not available",
            "consistency_analysis": "Analysis not available",
            "behavioral_evolution": "Analysis not available", 
            "risk_trajectory": "Analysis not available",
            "conversation_dynamics": "Analysis not available"
        },
        'quantitative_metrics': {
            "speech_rate_words_per_minute": 0,
            "formality_score": 50,
            "hesitation_count": 0,
            "filler_word_frequency": 0,
            "repetition_count": 0,
            "sentence_length_variability": 50,
            "vocabulary_complexity": 50
        },
        'audio_analysis': {
            "vocal_stress_indicators": ["Analysis not available"],
            "pitch_analysis": "Analysis not available",
            "pause_patterns": "Analysis not available", 
            "vocal_confidence_level": 50,
            "speaking_pace_consistency": "Analysis not available",
            "speaking_rate_variations": "Analysis not available",
            "voice_quality": "Analysis not available"
        },
        'overall_risk': "medium",   
        'extra': {}
    }    # Check for top-level fields - only use defaults for truly missing critical fields
    validated_response = {}
    
    # Critical fields that must have values
    critical_fields = ['credibility_score', 'confidence_level']
    
    # Fields that should come from analysis if available
    analysis_fields = [
        'speaker_transcripts', 'red_flags_per_speaker', 'gemini_summary', 
        'recommendations', 'linguistic_analysis', 'risk_assessment',
        'manipulation_assessment', 'argument_analysis', 'speaker_attitude', 
        'enhanced_understanding'
    ]
    
    # Fields that are optional and can use defaults
    optional_fields = [
        'conversation_flow', 'behavioral_patterns', 'verification_suggestions',
        'session_insights', 'quantitative_metrics', 'audio_analysis',
        'overall_risk', 'extra'
    ]
    
    # First, copy all available fields from raw_response
    for field, value in raw_response.items():
        validated_response[field] = value
    
    # Only add defaults for truly missing critical fields
    for field in critical_fields:
        if field not in validated_response or validated_response[field] is None:
            logger.warning(f"Missing critical field: {field}. Using default.")
            validated_response[field] = default_structure[field]
    
    # For analysis fields, only use defaults if completely missing and we have no analysis data
    for field in analysis_fields:
        if field not in validated_response:
            # Only log as info, not warning, since some fields might genuinely not be available
            logger.info(f"Analysis field not present: {field}. Using default.")
            validated_response[field] = default_structure[field]
      # For optional fields, add defaults only if missing
    for field in optional_fields:
        if field not in validated_response:
            validated_response[field] = default_structure[field]
            
    # Validate and normalize credibility_score
    try:
        score = int(validated_response.get('credibility_score', default_structure['credibility_score']))
        validated_response['credibility_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning(f"Invalid credibility_score type, using default.")
        validated_response['credibility_score'] = default_structure['credibility_score']

    # Validate confidence_level
    valid_confidence_levels = ["very_low", "low", "medium", "high", "very_high"]
    if validated_response.get('confidence_level') not in valid_confidence_levels:
        logger.warning(f"Invalid confidence_level value, using default.")
        validated_response['confidence_level'] = default_structure['confidence_level']

    # Generic helper to validate list of strings
    def validate_list_of_strings(parent_dict, key, default_list):
        val = parent_dict.get(key, default_list)
        if not isinstance(val, list):
            logger.warning(f"Invalid type for '{key}', expected list, got {type(val)}. Defaulting.")
            parent_dict[key] = default_list
            return
        parent_dict[key] = [str(item) if not isinstance(item, str) else item for item in val]    # Validate and fix gemini_summary
    gemini_summary_data = validated_response.get('gemini_summary', default_structure['gemini_summary'])
    if not isinstance(gemini_summary_data, dict): # Ensure it's a dict
        gemini_summary_data = default_structure['gemini_summary']
    validated_response['gemini_summary'] = gemini_summary_data
    for key, default_val in default_structure['gemini_summary'].items():
        val = gemini_summary_data.get(key, default_val)
        if isinstance(default_val, str) and not isinstance(val, str):
             # Convert lists to strings if needed (common issue with Gemini responses for string fields)
            if isinstance(val, list):
                gemini_summary_data[key] = '; '.join(str(item) for item in val)
                logger.info(f"Converted list to string for gemini_summary.{key}")
            else:
                 gemini_summary_data[key] = str(val)
        elif not val: # if empty string, list or other falsey value for a normally non-empty field.
            gemini_summary_data[key] = default_val
    # Validate linguistic_analysis (already somewhat handled by its source)
    linguistic_analysis_data = validated_response.get('linguistic_analysis', default_structure['linguistic_analysis'])
    if not isinstance(linguistic_analysis_data, dict):
        linguistic_analysis_data = default_structure['linguistic_analysis']
    validated_response['linguistic_analysis'] = linguistic_analysis_data
    for key, default_val in default_structure['linguistic_analysis'].items():
        if key not in linguistic_analysis_data or linguistic_analysis_data[key] is None: # Check for None explicitly for numeric fields
             linguistic_analysis_data[key] = default_val
    # Validate risk_assessment
    risk_assessment_data = validated_response.get('risk_assessment', default_structure['risk_assessment'])
    if not isinstance(risk_assessment_data, dict): # Ensure it's a dict
        risk_assessment_data = default_structure['risk_assessment']
    validated_response['risk_assessment'] = risk_assessment_data
    for key, default_val in default_structure['risk_assessment'].items():
        if key == 'overall_risk':
            if risk_assessment_data.get(key) not in ["low", "medium", "high"]:
                logger.warning(f"Invalid overall_risk value, using default.")
                risk_assessment_data[key] = default_structure['risk_assessment']['overall_risk']
        elif isinstance(default_val, list):
            validate_list_of_strings(risk_assessment_data, key, default_val)
        elif not risk_assessment_data.get(key):
            risk_assessment_data[key] = default_val

    # Validate recommendations (list of strings)
    validate_list_of_strings(validated_response, 'recommendations', default_structure['recommendations'])
    # --- Start Validation for New Fields ---

    # ManipulationAssessment
    manip_assess_data = validated_response.get('manipulation_assessment', default_structure['manipulation_assessment'])
    if not isinstance(manip_assess_data, dict): manip_assess_data = default_structure['manipulation_assessment'] # Ensure dict
    validated_response['manipulation_assessment'] = manip_assess_data
    try:
        score = int(manip_assess_data.get('manipulation_score', default_structure['manipulation_assessment']['manipulation_score']))
        manip_assess_data['manipulation_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning("Invalid manipulation_score, using default.")
        manip_assess_data['manipulation_score'] = default_structure['manipulation_assessment']['manipulation_score']
    validate_list_of_strings(manip_assess_data, 'manipulation_tactics', default_structure['manipulation_assessment']['manipulation_tactics'])
    manip_assess_data['manipulation_explanation'] = str(manip_assess_data.get('manipulation_explanation', default_structure['manipulation_assessment']['manipulation_explanation']) or default_structure['manipulation_assessment']['manipulation_explanation'])
    validate_list_of_strings(manip_assess_data, 'example_phrases', default_structure['manipulation_assessment']['example_phrases'])

    # ArgumentAnalysis
    arg_analysis_data = validated_response.get('argument_analysis', default_structure['argument_analysis'])
    if not isinstance(arg_analysis_data, dict): arg_analysis_data = default_structure['argument_analysis']
    validated_response['argument_analysis'] = arg_analysis_data
    validate_list_of_strings(arg_analysis_data, 'argument_strengths', default_structure['argument_analysis']['argument_strengths'])
    validate_list_of_strings(arg_analysis_data, 'argument_weaknesses', default_structure['argument_analysis']['argument_weaknesses'])
    try:
        score = int(arg_analysis_data.get('overall_argument_coherence_score', default_structure['argument_analysis']['overall_argument_coherence_score']))
        arg_analysis_data['overall_argument_coherence_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning("Invalid overall_argument_coherence_score, using default.")
        arg_analysis_data['overall_argument_coherence_score'] = default_structure['argument_analysis']['overall_argument_coherence_score']

    # SpeakerAttitude
    speaker_attitude_data = validated_response.get('speaker_attitude', default_structure['speaker_attitude'])
    if not isinstance(speaker_attitude_data, dict): speaker_attitude_data = default_structure['speaker_attitude']
    validated_response['speaker_attitude'] = speaker_attitude_data
    try:
        score = int(speaker_attitude_data.get('respect_level_score', default_structure['speaker_attitude']['respect_level_score']))
        speaker_attitude_data['respect_level_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning("Invalid respect_level_score, using default.")
        speaker_attitude_data['respect_level_score'] = default_structure['speaker_attitude']['respect_level_score']

    sarcasm_detected_val = speaker_attitude_data.get('sarcasm_detected', default_structure['speaker_attitude']['sarcasm_detected'])
    if not isinstance(sarcasm_detected_val, bool):
        logger.warning(f"Invalid sarcasm_detected type, using default.")
        speaker_attitude_data['sarcasm_detected'] = default_structure['speaker_attitude']['sarcasm_detected']
    else:
        speaker_attitude_data['sarcasm_detected'] = sarcasm_detected_val

    try:
        score = int(speaker_attitude_data.get('sarcasm_confidence_score', default_structure['speaker_attitude']['sarcasm_confidence_score']))
        speaker_attitude_data['sarcasm_confidence_score'] = max(0, min(100, score))
    except (ValueError, TypeError):
        logger.warning("Invalid sarcasm_confidence_score, using default.")
        speaker_attitude_data['sarcasm_confidence_score'] = default_structure['speaker_attitude']['sarcasm_confidence_score']
    validate_list_of_strings(speaker_attitude_data, 'tone_indicators_respect_sarcasm', default_structure['speaker_attitude']['tone_indicators_respect_sarcasm'])

    # EnhancedUnderstanding
    enhanced_und_data = validated_response.get('enhanced_understanding', default_structure['enhanced_understanding'])
    if not isinstance(enhanced_und_data, dict): enhanced_und_data = default_structure['enhanced_understanding']
    validated_response['enhanced_understanding'] = enhanced_und_data
    validate_list_of_strings(enhanced_und_data, 'key_inconsistencies', default_structure['enhanced_understanding']['key_inconsistencies'])
    validate_list_of_strings(enhanced_und_data, 'areas_of_evasiveness', default_structure['enhanced_understanding']['areas_of_evasiveness'])
    validate_list_of_strings(enhanced_und_data, 'suggested_follow_up_questions', default_structure['enhanced_understanding']['suggested_follow_up_questions'])
    validate_list_of_strings(enhanced_und_data, 'unverified_claims', default_structure['enhanced_understanding']['unverified_claims'])

    # --- End Validation for New Fields ---    # Ensure audio_analysis is present and structured, even if from text-only
    audio_analysis_data = validated_response.get('audio_analysis')
    default_audio_analysis = default_structure['audio_analysis']

    if not isinstance(audio_analysis_data, dict):
        logger.warning(f"Audio analysis data is missing or not a dict, using default.")
        validated_response['audio_analysis'] = default_audio_analysis.copy() # Use a copy
    else:
        # Ensure all keys from default are present
        for key, default_value in default_audio_analysis.items():
            if key not in audio_analysis_data:
                audio_analysis_data[key] = default_value
            # Specific validation for vocal_confidence_level
            if key == 'vocal_confidence_level':
                try:
                    score = int(audio_analysis_data.get(key, 0))
                    audio_analysis_data[key] = max(0, min(100, score))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid vocal_confidence_level, defaulting to 50.")
                    audio_analysis_data[key] = 50            # Validate lists of strings for relevant keys
            elif key == 'vocal_stress_indicators' and not isinstance(audio_analysis_data[key], list):
                 audio_analysis_data[key] = [str(audio_analysis_data[key])] if audio_analysis_data[key] else []

    # Validate new fields that frontend expects
    # Conversation flow - should be a string
    if not isinstance(validated_response.get('conversation_flow'), str):
        validated_response['conversation_flow'] = default_structure['conversation_flow']
    
    # Behavioral patterns - should be a string  
    if not isinstance(validated_response.get('behavioral_patterns'), str):
        validated_response['behavioral_patterns'] = default_structure['behavioral_patterns']
    
    # Verification suggestions - should be a list of strings
    validate_list_of_strings(validated_response, 'verification_suggestions', default_structure['verification_suggestions'])
    
    # Session insights - should be a dict with specific subfields
    session_insights_data = validated_response.get('session_insights', default_structure['session_insights'])
    if not isinstance(session_insights_data, dict):
        session_insights_data = default_structure['session_insights']
    validated_response['session_insights'] = session_insights_data
    
    # Validate session insights subfields
    for key, default_val in default_structure['session_insights'].items():
        if key not in session_insights_data or not isinstance(session_insights_data[key], str):
            session_insights_data[key] = default_val
    
    # Ensure quantitative_metrics is present and validated
    quantitative_metrics_data = validated_response.get('quantitative_metrics', default_structure['quantitative_metrics'])
    if not isinstance(quantitative_metrics_data, dict):
        quantitative_metrics_data = default_structure['quantitative_metrics']
    validated_response['quantitative_metrics'] = quantitative_metrics_data
    
    # Validate all numeric fields in quantitative_metrics
    for key, default_val in default_structure['quantitative_metrics'].items():
        try:
            score = int(quantitative_metrics_data.get(key, default_val))
            if key in ['speech_rate_words_per_minute', 'hesitation_count', 'filler_word_frequency', 'repetition_count']:
                quantitative_metrics_data[key] = max(0, score)  # No upper limit for count fields
            else:
                quantitative_metrics_data[key] = max(0, min(100, score))  # 0-100 for score fields
        except (ValueError, TypeError):
            logger.warning(f"Invalid {key} in quantitative_metrics, using default.")
            quantitative_metrics_data[key] = default_val
    
    print("validated_response structure:", _sanitize_for_logging(validated_response))
    return validated_response


def transcribe_with_gemini(audio_path: str) -> str:
    """
    Transcribe audio using Gemini API.
    Returns the transcription text.
    """
    if not GEMINI_API_KEY:
        logger.error("Missing Gemini API key. Cannot transcribe audio.")
        raise Exception("Missing Gemini API key")

    try:
        # Read and encode audio file
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
        
        # Encode audio to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Determine audio MIME type based on file extension
        file_ext = os.path.splitext(audio_path)[1].lower()
        mime_type_map = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg', 
            '.m4a': 'audio/mp4',
            '.ogg': 'audio/ogg',
            '.webm': 'audio/webm',
            '.flac': 'audio/flac'
        }
        mime_type = mime_type_map.get(file_ext, 'audio/wav')
        
        prompt = """
        Please transcribe this audio file accurately. Return only the transcribed text without any additional formatting or commentary.
        
        If there are multiple speakers, indicate them as "Speaker 1:", "Speaker 2:", etc.
        Include all spoken words, including filler words like "um", "uh", "you know" etc.
        Preserve the natural flow of speech including pauses where significant.
        """

        gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

        headers = {"Content-Type": "application/json"}
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": audio_base64
                        }
                    }
                ]
            }],
            "safetySettings": safety_settings,
            "generationConfig": {
                "temperature": 0.1,  # Low temperature for accurate transcription
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 2048            }
        }

        logger.info(f"Sending transcription request to Gemini for {len(audio_data)} bytes of audio data")
        response = requests.post(gemini_api_url, headers=headers, data=json.dumps(payload), timeout=300) # Added timeout
        
        if response.status_code == 200:
            gemini_response = response.json()
            logger.info("Gemini transcription response received")
            
            # Use centralized text extraction
            transcript = extract_text_from_gemini_response(gemini_response)
            
            if not transcript:
                # Check for specific block reasons
                block_reason_message = "Unknown reason."
                if 'promptFeedback' in gemini_response and 'blockReason' in gemini_response['promptFeedback']:
                    block_reason_message = gemini_response['promptFeedback']['blockReason']
                elif 'promptFeedback' in gemini_response and 'safetyRatings' in gemini_response['promptFeedback']:
                    safety_ratings = gemini_response['promptFeedback']['safetyRatings']
                    logger.warning(f"No transcript extracted, found safetyRatings")
                    block_reason_message = f"Content may have been filtered due to safety ratings"
                
                logger.error(f"Failed to extract transcript from Gemini response. Reason: {block_reason_message}")
                raise Exception(f"No transcription content received from Gemini. Reason: {block_reason_message}")
            
            logger.info(f"Successfully transcribed audio: {_sanitize_for_logging(transcript)}")
            return transcript
            
        else:
            logger.error(f"Gemini transcription API error: {response.status_code}")
            raise Exception(f"Gemini transcription API error: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Exception in transcribe_with_gemini: {type(e).__name__}", exc_info=True)
        raise Exception(f"Gemini transcription error: {str(e)}")


def analyze_emotions_with_gemini(audio_path: str, transcript: str) -> list:
    """
    Analyze emotions using Gemini API with both audio and transcript.
    Returns a list of emotion dictionaries with label and score.
    """
    if not GEMINI_API_KEY:
        logger.error("Missing Gemini API key. Cannot analyze emotions.")
        # Return default emotions instead of raising exception
        return [
            {"label": "neutral", "score": 0.7},
            {"label": "uncertainty", "score": 0.3}
        ]

    try:
        # Read and encode audio file
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
        
        # Encode audio to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Determine audio MIME type based on file extension
        file_ext = os.path.splitext(audio_path)[1].lower()
        mime_type_map = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg', 
            '.m4a': 'audio/mp4',
            '.ogg': 'audio/ogg',
            '.webm': 'audio/webm',
            '.flac': 'audio/flac'
        }
        mime_type = mime_type_map.get(file_ext, 'audio/wav')
        
        prompt = f"""
        Analyze the emotional content of this audio file and transcript for emotion detection.
        
        TRANSCRIPT:
        {transcript}
        
        Based on the audio content (tone, pitch, speaking rate, voice quality) and the transcript, 
        identify the primary emotions present in the speaker's voice.
        
        Return your analysis as a JSON array of emotion objects, each with "label" and "score" fields.
        The score should be a float between 0 and 1 representing confidence.
        
        Focus on these emotion categories:
        - neutral, happy, sad, angry, fear, surprise, disgust
        - confidence, uncertainty, stress, calm, excitement, boredom
        - sincerity, deception, nervousness, comfort
        
        Example format:
        [
            {{"label": "neutral", "score": 0.6}},
            {{"label": "confidence", "score": 0.4}},
            {{"label": "slight_stress", "score": 0.3}}
        ]
        
        Return only the JSON array, no other text.
        """

        gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": audio_base64
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 1024            }
        }
        
        logger.info(f"Sending emotion analysis request to Gemini for {len(audio_data)} bytes of audio data")
        response = requests.post(gemini_api_url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            gemini_response = response.json()
            logger.info("Gemini emotion analysis response received")
            
            # Use centralized text extraction
            text = extract_text_from_gemini_response(gemini_response)
            
            if not text:
                logger.warning("Failed to extract text from Gemini emotion response")
                return [{"label": "neutral", "score": 0.7}, {"label": "uncertainty", "score": 0.3}]            # Use centralized JSON parsing
            result = safe_json_parse(text)
            
            # Check if result is an error dict
            if isinstance(result, dict) and result.get('error'):
                logger.warning(f"Failed to parse Gemini emotion response: {result.get('error')}")
                return [{"label": "neutral", "score": 0.6}, {"label": "uncertainty", "score": 0.4}]
            
            # If successful, result is the parsed data directly (not wrapped in 'data' key)
            emotions = result
            
            # Validate the structure
            if not isinstance(emotions, list):
                logger.warning("Gemini emotion response is not a list")
                return [{"label": "neutral", "score": 0.6}, {"label": "uncertainty", "score": 0.4}]
            
            # Validate and normalize emotion objects
            valid_emotions = []
            for emotion in emotions:
                if isinstance(emotion, dict) and 'label' in emotion and 'score' in emotion:
                    try:
                        # Ensure score is a float between 0 and 1
                        score = float(emotion['score'])
                        if score < 0:
                            score = 0
                        elif score > 1:
                            score = 1
                        valid_emotions.append({"label": emotion['label'], "score": score})
                    except (ValueError, TypeError):
                        continue
            
            if valid_emotions:
                logger.info(f"Successfully analyzed emotions: {len(valid_emotions)} emotions detected")
                return valid_emotions
            else:
                logger.warning("No valid emotions found in response")
                return [{"label": "neutral", "score": 0.6}, {"label": "uncertainty", "score": 0.4}]
            
        else:
            logger.error(f"Gemini emotion API error: {response.status_code}")
            return [{"label": "neutral", "score": 0.7}, {"label": "uncertainty", "score": 0.3}]
            
    except Exception as e:
        logger.error(f"Exception in analyze_emotions_with_gemini: {type(e).__name__}", exc_info=True)
        # Return default emotions on any exception
        return [
            {"label": "neutral", "score": 0.7},
            {"label": "uncertainty", "score": 0.3}
        ]

def get_fallback_audio_analysis(error_reason: str) -> Dict[str, Any]:
    """
    Generate fallback audio analysis structure when Gemini fails or returns non-JSON
    """
    return {
        "vocal_stress_indicators": ["Analysis not available due to API issue"],
        "pitch_analysis": f"Analysis unavailable: {error_reason}",
        "pause_patterns": "Analysis not available - using fallback",
        "vocal_confidence_level": 50,
        "speaking_pace_consistency": "Unable to analyze due to API limitations",
        "speaking_rate_variations": "Analysis not available",
        "voice_quality": f"Audio analysis failed: {error_reason}",
        "error": error_reason,
        "fallback_used": True
    }


def audio_analysis_gemini(audio_path: str, transcript: str, flags: Dict[str, Any], session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Enhanced Gemini query that includes both audio data and transcript for more comprehensive analysis
    audio analysis includes tone, pitch, speaking rate, voice quality, and other audio-specific insights
    """
    if not GEMINI_API_KEY:
        logger.error("Missing Gemini API key. Cannot query Gemini.")
        return get_fallback_audio_analysis("Missing Gemini API key")

    try:
        # Read and encode audio file
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
            
        # Encode audio to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Determine audio MIME type based on file extension
        file_ext = os.path.splitext(audio_path)[1].lower()
        mime_type_map = {
            '.wav': 'audio/wav',
            '.mp3': 'audio/mpeg', 
            '.m4a': 'audio/mp4',
            '.ogg': 'audio/ogg',
            '.webm': 'audio/webm',
            '.flac': 'audio/flac'
        }
        mime_type = mime_type_map.get(file_ext, 'audio/wav')
        
        # Build prompt with audio and transcript
        prompt = f"""
        Analyze the audio and transcript for deception, stress, and speaker separation. 

        AUDIO:
        (audio data)

        TRANSCRIPT:
        {transcript}

        RED FLAGS FROM PRIMARY ANALYSIS:
        {json.dumps(flags, indent=2)}
        
        Focus on audio-specific metrics including:
        - Tone of voice
        - Pitch variations
        - Speaking rate changes
        - Hesitation patterns and pause analysis
        - Voice quality and emotional undertones
        - Vocal authenticity vs. performance
        - Micro-expressions in speech
        - Breathing patterns and vocal tension
        - Cognitive load indicators
        - Emotional stress responses
        - Fear of detection indicators
        - Cognitive dissonance signs
        
        Return a structured JSON response with audio analysis findings.
        """
        
        gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": audio_base64
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 4096
            }
        }

        logger.info(f"Sending audio analysis request to Gemini for {len(audio_data)} bytes of audio data")
        response = requests.post(gemini_api_url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            gemini_response = response.json()
            logger.info("Gemini audio analysis response received")
            
            # Use centralized JSON parsing
            result = parse_gemini_response(gemini_response, allow_partial=True)
            
            if result.get('error'):
                logger.warning(f"Gemini audio analysis parsing failed: {_sanitize_for_logging(result.get('error'))}")
                return get_fallback_audio_analysis(f"Parsing failed")
            else:
                logger.info("Successfully parsed Gemini audio analysis response")
                return result
        else:
            logger.error(f"Gemini audio analysis API error: {response.status_code}")
            return get_fallback_audio_analysis(f"Gemini API error: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Exception in audio_analysis_gemini: {type(e).__name__}", exc_info=True)
        return get_fallback_audio_analysis(f"Audio analysis exception")


# Add necessary imports for the new pipeline
# Placeholder for GeminiService if not already defined in this file
class GeminiService:
    async def query_gemini_for_raw_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Placeholder for the actual Gemini API call that returns a parsed JSON dictionary.
        This method is expected by the individual analysis services.
        The real implementation would call the Gemini API with the prompt
        and parse the response to extract a JSON object.
        """
        logger.info("GeminiService.query_gemini_for_raw_json called.")
        # This is a simplified placeholder.
        # A real implementation would use 'requests' or 'aiohttp' to call the Gemini API
        # and then parse the JSON from the response.
        # For now, it simulates a successful call returning None, relying on service fallbacks.
        # To make services actually work, this needs to be implemented.
        
        # Simulate a call to a generic Gemini text generation endpoint
        # that is expected to return a JSON string.
        
        # This is a conceptual representation. The actual API call structure
        # (endpoint, payload, headers) depends on the specific Gemini model and task.
        # For example, if using a model that directly outputs JSON:
        gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json", # Request JSON output
                "temperature": 0.2, # Lower temperature for more deterministic JSON structure
                "maxOutputTokens": 2048 
            }
        }
        
        try:
            # In a real async service, you'd use an async HTTP client
            # For simplicity in this synchronous placeholder within an async function context:
            # We'll log and return None, services should have fallbacks.
            # To truly make this work, this part needs to be async and use aiohttp or similar.
            
            # This is a conceptual synchronous call for placeholder purposes
            # response = requests.post(gemini_api_url, headers=headers, data=json.dumps(payload))
            # if response.status_code == 200:
            #     response_json = response.json()
            #     text_content = extract_text_from_gemini_response(response_json) # Assuming this extracts the string that is JSON
            #     if text_content:
            #         return safe_json_parse(text_content) # Parses the string to dict
            #     else:
            #         logger.warning("GeminiService: No text content in response to parse for JSON.")
            #         return None
            # else:
            #     logger.error(f"GeminiService: API error {response.status_code} - {response.text}")
            #     return None
            logger.warning("GeminiService.query_gemini_for_raw_json: Placeholder returning None. Implement actual API call.")
            return None # Services will use their fallbacks
        except Exception as e:
            logger.error(f"GeminiService.query_gemini_for_raw_json error: {e}", exc_info=True)
            return None

from backend.models import (
    ManipulationAssessment, ArgumentAnalysis, SpeakerAttitude, EnhancedUnderstanding,
    PsychologicalAnalysis, AudioAnalysis, InteractionMetrics, ConversationFlow,
    EmotionDetail, LinguisticAnalysis # Make sure these are the correct model names
)
from backend.services.manipulation_service import ManipulationService
from backend.services.argument_service import ArgumentService
from backend.services.speaker_attitude_service import SpeakerAttitudeService
from backend.services.enhanced_understanding_service import EnhancedUnderstandingService
from backend.services.psychological_service import PsychologicalService
from backend.services.audio_analysis_service import AudioAnalysisService
from backend.services.quantitative_metrics_service import QuantitativeMetricsService
from backend.services.conversation_flow_service import ConversationFlowService
# from backend.services.linguistic_service import analyze_linguistic_patterns # Causes circular import - import locally where needed
# transcribe_with_gemini and analyze_emotions_with_gemini should be defined in this file or imported.
# Assuming they are defined later in this file as per previous context.

async def full_audio_analysis_pipeline(
    audio_path: str,
    existing_transcript: Optional[str],
    session_context: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Orchestrates the full audio analysis by calling transcription,
    all modular analysis services, emotion analysis, and linguistic analysis.
    """
    loop = asyncio.get_running_loop()
    gemini_service_instance = GeminiService()

    manipulation_service = ManipulationService(gemini_service_instance)
    argument_service = ArgumentService(gemini_service_instance)
    speaker_attitude_service = SpeakerAttitudeService(gemini_service_instance)
    enhanced_understanding_service = EnhancedUnderstandingService(gemini_service_instance)
    psychological_service = PsychologicalService(gemini_service_instance)
    audio_analysis_svc = AudioAnalysisService(gemini_service_instance) # Renamed to avoid conflict
    quantitative_metrics_service = QuantitativeMetricsService(gemini_service_instance)
    conversation_flow_service = ConversationFlowService(gemini_service_instance)

    transcript_text = existing_transcript
    if not transcript_text:
        logger.info(f"Transcribing audio file")
        try:
            # Assuming transcribe_with_gemini is a synchronous function
            transcript_text = await loop.run_in_executor(None, transcribe_with_gemini, audio_path)
            logger.info(f"Transcription successful: {_sanitize_for_logging(transcript_text)}")
        except Exception as e:
            logger.error(f"Transcription failed: {type(e).__name__}", exc_info=True)
            transcript_text = "Transcription failed." # Fallback

    # Import locally to avoid circular import at module level
    from backend.services.linguistic_service import analyze_linguistic_patterns

    analysis_tasks = {
        "manipulation_assessment": manipulation_service.analyze(transcript_text, session_context),
        "argument_analysis": argument_service.analyze(transcript_text, session_context),
        "speaker_attitude": speaker_attitude_service.analyze(transcript_text, session_context),
        "enhanced_understanding": enhanced_understanding_service.analyze(transcript_text, session_context),
        "psychological_analysis": psychological_service.analyze(transcript_text, session_context),
        "audio_analysis": audio_analysis_svc.analyze(audio_path, transcript_text, session_context),
        "quantitative_metrics": quantitative_metrics_service.analyze(transcript_text, session_context),
        "conversation_flow": conversation_flow_service.analyze(transcript_text, session_context),
        # Assuming analyze_emotions_with_gemini and analyze_linguistic_patterns are synchronous
        "emotion_analysis": loop.run_in_executor(None, analyze_emotions_with_gemini, audio_path, transcript_text),
        "linguistic_analysis": loop.run_in_executor(None, analyze_linguistic_patterns, transcript_text)
    }

    results = {}
    gathered_results = await asyncio.gather(*analysis_tasks.values(), return_exceptions=True)
    
    result_keys = list(analysis_tasks.keys())
    for i, key in enumerate(result_keys):
        if isinstance(gathered_results[i], Exception):
            logger.error(f"Error in analysis task '{key}': {type(gathered_results[i]).__name__}", exc_info=gathered_results[i])
            # Fallback to None or default model instance (services should handle this internally)
            results[key] = None # Or a default object if known
        else:
            results[key] = gathered_results[i]

    final_analysis_data = {
        "transcript": transcript_text,
        "manipulation_assessment": results.get("manipulation_assessment"),
        "argument_analysis": results.get("argument_analysis"),
        "speaker_attitude": results.get("speaker_attitude"),
        "enhanced_understanding": results.get("enhanced_understanding"),
        "psychological_analysis": results.get("psychological_analysis"),
        "audio_analysis": results.get("audio_analysis"),
        "interaction_metrics": results.get("interaction_metrics"),
        "conversation_flow": results.get("conversation_flow"),
        "emotion_analysis": results.get("emotion_analysis", []),
        "linguistic_analysis": results.get("linguistic_analysis", {})
    }
    
    logger.debug(f"full_audio_analysis_pipeline results structure: {{key: type(value).__name__ for key, value in final_analysis_data.items()}}")
    return final_analysis_data

# ... rest of the existing code in gemini_service.py ...
# Ensure that query_gemini, query_gemini_with_audio, validate_and_structure_gemini_response,
# transcribe_with_gemini, analyze_emotions_with_gemini, get_fallback_audio_analysis are defined
# correctly in this file. The new pipeline function should be placed before them if they depend on it,
# or after if it depends on them (which is the case for transcribe_with_gemini etc.)
# For now, placing this new pipeline function and GeminiService class definition
# towards the top, after imports but before other function definitions that might use GeminiService.