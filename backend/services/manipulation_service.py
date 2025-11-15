# backend/services/manipulation_service.py
import logging
from typing import Dict, Any, Optional, TYPE_CHECKING
from backend.models import ManipulationAssessment
import json

# Use TYPE_CHECKING to avoid circular import while keeping type hints
if TYPE_CHECKING:
    from backend.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ManipulationService:
    def __init__(self, gemini_service: Optional["GeminiService"] = None):
        if gemini_service is None:
            # Import here to avoid circular import at module level
            from backend.services.gemini_service import GeminiService
            gemini_service = GeminiService()
        self.gemini_service = gemini_service

    async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> ManipulationAssessment:
        if not transcript:
            return ManipulationAssessment()

        prompt = f"""Analyze the following transcript for signs of manipulation.
Transcript:
"{transcript}"

Session Context (if available, use for nuanced understanding):
{json.dumps(session_context) if session_context else "No additional session context provided."}

Consider the following aspects and provide your analysis as a JSON object matching the ManipulationAssessment model:
1.  is_manipulative (bool): Overall assessment of whether manipulation is present in the provided transcript.
2.  manipulation_score (float, 0.0 to 1.0): A score indicating the likelihood and intensity of manipulation. 0.0 means no manipulation, 1.0 means strong and clear manipulation.
3.  manipulation_techniques (List[str]): Identify specific manipulation techniques observed (e.g., "Gaslighting", "Guilt-tripping", "Love bombing", "Appeal to pity", "Intimidation", "Minimization", "Threatening", "Flattery", "Playing the victim").
4.  manipulation_confidence (float, 0.0 to 1.0): Your confidence in this overall manipulation assessment (is_manipulative, score, techniques).
5.  manipulation_explanation (str): A concise explanation for your overall assessment (is_manipulative). Cite specific examples or phrases from the transcript that support your findings for the identified techniques.
6.  manipulation_score_analysis (str): Provide a detailed analysis and reasoning behind the specific 'manipulation_score' you assigned. Explain how the presence, absence, or combination of techniques and their perceived intensity in the transcript led to this score. For example, if the score is 0.7, explain what factors make it high but not 1.0.

JSON structure to be returned:
{{
  "is_manipulative": bool,
  "manipulation_score": float,
  "manipulation_techniques": ["technique1", "technique2"],
  "manipulation_confidence": float,
  "manipulation_explanation": "...",
  "manipulation_score_analysis": "..."
}}
If a field cannot be determined or is not applicable, use a sensible default (e.g., false for boolean, 0.0 for float, empty list for lists, or "Analysis not available." for strings).
Focus your analysis solely on the provided transcript and session context.
"""

        try:
            raw_analysis = await self.gemini_service.query_gemini_for_raw_json(prompt)
            if raw_analysis:
                data = json.loads(raw_analysis)
                # Ensure all fields from the model are present, with defaults if missing
                return ManipulationAssessment(
                    is_manipulative=data.get("is_manipulative", False),
                    manipulation_score=data.get("manipulation_score", 0.0),
                    manipulation_techniques=data.get("manipulation_techniques", []),
                    manipulation_confidence=data.get("manipulation_confidence", 0.0),
                    manipulation_explanation=data.get("manipulation_explanation", "Analysis not available."),
                    manipulation_score_analysis=data.get("manipulation_score_analysis", "Analysis not available.")
                )
            else:
                return self._fallback_text_analysis(transcript)
        except Exception as e:
            logger.error(f"Error in ManipulationService LLM call: {e}")
            return self._fallback_text_analysis(transcript)

    def _fallback_text_analysis(self, transcript: str) -> ManipulationAssessment:
        logger.info(f"Performing fallback manipulation assessment for transcript snippet: {transcript[:100]}...")
        techniques = []
        explanation = "No significant manipulative tactics detected in this fallback analysis."
        score = 0.0
        is_manipulative = False
        confidence = 0.3 # Low confidence for fallback

        if "you always" in transcript.lower() or "you never" in transcript.lower():
            techniques.append("Overgeneralization/Absolutes")
            score += 0.2
            is_manipulative = True
        if "if you really loved me" in transcript.lower() or "a good person would" in transcript.lower():
            techniques.append("Guilt-tripping/Moralizing")
            score += 0.3
            is_manipulative = True
        
        if techniques:
            explanation = f"Fallback analysis detected potential manipulative tactics: {', '.join(techniques)}."
        
        score = min(score, 1.0)

        return ManipulationAssessment(
            is_manipulative=is_manipulative,
            manipulation_score=score,
            manipulation_techniques=techniques,
            manipulation_confidence=confidence,
            manipulation_explanation=explanation,
            manipulation_score_analysis=f"Fallback score ({score:.2f}) implies low/moderate manipulation likelihood based on keyword matching."
        )

# Remove the global instance if services are to be instantiated by the main pipeline
# manipulation_service = ManipulationService()
