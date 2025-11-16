"""EnhancedUnderstandingService v2

Migrated from backend.services.enhanced_understanding_service to follow the v2 streaming protocol.
Analyzes key topics, action items, inconsistencies, evasiveness, and provides deep understanding.
"""
import logging
from typing import Optional, Dict, Any, AsyncGenerator, List

from backend.models import EnhancedUnderstanding
from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.gemini_client import GeminiClientV2

logger = logging.getLogger(__name__)


class EnhancedUnderstandingServiceV2(AnalysisService):
    """V2 service for enhanced understanding analysis with streaming support."""
    
    serviceName = "enhanced_understanding"
    serviceVersion = "2.0"
    
    def __init__(self, gemini_client: Optional[GeminiClientV2] = None, transcript: str = "", meta: Optional[Dict[str, Any]] = None, **kwargs):
        self.gemini_client = gemini_client or GeminiClientV2()
        super().__init__(transcript=transcript, meta=meta)
    
    def _get_fallback_result(self) -> EnhancedUnderstanding:
        """Return fallback analysis when LLM fails."""
        return EnhancedUnderstanding(
            key_topics=[],
            action_items=[],
            unresolved_questions=[],
            summary_of_understanding="Analysis not available (fallback).",
            contextual_insights=[],
            nuances_detected=[],
            key_inconsistencies=[],
            areas_of_evasiveness=[],
            suggested_follow_up_questions=[],
            unverified_claims=[],
            key_inconsistencies_analysis="Analysis not available (fallback).",
            areas_of_evasiveness_analysis="Analysis not available (fallback).",
            suggested_follow_up_questions_analysis="Analysis not available (fallback).",
            fact_checking_analysis="Analysis not available (fallback).",
            deep_dive_analysis="Analysis not available (fallback)."
        )
    
    async def _perform_analysis(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> EnhancedUnderstanding:
        """Perform the actual enhanced understanding analysis using Gemini."""
        if not transcript or len(transcript.strip()) < 10:
            return self._get_fallback_result()
        
        prompt = f"""Analyze the following transcript for enhanced understanding.

Transcript:
"{transcript}"

Session Context:
{session_context if session_context else "No additional session context provided."}

Provide your analysis as a JSON object with the following fields:
1. key_topics (List[str]): Main topics discussed
2. action_items (List[str]): Clear action items or tasks mentioned
3. unresolved_questions (List[str]): Questions asked but not answered
4. summary_of_understanding (str): Concise summary of core understanding
5. contextual_insights (List[str]): Insights from considering broader context
6. nuances_detected (List[str]): Subtle communication nuances
7. key_inconsistencies (List[str]): Contradictory statements
8. areas_of_evasiveness (List[str]): Topics where direct answers were avoided
9. suggested_follow_up_questions (List[str]): Questions to clarify or probe further
10. unverified_claims (List[str]): Claims needing fact-checking
11. key_inconsistencies_analysis (str): Analysis of inconsistency implications
12. areas_of_evasiveness_analysis (str): Reasons/implications of evasiveness
13. suggested_follow_up_questions_analysis (str): Explanation of follow-up questions
14. fact_checking_analysis (str): Why claims need fact-checking
15. deep_dive_analysis (str): Overall synthesis of enhanced understanding

Return valid JSON matching this structure."""

        try:
            result = await self.gemini_client.query_json(prompt)
            
            if not isinstance(result, dict):
                logger.warning(f"Gemini returned non-dict result: {type(result)}")
                return self._get_fallback_result()
            
            # Helper to ensure list fields are lists
            def ensure_list(value, default=[]) -> List:
                if isinstance(value, list):
                    return value
                return default
            
            return EnhancedUnderstanding(
                key_topics=ensure_list(result.get("key_topics")),
                action_items=ensure_list(result.get("action_items")),
                unresolved_questions=ensure_list(result.get("unresolved_questions")),
                summary_of_understanding=result.get("summary_of_understanding", "Analysis not available."),
                contextual_insights=ensure_list(result.get("contextual_insights")),
                nuances_detected=ensure_list(result.get("nuances_detected")),
                key_inconsistencies=ensure_list(result.get("key_inconsistencies")),
                areas_of_evasiveness=ensure_list(result.get("areas_of_evasiveness")),
                suggested_follow_up_questions=ensure_list(result.get("suggested_follow_up_questions")),
                unverified_claims=ensure_list(result.get("unverified_claims")),
                key_inconsistencies_analysis=result.get("key_inconsistencies_analysis", "Analysis not available."),
                areas_of_evasiveness_analysis=result.get("areas_of_evasiveness_analysis", "Analysis not available."),
                suggested_follow_up_questions_analysis=result.get("suggested_follow_up_questions_analysis", "Analysis not available."),
                fact_checking_analysis=result.get("fact_checking_analysis", "Analysis not available."),
                deep_dive_analysis=result.get("deep_dive_analysis", "Analysis not available.")
            )
        except Exception as e:
            logger.error(f"Enhanced understanding analysis failed: {e}", exc_info=True)
            return self._get_fallback_result()
    
    async def stream_analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream enhanced understanding analysis with pseudo-streaming (coarse → final)."""
        meta = meta or {}
        ctx = meta.get("analysis_context")
        
        # Get effective transcript
        effective_transcript = transcript or ""
        if ctx:
            effective_transcript = ctx.transcript_final or ctx.transcript_partial or transcript or ""
        
        if not effective_transcript or len(effective_transcript.split()) < 10:
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": {},
                "gemini": None,
                "errors": [{"error": "Insufficient transcript for enhanced understanding analysis"}],
                "partial": False,
                "phase": "final",
                "chunk_index": None,
            }
            return
        
        # Phase 1: Coarse - quick placeholder
        yield {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {"status": "analyzing_understanding"},
            "gemini": None,
            "errors": [],
            "partial": True,
            "phase": "coarse",
            "chunk_index": 0,
        }
        
        # Phase 2: Perform full analysis
        session_context = meta.get("session_context") or meta.get("session_summary")
        analysis_result = await self._perform_analysis(effective_transcript, session_context)
        
        # Convert to dict safely
        if hasattr(analysis_result, 'model_dump'):
            result_dict = analysis_result.model_dump()
        elif hasattr(analysis_result, '__dict__'):
            result_dict = analysis_result.__dict__
        else:
            result_dict = {}
        
        # Update context
        if ctx:
            ctx.service_results["enhanced_understanding"] = result_dict
        
        # Phase 3: Final result
        yield {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {},
            "gemini": result_dict,
            "errors": [],
            "partial": False,
            "phase": "final",
            "chunk_index": 1,
        }
