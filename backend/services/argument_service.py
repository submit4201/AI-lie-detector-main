# backend/services/argument_service.py
import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from backend.models import ArgumentAnalysis
import json

# Use TYPE_CHECKING to avoid circular import while keeping type hints
if TYPE_CHECKING:
    from backend.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

# Import sanitization function for secure logging
from backend.services.logging_utils import sanitize_for_logging as _sanitize_for_logging

class ArgumentService:
    def __init__(self, gemini_service: Optional["GeminiService"] = None):
        if gemini_service is None:
            # Import here to avoid circular import at module level
            from backend.services.gemini_service import GeminiService
            gemini_service = GeminiService()
        self.gemini_service = gemini_service

    async def analyze(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> ArgumentAnalysis:
        if not transcript:
            return ArgumentAnalysis()

        prompt = f"""Analyze the following transcript for its argument structure.
Transcript:
"{transcript}"

Session Context (if available, use for nuanced understanding):
{json.dumps(session_context) if session_context else "No additional session context provided."}

Identify and evaluate the arguments present. Provide your analysis as a JSON object matching the ArgumentAnalysis model fields below:
1.  arguments_present (bool): Are there identifiable arguments (claims supported by reasons/evidence) in the transcript?
2.  key_arguments (List[Dict[str, str]]): List key arguments. Each argument should be a dictionary with a "claim" (the main point or conclusion) and "evidence" (the reasons, facts, or data supporting the claim). If multiple pieces of evidence support one claim, list them or summarize. If a claim has no clear evidence, state that.
    Example: [{{"claim": "The new policy is effective.", "evidence": "Data shows a 20% increase in efficiency since implementation."}}]
3.  argument_strength (float, 0.0 to 1.0): Your overall assessment of the strength of the arguments presented. Consider factors like the quality of evidence, logical coherence, and relevance. 0.0 means very weak or no argument, 1.0 means very strong.
4.  fallacies_detected (List[str]): Identify any logical fallacies present in the arguments (e.g., "Ad hominem", "Straw man", "Appeal to emotion", "False dilemma", "Hasty generalization"). List them.
5.  argument_summary (str): Provide a concise summary of the main arguments identified in the transcript. This should capture the essence of what is being argued for or against.
6.  argument_structure_rating (float, 0.0 to 1.0): Rate how well-structured the arguments are. Consider clarity, organization, and logical flow. 0.0 means very poorly structured, 1.0 means very well-structured.
7.  argument_structure_analysis (str): Provide a detailed analysis and reasoning for the 'argument_structure_rating'. Explain what makes the structure good or bad. For example, are claims clearly stated? Is evidence directly linked to claims? Is there a logical progression of points? Are there counter-arguments addressed?

JSON structure to be returned:
{{
  "arguments_present": bool,
  "key_arguments": [{{"claim": "text", "evidence": "text"}}],
  "argument_strength": float,
  "fallacies_detected": ["fallacy1"],
  "argument_summary": "...",
  "argument_structure_rating": float,
  "argument_structure_analysis": "..."
}}
If a field cannot be determined or is not applicable, use a sensible default (e.g., false for boolean, 0.0 for float, empty list for lists, or "Analysis not available." for strings).
Focus your analysis solely on the provided transcript and session context.
"""

        try:
            raw_analysis = await self.gemini_service.query_gemini_for_raw_json(prompt)
            if raw_analysis:
                data = json.loads(raw_analysis)
                return ArgumentAnalysis(
                    arguments_present=data.get("arguments_present", False),
                    key_arguments=data.get("key_arguments", []),
                    argument_strength=data.get("argument_strength", 0.0),
                    fallacies_detected=data.get("fallacies_detected", []),
                    argument_summary=data.get("argument_summary", "Analysis not available."),
                    argument_structure_rating=data.get("argument_structure_rating", 0.0),
                    argument_structure_analysis=data.get("argument_structure_analysis", "Analysis not available.")
                )
            else:
                return self._fallback_text_analysis(transcript)
        except Exception as e:
            logger.error(f"Error in ArgumentService LLM call: {e}")
            return self._fallback_text_analysis(transcript)

    def _fallback_text_analysis(self, transcript: str) -> ArgumentAnalysis:
        logger.info(f"Performing fallback argument analysis for transcript: {_sanitize_for_logging(transcript)}")
        key_args: List[Dict[str, str]] = []
        fallacies: List[str] = []
        summary = "No clear arguments identified by fallback analysis."
        strength = 0.0
        structure_rating = 0.0
        present = False

        if "because" in transcript.lower() and len(transcript.split('.')) > 1:
            present = True
            # Simplistic claim/evidence split for fallback
            parts = transcript.lower().split("because", 1)
            if len(parts) == 2:
                 key_args.append({"claim": parts[0].strip(), "evidence": parts[1].strip()})
            strength += 0.3
            structure_rating += 0.2
            summary = "Fallback: Basic argument structure (claim with 'because') detected."
        
        if "therefore" in transcript.lower() or "so it follows" in transcript.lower():
            present = True
            strength += 0.2
            structure_rating += 0.2
            if not key_args: # Add a general argument if none from 'because'
                key_args.append({"claim": "A conclusion was likely drawn.", "evidence": "Presence of concluding phrases."}) 

        if len(transcript) < 50 and present: # Very short argument
            strength = max(0.1, strength - 0.2)
            structure_rating = max(0.1, structure_rating - 0.2)
            summary += " Argument is very brief."
        elif not present and len(transcript) > 100:
            summary = "Fallback: Transcript is substantial but lacks clear argumentative keywords."

        return ArgumentAnalysis(
            arguments_present=present,
            key_arguments=key_args,
            argument_strength=min(strength, 1.0),
            fallacies_detected=fallacies,
            argument_summary=summary,
            argument_structure_rating=min(structure_rating, 1.0),
            argument_structure_analysis="Fallback analysis based on keyword matching for argument structure."
        )

# argument_service = ArgumentService()
