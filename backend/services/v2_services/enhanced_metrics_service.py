"""
Enhanced Metrics Service v2
Integrates EnhancedAcousticService and LinguisticEnhancementService into the v2 pipeline.
"""

import logging
from typing import Optional, Dict, Any, AsyncGenerator

from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.enhanced_acoustic_service import EnhancedAcousticService
from backend.services.linguistic_enhancement_service import LinguisticEnhancementService
from backend.models import (
    EnhancedAcousticMetrics,
    LinguisticEnhancementMetrics,
    ErrorResponse
)

logger = logging.getLogger(__name__)


class EnhancedMetricsService(AnalysisService):
    """
    V2 service for extracting enhanced acoustic and linguistic metrics.
    Integrates parselmouth-based acoustic analysis with advanced linguistic features.
    """
    serviceName = "enhanced_metrics"
    serviceVersion = "2.0"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.acoustic_service = EnhancedAcousticService()
        self.linguistic_service = LinguisticEnhancementService()
        logger.info("EnhancedMetricsService initialized.")
    
    async def stream_analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream enhanced metrics extraction.
        
        Yields:
        - Coarse phase: Quick linguistic metrics from partial transcript
        - Final phase: Full acoustic + linguistic metrics
        """
        meta = meta or {}
        context = meta.get("analysis_context")
        errors = []
        
        # Phase 1: Coarse linguistic analysis from partial transcript
        if transcript or (context and context.transcript_partial):
            text = transcript or context.transcript_partial
            
            try:
                # Extract basic linguistic metrics quickly
                linguistic_metrics = self.linguistic_service.extract_linguistic_metrics(text)
                
                # Update context if available
                if context:
                    context.linguistic_metrics = linguistic_metrics.model_dump()
                
                yield {
                    "service_name": self.serviceName,
                    "service_version": self.serviceVersion,
                    "local": {
                        "linguistic_metrics": linguistic_metrics.model_dump()
                    },
                    "gemini": {},
                    "errors": [],
                    "partial": True,
                    "phase": "coarse",
                    "chunk_index": 0
                }
            except Exception as e:
                logger.error(f"Coarse linguistic analysis failed: {e}", exc_info=True)
                errors.append(ErrorResponse(
                    error=f"Linguistic analysis failed: {str(e)}",
                    code=500
                ).model_dump())
        
        # Phase 2: Full analysis with acoustic metrics (when audio available)
        final_transcript = None
        if context and context.transcript_final:
            final_transcript = context.transcript_final
        elif transcript:
            final_transcript = transcript
        
        if audio and final_transcript:
            try:
                # Extract audio metadata from context or meta
                sample_rate = meta.get("sample_rate", 16000)
                channels = meta.get("channels", 1)
                duration = meta.get("duration")
                
                # If context has audio_summary, use it
                if context and context.audio_summary:
                    sample_rate = context.audio_summary.get("sample_rate", sample_rate)
                    channels = context.audio_summary.get("channels", channels)
                    duration = context.audio_summary.get("duration", duration)
                
                # Extract enhanced acoustic metrics
                acoustic_metrics = self.acoustic_service.extract_enhanced_metrics(
                    audio_bytes=audio,
                    sample_rate=sample_rate,
                    channels=channels,
                    transcript=final_transcript,
                    duration_seconds=duration
                )
                
                # Extract enhanced linguistic metrics with acoustic context
                acoustic_emotions = []  # Could extract from context if available
                linguistic_sentiment = None  # Could extract from context if available
                
                if context and context.service_results:
                    # Try to get emotions from previous services
                    if "emotion_analysis" in context.service_results:
                        emotion_data = context.service_results["emotion_analysis"]
                        acoustic_emotions = emotion_data.get("local", {}).get("emotions", [])
                    
                    # Try to get sentiment from previous services
                    if "sentiment_analysis" in context.service_results:
                        sentiment_data = context.service_results["sentiment_analysis"]
                        linguistic_sentiment = sentiment_data.get("local", {}).get("sentiment")
                
                linguistic_metrics = self.linguistic_service.extract_linguistic_metrics(
                    text=final_transcript,
                    acoustic_emotions=acoustic_emotions,
                    linguistic_sentiment=linguistic_sentiment
                )
                
                # Update context with enhanced metrics
                if context:
                    context.acoustic_metrics = acoustic_metrics.model_dump()
                    context.linguistic_metrics = linguistic_metrics.model_dump()
                
                yield {
                    "service_name": self.serviceName,
                    "service_version": self.serviceVersion,
                    "local": {
                        "acoustic_metrics": acoustic_metrics.model_dump(),
                        "linguistic_metrics": linguistic_metrics.model_dump()
                    },
                    "gemini": {},
                    "errors": errors,
                    "partial": False,
                    "phase": "final",
                    "chunk_index": 1
                }
                
            except Exception as e:
                logger.error(f"Enhanced metrics extraction failed: {e}", exc_info=True)
                errors.append(ErrorResponse(
                    error=f"Enhanced metrics extraction failed: {str(e)}",
                    code=500
                ).model_dump())
                
                # Yield error result
                yield {
                    "service_name": self.serviceName,
                    "service_version": self.serviceVersion,
                    "local": {},
                    "gemini": {},
                    "errors": errors,
                    "partial": False,
                    "phase": "final",
                    "chunk_index": 1
                }
        elif final_transcript:
            # Only linguistic metrics available (no audio)
            try:
                linguistic_metrics = self.linguistic_service.extract_linguistic_metrics(final_transcript)
                
                if context:
                    context.linguistic_metrics = linguistic_metrics.model_dump()
                
                yield {
                    "service_name": self.serviceName,
                    "service_version": self.serviceVersion,
                    "local": {
                        "linguistic_metrics": linguistic_metrics.model_dump(),
                        "note": "Audio not available - acoustic metrics not extracted"
                    },
                    "gemini": {},
                    "errors": errors,
                    "partial": False,
                    "phase": "final",
                    "chunk_index": 1
                }
            except Exception as e:
                logger.error(f"Linguistic metrics extraction failed: {e}", exc_info=True)
                errors.append(ErrorResponse(
                    error=f"Linguistic metrics extraction failed: {str(e)}",
                    code=500
                ).model_dump())
                
                yield {
                    "service_name": self.serviceName,
                    "service_version": self.serviceVersion,
                    "local": {},
                    "gemini": {},
                    "errors": errors,
                    "partial": False,
                    "phase": "final",
                    "chunk_index": 1
                }
    
    async def analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Non-streaming analyze method (consumes stream_analyze).
        """
        final_result = {}
        async for chunk in self.stream_analyze(transcript, audio, meta):
            if not chunk.get("partial", False):
                final_result = chunk
        
        return final_result
