"""SpeakerAttitudeService v2

Migrated from backend.services.speaker_attitude_service to follow the v2 streaming protocol.
Analyzes speaker attitude, respect level, formality, and politeness.
"""
import logging
from typing import Optional, Dict, Any, AsyncGenerator

from backend.models import SpeakerAttitude
from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.gemini_client import GeminiClientV2

logger = logging.getLogger(__name__)


class SpeakerAttitudeServiceV2(AnalysisService):
    """V2 service for speaker attitude analysis with streaming support."""
    
    serviceName = "speaker_attitude"
    serviceVersion = "2.0"
    
    def __init__(self, gemini_client: Optional[GeminiClientV2] = None, transcript: str = "", meta: Optional[Dict[str, Any]] = None, **kwargs):
        self.gemini_client = gemini_client or GeminiClientV2()
        super().__init__(transcript=transcript, meta=meta)
    
    def _get_fallback_result(self) -> SpeakerAttitude:
        """Return fallback analysis when LLM fails."""
        return SpeakerAttitude(
            dominant_attitude="Neutral",
            attitude_scores={},
            respect_level="Neutral",
            respect_level_score=0.5,
            respect_level_score_analysis="Analysis not available (fallback).",
            formality_score=0.5,
            formality_assessment="Analysis not available (fallback).",
            politeness_score=0.5,
            politeness_assessment="Analysis not available (fallback)."
        )
    
    async def _perform_analysis(self, transcript: str, session_context: Optional[Dict[str, Any]] = None) -> SpeakerAttitude:
        """Perform the actual speaker attitude analysis using Gemini."""
        if not transcript or len(transcript.strip()) < 10:
            return self._get_fallback_result()
        
        prompt = f"""Analyze the speaker's attitude in the following transcript.

Transcript:
"{transcript}"

Session Context:
{session_context if session_context else "No additional session context provided."}

Provide your analysis as a JSON object with the following fields:
1. dominant_attitude (str): Dominant attitude (e.g., "Cooperative", "Hostile", "Neutral", "Supportive")
2. attitude_scores (Dict[str, float]): Scores (0.0-1.0) for various attitudes, e.g., {{"polite": 0.8, "impatient": 0.6}}
3. respect_level (str): Qualitative respect level (e.g., "Respectful", "Disrespectful", "Neutral")
4. respect_level_score (float, 0.0-1.0): Numerical respect score
5. respect_level_score_analysis (str): Detailed reasoning for respect score
6. formality_score (float, 0.0-1.0): Language formality score
7. formality_assessment (str): Qualitative formality assessment with examples
8. politeness_score (float, 0.0-1.0): Politeness level score
9. politeness_assessment (str): Qualitative politeness assessment with examples

Return valid JSON matching this structure."""

        try:
            result = await self.gemini_client.query_json(prompt)
            
            # Ensure we have a dict
            if not isinstance(result, dict):
                logger.warning(f"Gemini returned non-dict result: {type(result)}")
                return self._get_fallback_result()
            
            # Build the model with defaults for missing fields
            return SpeakerAttitude(
                dominant_attitude=result.get("dominant_attitude", "Neutral"),
                attitude_scores=result.get("attitude_scores", {}),
                respect_level=result.get("respect_level", "Neutral"),
                respect_level_score=float(result.get("respect_level_score", 0.5)),
                respect_level_score_analysis=result.get("respect_level_score_analysis", "Analysis not available."),
                formality_score=float(result.get("formality_score", 0.5)),
                formality_assessment=result.get("formality_assessment", "Analysis not available."),
                politeness_score=float(result.get("politeness_score", 0.5)),
                politeness_assessment=result.get("politeness_assessment", "Analysis not available.")
            )
        except Exception as e:
            logger.error(f"Speaker attitude analysis failed: {e}", exc_info=True)
            return self._get_fallback_result()
    
    async def stream_analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream speaker attitude analysis with pseudo-streaming (coarse → final)."""
        meta = meta or {}
        ctx = meta.get("analysis_context")
        
        # Get effective transcript
        effective_transcript = transcript or ""
        if ctx:
            effective_transcript = ctx.transcript_final or ctx.transcript_partial or transcript or ""
        
        if not effective_transcript or len(effective_transcript.split()) < 5:
            # Not enough data
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": {},
                "gemini": None,
                "errors": [{"error": "Insufficient transcript for speaker attitude analysis"}],
                "partial": False,
                "phase": "final",
                "chunk_index": None,
            }
            return
        
        # Phase 1: Coarse - emit quick placeholder
        yield {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {"status": "analyzing_attitude"},
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
        
        # Update context if available
        if ctx:
            ctx.service_results["speaker_attitude"] = result_dict
        
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
