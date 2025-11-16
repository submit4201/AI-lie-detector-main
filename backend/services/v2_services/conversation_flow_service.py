"""ConversationFlowService v2

Migrated from backend.services.conversation_flow_service to follow the v2 streaming protocol.
Analyzes conversation flow, engagement, turn-taking, and topic coherence.
"""
import logging
from typing import Optional, Dict, Any, AsyncGenerator, List

from backend.models import ConversationFlow
from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.gemini_client import GeminiClientV2

logger = logging.getLogger(__name__)


class ConversationFlowServiceV2(AnalysisService):
    """V2 service for conversation flow analysis with streaming support."""
    
    serviceName = "conversation_flow"
    serviceVersion = "2.0"
    
    def __init__(self, gemini_client: Optional[GeminiClientV2] = None, transcript: str = "", meta: Optional[Dict[str, Any]] = None, **kwargs):
        self.gemini_client = gemini_client or GeminiClientV2()
        super().__init__(transcript=transcript, meta=meta)
    
    def _get_fallback_result(self) -> ConversationFlow:
        """Return fallback analysis when LLM fails."""
        return ConversationFlow(
            engagement_level="Medium",
            topic_coherence_score=0.5,
            conversation_dominance={},
            turn_taking_efficiency="Analysis not available (fallback).",
            conversation_phase="Unknown",
            flow_disruptions=[]
        )
    
    async def _perform_analysis(
        self,
        transcript: str,
        dialogue_acts: Optional[List[Dict[str, Any]]] = None,
        speaker_diarization: Optional[List[Dict[str, Any]]] = None
    ) -> ConversationFlow:
        """Perform the actual conversation flow analysis using Gemini."""
        if not transcript or len(transcript.strip()) < 10:
            return self._get_fallback_result()
        
        # Build summaries for prompt
        dialogue_acts_summary = "Dialogue acts not available."
        if dialogue_acts:
            dialogue_acts_summary = f"Dialogue acts provided: {len(dialogue_acts)} acts"
        
        diarization_summary = "Speaker diarization not available."
        if speaker_diarization:
            diarization_summary = f"Speaker diarization: {len(speaker_diarization)} segments"
        
        prompt = f"""Analyze the conversation flow in the following transcript.

Transcript:
"{transcript}"

{dialogue_acts_summary}
{diarization_summary}

Provide your analysis as a JSON object with the following fields:
1. engagement_level (str): Overall engagement ("Low", "Medium", "High")
2. topic_coherence_score (float, 0.0-1.0): How well topics are maintained
3. conversation_dominance (Dict[str, float]): Speaker contribution proportions
4. turn_taking_efficiency (str): Quality of turn-taking (e.g., "Smooth", "Overlapping")
5. conversation_phase (str): Current phase (e.g., "Opening", "Development", "Closing")
6. flow_disruptions (List[str]): List of flow disruptions detected

Return valid JSON matching this structure."""

        try:
            result = await self.gemini_client.query_json(prompt)
            
            if not isinstance(result, dict):
                logger.warning(f"Gemini returned non-dict result: {type(result)}")
                return self._get_fallback_result()
            
            return ConversationFlow(
                engagement_level=result.get("engagement_level", "Medium"),
                topic_coherence_score=float(result.get("topic_coherence_score", 0.5)),
                conversation_dominance=result.get("conversation_dominance", {}),
                turn_taking_efficiency=result.get("turn_taking_efficiency", "Analysis not available."),
                conversation_phase=result.get("conversation_phase", "Unknown"),
                flow_disruptions=result.get("flow_disruptions", []) if isinstance(result.get("flow_disruptions"), list) else []
            )
        except Exception as e:
            logger.error(f"Conversation flow analysis failed: {e}", exc_info=True)
            return self._get_fallback_result()
    
    async def stream_analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream conversation flow analysis with pseudo-streaming (coarse → final)."""
        meta = meta or {}
        ctx = meta.get("analysis_context")
        
        # Get effective transcript
        effective_transcript = transcript or ""
        if ctx:
            effective_transcript = ctx.transcript_final or ctx.transcript_partial or transcript or ""
        
        # Get speaker diarization and dialogue acts from context
        speaker_diarization = None
        dialogue_acts = None
        if ctx:
            speaker_diarization = ctx.speaker_segments
            # dialogue_acts might be in service_results if another service computed them
            dialogue_acts = ctx.service_results.get("dialogue_acts")
        
        if not effective_transcript or len(effective_transcript.split()) < 10:
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": {},
                "gemini": None,
                "errors": [{"error": "Insufficient transcript for conversation flow analysis"}],
                "partial": False,
                "phase": "final",
                "chunk_index": None,
            }
            return
        
        # Phase 1: Coarse - quick placeholder
        yield {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {"status": "analyzing_conversation_flow"},
            "gemini": None,
            "errors": [],
            "partial": True,
            "phase": "coarse",
            "chunk_index": 0,
        }
        
        # Phase 2: Perform full analysis
        analysis_result = await self._perform_analysis(effective_transcript, dialogue_acts, speaker_diarization)
        
        # Convert to dict safely
        if hasattr(analysis_result, 'model_dump'):
            result_dict = analysis_result.model_dump()
        elif hasattr(analysis_result, '__dict__'):
            result_dict = analysis_result.__dict__
        else:
            result_dict = {}
        
        # Update context
        if ctx:
            ctx.service_results["conversation_flow"] = result_dict
        
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
