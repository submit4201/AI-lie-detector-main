# backend/services/speaker_attitude_service.py
import logging
import json
from typing import Dict, Any, Optional, TYPE_CHECKING
from backend.models import SpeakerAttitude # Ensure this import is correct and SpeakerAttitude is defined in models.py

# Use TYPE_CHECKING to avoid circular import while keeping type hints
if TYPE_CHECKING:
    from backend.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class SpeakerAttitudeService:
    def __init__(self, gemini_service: Optional["GeminiService"] = None):
        if gemini_service is None:
            # Import here to avoid circular import at module level
            from backend.services.gemini_service import GeminiService
            gemini_service = GeminiService()
        self.gemini_service = gemini_service

    def _fallback_analysis(self, transcript_snippet: str) -> SpeakerAttitude:
        logger.warning(f"SpeakerAttitudeService: LLM call failed or returned malformed data for transcript snippet: {transcript_snippet}. Falling back to default.")
        # Ensure fallback returns all fields expected by SpeakerAttitude, using defaults
        return SpeakerAttitude(
            dominant_attitude="Neutral",
            attitude_scores={},
            respect_level="Neutral",
            respect_level_score=0.0,
            respect_level_score_analysis="Fallback: Analysis not available.",
            formality_score=0.0,
            formality_assessment="Fallback: Analysis not available.",
            politeness_score=0.0,
            politeness_assessment="Fallback: Analysis not available."
        )

    async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> SpeakerAttitude:
        """
        Performs speaker attitude analysis on the given transcript using an LLM.
        """
        transcript_snippet = transcript[:500] # Use a snippet for brevity in logs if needed
        logger.info(f"Performing speaker attitude analysis for transcript snippet: {transcript_snippet}...")

        prompt = f"""
Analyze the speaker's attitude in the following transcript.
Transcript:
"{transcript}"

Session Context (if available, use for nuanced understanding):
{json.dumps(session_context) if session_context else "No additional session context provided."}

Based on the transcript and context, provide your analysis as a JSON object matching the SpeakerAttitude model fields below:
1.  dominant_attitude (str): Describe the dominant attitude of the speaker (e.g., "Cooperative", "Hostile", "Dismissive", "Supportive", "Neutral", "Anxious").
2.  attitude_scores (Dict[str, float]): Provide scores (0.0 to 1.0) for various relevant attitudes you can infer. Examples: {{"polite": 0.8, "impatient": 0.6, "friendly": 0.7}}.
3.  respect_level (str): Assess the qualitative level of respect shown by the speaker (e.g., "Respectful", "Disrespectful", "Neutral", "Condescending").
4.  respect_level_score (float, 0.0 to 1.0): A numerical score for the assessed respect level. 0.0 means very disrespectful, 1.0 means very respectful.
5.  respect_level_score_analysis (str): Provide a detailed analysis and reasoning for the 'respect_level_score'. Explain which cues (verbal, tonal if inferable from text) led to this score. Cite examples.
6.  formality_score (float, 0.0 to 1.0): Assess the formality of the speaker's language. 0.0 is very informal, 1.0 is very formal.
7.  formality_assessment (str): Provide a qualitative assessment of the speaker's formality. Explain your reasoning, citing examples of word choice, phrasing, or sentence structure.
8.  politeness_score (float, 0.0 to 1.0): Assess the politeness level of the speaker. 0.0 is very impolite, 1.0 is very polite.
9.  politeness_assessment (str): Provide a qualitative assessment of the speaker's politeness. Explain your reasoning, citing examples of polite/impolite markers, requests, or responses.

JSON structure to be returned:
{{
  "dominant_attitude": "...",
  "attitude_scores": {{"attitude1": score1, "attitude2": score2}},
  "respect_level": "...",
  "respect_level_score": float,
  "respect_level_score_analysis": "...",
  "formality_score": float,
  "formality_assessment": "...",
  "politeness_score": float,
  "politeness_assessment": "..."
}}
If a field cannot be determined or is not applicable, use a sensible default (e.g., "Neutral" for strings, 0.0 for floats, empty dict for scores, or "Analysis not available." for detailed analysis strings).
Focus your analysis solely on the provided transcript and session context.
"""
        try:
            raw_analysis = await self.gemini_service.query_gemini_for_raw_json(prompt)
            if raw_analysis:
                data = json.loads(raw_analysis)
                # Ensure all fields from the model are present, with defaults if missing
                return SpeakerAttitude(
                    dominant_attitude=data.get("dominant_attitude", "Neutral"),
                    attitude_scores=data.get("attitude_scores", {}),
                    respect_level=data.get("respect_level", "Neutral"),
                    respect_level_score=data.get("respect_level_score", 0.0),
                    respect_level_score_analysis=data.get("respect_level_score_analysis", "Analysis not available."),
                    formality_score=data.get("formality_score", 0.0),
                    formality_assessment=data.get("formality_assessment", "Analysis not available."),
                    politeness_score=data.get("politeness_score", 0.0),
                    politeness_assessment=data.get("politeness_assessment", "Analysis not available.")
                )
            else:
                logger.warning(f"SpeakerAttitudeService: Received no response from LLM for transcript snippet: {transcript_snippet}.")
                return self._fallback_analysis(transcript_snippet)
        except (json.JSONDecodeError, TypeError) as e: # Keep Exception for broader unexpected issues
            logger.error(f"SpeakerAttitudeService: Error processing LLM response for transcript snippet: {transcript_snippet}. Error: {e}")
            return self._fallback_analysis(transcript_snippet)
        except Exception as e:
            logger.error(f"SpeakerAttitudeService: Unexpected error during analysis for transcript snippet: {transcript_snippet}. Error: {e}")
            return self._fallback_analysis(transcript_snippet)

# speaker_attitude_service = SpeakerAttitudeService() # Commented out global instantiation
