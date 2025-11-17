"""PsychologicalService v2

Migrated from backend.services.psychological_service to follow the v2 streaming protocol.
Analyzes psychological state, emotional state, cognitive load, stress, and confidence levels.
"""
import logging
from typing import Optional, Dict, Any, AsyncGenerator

from backend.models import PsychologicalAnalysis
from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.gemini_client import GeminiClientV2

logger = logging.getLogger(__name__)


class PsychologicalServiceV2(AnalysisService):
    """V2 service for psychological analysis with streaming support."""
    
    serviceName = "psychological"
    serviceVersion = "2.0"
    
    def __init__(self, gemini_client: Optional[GeminiClientV2] = None, transcript: str = "", meta: Optional[Dict[str, Any]] = None, **kwargs):
        self.gemini_client = gemini_client or GeminiClientV2()
        super().__init__(transcript=transcript, meta=meta)
    
    def _get_fallback_result(self) -> PsychologicalAnalysis:
        """Return fallback analysis when LLM fails."""
        return PsychologicalAnalysis(
            emotional_state="Neutral",
            emotional_state_analysis="Analysis not available (fallback).",
            cognitive_load="Normal",
            cognitive_load_analysis="Analysis not available (fallback).",
            stress_level=0.5,
            stress_level_analysis="Analysis not available (fallback).",
            confidence_level=0.5,
            confidence_level_analysis="Analysis not available (fallback).",
            psychological_summary="Analysis not available (fallback).",
            potential_biases=[],
            potential_biases_analysis="Analysis not available (fallback)."
        )
    
    async def _perform_analysis(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> PsychologicalAnalysis:
        """Perform the actual psychological analysis using Gemini."""
        if not transcript or len(transcript.strip()) < 10:
            return self._get_fallback_result()
        
        prompt = f"""Analyze the speaker's psychological state based on the following transcript.

Transcript:
"{transcript}"

Session Context:
{session_context if session_context else "No additional session context provided."}

Provide your analysis as a JSON object with the following fields:
1. emotional_state (str): Current emotional state (e.g., "Calm", "Anxious", "Excited", "Frustrated")
2. emotional_state_analysis (str): Detailed explanation with examples from transcript
3. cognitive_load (str): Level of mental processing (e.g., "Low", "Normal", "High", "Overloaded")
4. cognitive_load_analysis (str): Reasoning for cognitive load assessment with evidence
5. stress_level (float, 0.0-1.0): Stress level score
6. stress_level_analysis (str): Detailed stress level reasoning
7. confidence_level (float, 0.0-1.0): Speaker's confidence score
8. confidence_level_analysis (str): Reasoning for confidence assessment
9. psychological_summary (str): Overall psychological state summary
10. potential_biases (List[str]): List of potential cognitive biases detected
11. potential_biases_analysis (str): Explanation of detected biases

Return valid JSON matching this structure."""

        try:
            result = await self.gemini_client.query_json(prompt)
            
            if not isinstance(result, dict):
                logger.warning(f"Gemini returned non-dict result: {type(result)}")
                return self._get_fallback_result()
            
            # Build the model with defaults
            return PsychologicalAnalysis(
                emotional_state=result.get("emotional_state", "Neutral"),
                emotional_state_analysis=result.get("emotional_state_analysis", "Analysis not available."),
                cognitive_load=result.get("cognitive_load", "Normal"),
                cognitive_load_analysis=result.get("cognitive_load_analysis", "Analysis not available."),
                stress_level=float(result.get("stress_level", 0.5)),
                stress_level_analysis=result.get("stress_level_analysis", "Analysis not available."),
                confidence_level=float(result.get("confidence_level", 0.5)),
                confidence_level_analysis=result.get("confidence_level_analysis", "Analysis not available."),
                psychological_summary=result.get("psychological_summary", "Analysis not available."),
                potential_biases=result.get("potential_biases", []),
                potential_biases_analysis=result.get("potential_biases_analysis", "Analysis not available.")
            )
        except Exception as e:
            logger.error(f"Psychological analysis failed: {e}", exc_info=True)
            return self._get_fallback_result()
    
    async def stream_analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream psychological analysis with pseudo-streaming (coarse → final)."""
        meta = meta or {}
        ctx = meta.get("analysis_context")
        
        # Get effective transcript
        effective_transcript = transcript or ""
        if ctx:
            effective_transcript = ctx.transcript_final or ctx.transcript_partial or transcript or ""
        
        if not effective_transcript or len(effective_transcript.split()) < 5:
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": {},
                "gemini": None,
                "errors": [{"error": "Insufficient transcript for psychological analysis"}],
                "partial": False,
                "phase": "final",
                "chunk_index": None,
            }
            return
        
        # Phase 1: Coarse - quick placeholder
        yield {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {"status": "analyzing_psychological_state"},
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
            ctx.service_results["psychological"] = result_dict
        
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
