"""LinguisticService v2

Migrated from backend.services.linguistic_service to follow the v2 streaming protocol.
Provides advanced linguistic pattern analysis beyond basic quantitative metrics.

Note: Basic numerical metrics (word count, speech rate, etc.) are handled by QuantitativeMetricsService.
This service focuses on formality, complexity, and linguistic interpretation.
"""
import logging
from typing import Optional, Dict, Any, AsyncGenerator

from backend.models import LinguisticAnalysis
from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.gemini_client import GeminiClientV2

logger = logging.getLogger(__name__)


class LinguisticServiceV2(AnalysisService):
    """V2 service for linguistic pattern analysis with streaming support."""
    
    serviceName = "linguistic"
    serviceVersion = "2.0"
    
    def __init__(self, gemini_client: Optional[GeminiClientV2] = None, transcript: str = "", meta: Optional[Dict[str, Any]] = None, **kwargs):
        self.gemini_client = gemini_client or GeminiClientV2()
        super().__init__(transcript=transcript, meta=meta)
    
    def _get_fallback_result(self) -> LinguisticAnalysis:
        """Return fallback analysis when LLM fails."""
        return LinguisticAnalysis(
            linguistic_interpretation_summary="Analysis not available (fallback).",
            linguistic_patterns=[],
            confidence_linguistic=0.5,
            hedging_analysis="Analysis not available (fallback).",
            certainty_analysis="Analysis not available (fallback).",
            formality_analysis="Analysis not available (fallback).",
            complexity_analysis="Analysis not available (fallback).",
            hesitation_interpretation="Analysis not available (fallback).",
            repetition_interpretation="Analysis not available (fallback).",
            speech_rate_interpretation="Analysis not available (fallback)."
        )
    
    async def _perform_analysis(
        self,
        transcript: str,
        numerical_metrics: Optional[Dict[str, Any]] = None
    ) -> LinguisticAnalysis:
        """Perform linguistic pattern analysis using Gemini."""
        if not transcript or len(transcript.strip()) < 10:
            return self._get_fallback_result()
        
        # Build context from numerical metrics if available
        metrics_context = ""
        if numerical_metrics:
            metrics_context = f"""
Numerical Metrics Available:
- Word count: {numerical_metrics.get('word_count', 'unknown')}
- Speech rate: {numerical_metrics.get('speech_rate_wpm', 'unknown')} wpm
- Hesitation markers: {numerical_metrics.get('hesitation_marker_count', 'unknown')}
- Qualifiers: {numerical_metrics.get('qualifier_count', 'unknown')}
- Certainty indicators: {numerical_metrics.get('certainty_indicator_count', 'unknown')}
"""
        
        prompt = f"""Analyze the linguistic patterns in the following transcript.

Transcript:
"{transcript}"

{metrics_context}

Provide your analysis as a JSON object with the following fields:
1. linguistic_interpretation_summary (str): Overall summary of linguistic patterns
2. linguistic_patterns (List[str]): Key patterns detected (e.g., "frequent hedging", "formal tone")
3. confidence_linguistic (float, 0.0-1.0): Confidence in this linguistic analysis
4. hedging_analysis (str): Analysis of hedging language and uncertainty markers
5. certainty_analysis (str): Analysis of confidence and certainty expressions
6. formality_analysis (str): Assessment of language formality with examples
7. complexity_analysis (str): Assessment of linguistic complexity (vocabulary, structure)
8. hesitation_interpretation (str): Interpretation of hesitations and fillers
9. repetition_interpretation (str): Analysis of repetitive patterns
10. speech_rate_interpretation (str): Interpretation of speech rate if metrics available

Return valid JSON matching this structure."""

        try:
            result = await self.gemini_client.query_json(prompt)
            
            if not isinstance(result, dict):
                logger.warning(f"Gemini returned non-dict result: {type(result)}")
                return self._get_fallback_result()
            
            # Ensure linguistic_patterns is a list
            patterns = result.get("linguistic_patterns", [])
            if not isinstance(patterns, list):
                patterns = []
            
            return LinguisticAnalysis(
                linguistic_interpretation_summary=result.get("linguistic_interpretation_summary", "Analysis not available."),
                linguistic_patterns=patterns,
                confidence_linguistic=float(result.get("confidence_linguistic", 0.5)),
                hedging_analysis=result.get("hedging_analysis", "Analysis not available."),
                certainty_analysis=result.get("certainty_analysis", "Analysis not available."),
                formality_analysis=result.get("formality_analysis", "Analysis not available."),
                complexity_analysis=result.get("complexity_analysis", "Analysis not available."),
                hesitation_interpretation=result.get("hesitation_interpretation", "Analysis not available."),
                repetition_interpretation=result.get("repetition_interpretation", "Analysis not available."),
                speech_rate_interpretation=result.get("speech_rate_interpretation", "Analysis not available.")
            )
        except Exception as e:
            logger.error(f"Linguistic analysis failed: {e}", exc_info=True)
            return self._get_fallback_result()
    
    async def stream_analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream linguistic analysis with pseudo-streaming (coarse → final)."""
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
                "errors": [{"error": "Insufficient transcript for linguistic analysis"}],
                "partial": False,
                "phase": "final",
                "chunk_index": None,
            }
            return
        
        # Phase 1: Coarse - quick placeholder
        yield {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {"status": "analyzing_linguistic_patterns"},
            "gemini": None,
            "errors": [],
            "partial": True,
            "phase": "coarse",
            "chunk_index": 0,
        }
        
        # Get numerical metrics from context if available
        numerical_metrics = None
        if ctx and ctx.quantitative_metrics:
            numerical_metrics = ctx.quantitative_metrics.get("numerical_linguistic_metrics")
        
        # Phase 2: Perform full analysis
        analysis_result = await self._perform_analysis(effective_transcript, numerical_metrics)
        
        # Convert to dict safely
        if hasattr(analysis_result, 'model_dump'):
            result_dict = analysis_result.model_dump()
        elif hasattr(analysis_result, '__dict__'):
            result_dict = analysis_result.__dict__
        else:
            result_dict = {}
        
        # Update context
        if ctx:
            ctx.service_results["linguistic"] = result_dict
        
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
