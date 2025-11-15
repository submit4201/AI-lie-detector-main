# backend/services/enhanced_understanding_service.py
import logging
import json
from typing import Dict, Any, Optional, TYPE_CHECKING
from backend.models import EnhancedUnderstanding # Ensure this import is correct

# Use TYPE_CHECKING to avoid circular import while keeping type hints
if TYPE_CHECKING:
    from backend.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class EnhancedUnderstandingService:
    def __init__(self, gemini_service: Optional["GeminiService"] = None): # Added Optional and default
        if gemini_service is None:
            # Import here to avoid circular import at module level
            from backend.services.gemini_service import GeminiService
            gemini_service = GeminiService()
        self.gemini_service = gemini_service

    def _fallback_analysis(self, transcript_snippet: str) -> EnhancedUnderstanding:
        logger.warning(f"EnhancedUnderstandingService: LLM call failed or returned malformed data for transcript snippet: {transcript_snippet}. Falling back to default.")
        # Ensure fallback returns all fields expected by EnhancedUnderstanding
        return EnhancedUnderstanding(
            key_topics=[],
            action_items=[],
            unresolved_questions=[],
            summary_of_understanding="Fallback: Analysis not available.",
            contextual_insights=[],
            nuances_detected=[],
            key_inconsistencies=[],
            areas_of_evasiveness=[],
            suggested_follow_up_questions=[],
            unverified_claims=[],
            key_inconsistencies_analysis="Fallback: Analysis not available.",
            areas_of_evasiveness_analysis="Fallback: Analysis not available.",
            suggested_follow_up_questions_analysis="Fallback: Analysis not available.",
            fact_checking_analysis="Fallback: Analysis not available.",
            deep_dive_analysis="Fallback: Analysis not available."
        )

    async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> EnhancedUnderstanding: # Added Optional
        """
        Performs enhanced understanding analysis on the given transcript using an LLM.
        """
        transcript_snippet = transcript[:500]
        logger.info(f"Performing enhanced understanding analysis for transcript snippet: {transcript_snippet}...")

        prompt = f"""
Analyze the following transcript for enhanced understanding.
Transcript:
"{transcript}"

Session Context (if available, use for nuanced understanding):
{json.dumps(session_context) if session_context else "No additional session context provided."}

Based on the transcript and context, provide your analysis as a JSON object matching the EnhancedUnderstanding model fields below:
1.  key_topics (List[str]): Identify the main topics discussed in the transcript.
2.  action_items (List[str]): List any clear action items or tasks mentioned.
3.  unresolved_questions (List[str]): List any questions asked by any party that were not answered in the transcript.
4.  summary_of_understanding (str): Provide a concise summary of the core understanding derived from the transcript. What are the main takeaways?
5.  contextual_insights (List[str]): List any insights that can be derived by considering the broader context (if provided) alongside the transcript.
6.  nuances_detected (List[str]): Identify any subtle nuances in communication (e.g., implied meanings, sarcasm if not covered by attitude, subtle shifts in topic/tone).
7.  key_inconsistencies (List[str]): List specific statements or pieces of information within the transcript that contradict each other.
8.  areas_of_evasiveness (List[str]): Identify topics or direct questions where the speaker(s) seem to avoid giving a direct answer.
9.  suggested_follow_up_questions (List[str]): Based on the analysis (e.g., inconsistencies, evasiveness, unresolved questions), suggest specific follow-up questions that could be asked to clarify information or probe further.
10. unverified_claims (List[str]): List any claims made by the speaker(s) that sound like they might need external fact-checking.
11. key_inconsistencies_analysis (str): For the identified 'key_inconsistencies', provide a brief analysis of their potential implications. Why do these inconsistencies matter in the context of the conversation?
12. areas_of_evasiveness_analysis (str): For the identified 'areas_of_evasiveness', explain the potential reasons for or implications of this evasiveness.
13. suggested_follow_up_questions_analysis (str): For each 'suggested_follow_up_question', briefly explain what clarification or insight the question aims to achieve.
14. fact_checking_analysis (str): For the 'unverified_claims', explain why they might need fact-checking and the potential impact if they are inaccurate.
15. deep_dive_analysis (str): Provide an overall 'deep dive' synthesis of the enhanced understanding. How do the various elements (topics, inconsistencies, evasiveness, etc.) fit together to paint a fuller picture of the communication?

JSON structure to be returned:
{{
  "key_topics": [],
  "action_items": [],
  "unresolved_questions": [],
  "summary_of_understanding": "...",
  "contextual_insights": [],
  "nuances_detected": [],
  "key_inconsistencies": [],
  "areas_of_evasiveness": [],
  "suggested_follow_up_questions": [],
  "unverified_claims": [],
  "key_inconsistencies_analysis": "...",
  "areas_of_evasiveness_analysis": "...",
  "suggested_follow_up_questions_analysis": "...",
  "fact_checking_analysis": "...",
  "deep_dive_analysis": "..."
}}
If a field cannot be determined or is not applicable, use a sensible default (e.g., empty list for lists, or "Analysis not available." for strings).
Focus your analysis solely on the provided transcript and session context.
"""
        try:
            raw_analysis = await self.gemini_service.query_gemini_for_raw_json(prompt) # Changed from raw_response
            if raw_analysis: # Changed from raw_response
                data = json.loads(raw_analysis) # Added this line
                # Ensure all fields from the model are present, with defaults if missing
                return EnhancedUnderstanding(
                    key_topics=data.get("key_topics", []),
                    action_items=data.get("action_items", []),
                    unresolved_questions=data.get("unresolved_questions", []),
                    summary_of_understanding=data.get("summary_of_understanding", "Analysis not available."),
                    contextual_insights=data.get("contextual_insights", []),
                    nuances_detected=data.get("nuances_detected", []),
                    key_inconsistencies=data.get("key_inconsistencies", []),
                    areas_of_evasiveness=data.get("areas_of_evasiveness", []),
                    suggested_follow_up_questions=data.get("suggested_follow_up_questions", []),
                    unverified_claims=data.get("unverified_claims", []),
                    key_inconsistencies_analysis=data.get("key_inconsistencies_analysis", "Analysis not available."),
                    areas_of_evasiveness_analysis=data.get("areas_of_evasiveness_analysis", "Analysis not available."),
                    suggested_follow_up_questions_analysis=data.get("suggested_follow_up_questions_analysis", "Analysis not available."),
                    fact_checking_analysis=data.get("fact_checking_analysis", "Analysis not available."),
                    deep_dive_analysis=data.get("deep_dive_analysis", "Analysis not available.")
                )
            else:
                logger.warning(f"EnhancedUnderstandingService: Received no response from LLM for transcript snippet: {transcript_snippet}.")
                return self._fallback_analysis(transcript_snippet)
        except (json.JSONDecodeError, TypeError) as e: # Keep Exception for broader unexpected issues
            logger.error(f"EnhancedUnderstandingService: Error processing LLM response for transcript snippet: {transcript_snippet}. Error: {e}")
            return self._fallback_analysis(transcript_snippet)
        except Exception as e:
            logger.error(f"EnhancedUnderstandingService: Unexpected error during analysis for transcript snippet: {transcript_snippet}. Error: {e}")
            return self._fallback_analysis(transcript_snippet)

# enhanced_understanding_service = EnhancedUnderstandingService() # Commented out global instantiation
