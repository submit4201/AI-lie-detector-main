# backend/services/psychological_service.py
import logging
import json
from typing import Dict, Any, Optional, TYPE_CHECKING
from backend.models import PsychologicalAnalysis # Ensure this import is correct

# Use TYPE_CHECKING to avoid circular import while keeping type hints
if TYPE_CHECKING:
    from backend.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class PsychologicalService:
    def __init__(self, gemini_service: Optional["GeminiService"] = None): # Added Optional and default
        if gemini_service is None:
            # Import here to avoid circular import at module level
            from backend.services.gemini_service import GeminiService
            gemini_service = GeminiService()
        self.gemini_service = gemini_service

    def _fallback_analysis(self, transcript_snippet: str) -> PsychologicalAnalysis:
        logger.warning(f"PsychologicalService: LLM call failed or returned malformed data for transcript snippet: {transcript_snippet}. Falling back to default.")
        # Ensure fallback returns all fields expected by PsychologicalAnalysis
        return PsychologicalAnalysis(
            emotional_state="Neutral",
            emotional_state_analysis="Fallback: Analysis not available.",
            cognitive_load="Normal",
            cognitive_load_analysis="Fallback: Analysis not available.",
            stress_level=0.0,
            stress_level_analysis="Fallback: Analysis not available.",
            confidence_level=0.0,
            confidence_level_analysis="Fallback: Analysis not available.",
            psychological_summary="Fallback: Analysis not available.",
            potential_biases=[],
            potential_biases_analysis="Fallback: Analysis not available."
        )

    async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> PsychologicalAnalysis: # Added Optional
        """
        Performs psychological analysis on the given transcript using an LLM.
        """
        transcript_snippet = transcript[:500]
        logger.info(f"Performing psychological analysis for transcript snippet: {transcript_snippet}...")

        prompt = f"""
Analyze the speaker's psychological state based on the following transcript.
Transcript:
"{transcript}"

Session Context (if available, use for nuanced understanding):
{json.dumps(session_context) if session_context else "No additional session context provided."}

Based on the transcript and context, provide your analysis as a JSON object matching the PsychologicalAnalysis model fields below:
1.  emotional_state (str): Describe the overall emotional state inferred from the speaker's language and expression (e.g., "Neutral", "Anxious", "Frustrated", "Joyful", "Sad", "Agitated").
2.  emotional_state_analysis (str): Provide a detailed analysis and reasoning for the inferred 'emotional_state'. What specific cues (word choice, tone implied by text, recurring themes) led to this assessment? Cite examples.
3.  cognitive_load (str): Assess the speaker's inferred cognitive load (e.g., "Low", "Normal", "High", "Overwhelmed").
4.  cognitive_load_analysis (str): Provide a detailed analysis for the 'cognitive_load' assessment. Are there signs of difficulty in processing information, memory recall, or decision-making (e.g., hesitations, confusion, slow responses, complex sentence structures vs. simple)? Cite examples.
5.  stress_level (float, 0.0 to 1.0): Estimate the speaker's inferred stress level. 0.0 means no stress, 1.0 means very high stress.
6.  stress_level_analysis (str): Provide a detailed analysis for the 'stress_level' score. What linguistic or behavioral cues (e.g., pressured speech, negative emotional language, expressions of worry) indicate this level of stress? Cite examples.
7.  confidence_level (float, 0.0 to 1.0): Estimate the speaker's inferred confidence level in their statements and demeanor. 0.0 means very low confidence, 1.0 means very high confidence.
8.  confidence_level_analysis (str): Provide a detailed analysis for the 'confidence_level' score. What cues (e.g., assertive language, hesitations, qualifiers, self-correction, directness) indicate this level of confidence? Cite examples.
9.  psychological_summary (str): Provide a concise overall summary of the psychological state analysis, integrating the findings above.
10. potential_biases (List[str]): Identify any potential cognitive biases that might be influencing the speaker's communication or reasoning (e.g., "Confirmation bias", "Anchoring bias", "Availability heuristic", "Self-serving bias").
11. potential_biases_analysis (str): For each identified 'potential_bias', provide a brief explanation of why you suspect it and how it might be impacting the speaker's statements or perspective. Cite examples.

JSON structure to be returned:
{{
  "emotional_state": "...",
  "emotional_state_analysis": "...",
  "cognitive_load": "...",
  "cognitive_load_analysis": "...",
  "stress_level": float,
  "stress_level_analysis": "...",
  "confidence_level": float,
  "confidence_level_analysis": "...",
  "psychological_summary": "...",
  "potential_biases": [],
  "potential_biases_analysis": "..."
}}
If a field cannot be determined or is not applicable, use a sensible default (e.g., "Neutral"/"Normal" for states, 0.0 for floats, empty list for lists, or "Analysis not available." for strings).
Focus your analysis solely on the provided transcript and session context.
"""
        try:
            raw_analysis = await self.gemini_service.query_gemini_for_raw_json(prompt) # Changed from raw_response
            if raw_analysis: # Changed from raw_response
                data = json.loads(raw_analysis) # Added this line
                # Ensure all fields from the model are present, with defaults if missing
                return PsychologicalAnalysis(
                    emotional_state=data.get("emotional_state", "Neutral"),
                    emotional_state_analysis=data.get("emotional_state_analysis", "Analysis not available."),
                    cognitive_load=data.get("cognitive_load", "Normal"),
                    cognitive_load_analysis=data.get("cognitive_load_analysis", "Analysis not available."),
                    stress_level=data.get("stress_level", 0.0),
                    stress_level_analysis=data.get("stress_level_analysis", "Analysis not available."),
                    confidence_level=data.get("confidence_level", 0.0),
                    confidence_level_analysis=data.get("confidence_level_analysis", "Analysis not available."),
                    psychological_summary=data.get("psychological_summary", "Analysis not available."),
                    potential_biases=data.get("potential_biases", []),
                    potential_biases_analysis=data.get("potential_biases_analysis", "Analysis not available.")
                )
            else:
                logger.warning(f"PsychologicalService: Received no response from LLM for transcript snippet: {transcript_snippet}.")
                return self._fallback_analysis(transcript_snippet)
        except (json.JSONDecodeError, TypeError) as e: # Keep Exception for broader unexpected issues
            logger.error(f"PsychologicalService: Error processing LLM response for transcript snippet: {transcript_snippet}. Error: {e}")
            return self._fallback_analysis(transcript_snippet)
        except Exception as e:
            logger.error(f"PsychologicalService: Unexpected error during analysis for transcript snippet: {transcript_snippet}. Error: {e}")
            return self._fallback_analysis(transcript_snippet)

# psychological_service = PsychologicalService() # Commented out global instantiation
