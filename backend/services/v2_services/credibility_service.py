"""
Credibility Service v2
Provides comprehensive credibility assessment using statistical scoring.
"""

import logging
from typing import Optional, Dict, Any, AsyncGenerator

from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.credibility_scoring_service import CredibilityScoringServiceV2
from backend.models import (
    CredibilityScore,
    EnhancedAcousticMetrics,
    LinguisticEnhancementMetrics,
    BaselineProfile,
    ErrorResponse
)

logger = logging.getLogger(__name__)


class CredibilityServiceV2(AnalysisService):
    """
    V2 service for calculating credibility scores with statistical rigor.
    Integrates acoustic, linguistic, behavioral, and consistency metrics.
    """
    serviceName = "credibility"
    serviceVersion = "2.0"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize with default weights, can be overridden via config
        self.scoring_service = CredibilityScoringServiceV2()
        logger.info("CredibilityServiceV2 initialized.")
    
    async def stream_analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream credibility assessment.
        
        Yields:
        - Coarse phase: Initial credibility estimate from available metrics
        - Final phase: Complete credibility score with all metrics
        """
        meta = meta or {}
        context = meta.get("analysis_context")
        errors = []
        
        # Wait for enhanced metrics to be available
        if not context:
            logger.warning("No analysis context available for credibility assessment")
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": {},
                "gemini": {},
                "errors": [ErrorResponse(
                    error="Analysis context not available",
                    code=400
                ).model_dump()],
                "partial": False,
                "phase": "final",
                "chunk_index": 0
            }
            return
        
        # Phase 1: Coarse assessment from partial metrics
        if context.acoustic_metrics or context.linguistic_metrics:
            try:
                # Parse metrics from context
                acoustic_metrics = None
                if context.acoustic_metrics:
                    acoustic_metrics = EnhancedAcousticMetrics(**context.acoustic_metrics)
                
                linguistic_metrics = None
                if context.linguistic_metrics:
                    linguistic_metrics = LinguisticEnhancementMetrics(**context.linguistic_metrics)
                
                # Extract baseline if available
                baseline = None
                if context.baseline_profile:
                    baseline = BaselineProfile(**context.baseline_profile)
                
                # Get behavioral and consistency data from other services
                behavioral_data = self._extract_behavioral_data(context)
                consistency_data = self._extract_consistency_data(context)
                
                # Calculate coarse credibility score
                credibility_score = self.scoring_service.calculate_credibility_score(
                    acoustic_metrics=acoustic_metrics,
                    linguistic_metrics=linguistic_metrics,
                    behavioral_data=behavioral_data,
                    consistency_data=consistency_data,
                    baseline=baseline
                )
                
                yield {
                    "service_name": self.serviceName,
                    "service_version": self.serviceVersion,
                    "local": {
                        "credibility_score": credibility_score.model_dump(),
                        "note": "Preliminary assessment - may be refined with additional data"
                    },
                    "gemini": {},
                    "errors": [],
                    "partial": True,
                    "phase": "coarse",
                    "chunk_index": 0
                }
                
            except Exception as e:
                logger.error(f"Coarse credibility assessment failed: {e}", exc_info=True)
                errors.append(ErrorResponse(
                    error=f"Credibility assessment failed: {str(e)}",
                    code=500
                ).model_dump())
        
        # Phase 2: Final assessment with all metrics
        if context.transcript_final and (context.acoustic_metrics or context.linguistic_metrics):
            try:
                # Parse metrics
                acoustic_metrics = None
                if context.acoustic_metrics:
                    acoustic_metrics = EnhancedAcousticMetrics(**context.acoustic_metrics)
                
                linguistic_metrics = None
                if context.linguistic_metrics:
                    linguistic_metrics = LinguisticEnhancementMetrics(**context.linguistic_metrics)
                
                baseline = None
                if context.baseline_profile:
                    baseline = BaselineProfile(**context.baseline_profile)
                
                behavioral_data = self._extract_behavioral_data(context)
                consistency_data = self._extract_consistency_data(context)
                
                # Get previous score for EMA smoothing if available
                previous_score = None
                if context.service_results.get("credibility"):
                    prev_result = context.service_results["credibility"]
                    if "local" in prev_result and "credibility_score" in prev_result["local"]:
                        previous_score = prev_result["local"]["credibility_score"].get("credibility_score")
                
                # Calculate final credibility score
                credibility_score = self.scoring_service.calculate_credibility_score(
                    acoustic_metrics=acoustic_metrics,
                    linguistic_metrics=linguistic_metrics,
                    behavioral_data=behavioral_data,
                    consistency_data=consistency_data,
                    baseline=baseline,
                    previous_score=previous_score
                )
                
                # Store in context
                if context:
                    context.service_results["credibility"] = {
                        "local": {"credibility_score": credibility_score.model_dump()}
                    }
                
                yield {
                    "service_name": self.serviceName,
                    "service_version": self.serviceVersion,
                    "local": {
                        "credibility_score": credibility_score.model_dump()
                    },
                    "gemini": {},
                    "errors": errors,
                    "partial": False,
                    "phase": "final",
                    "chunk_index": 1
                }
                
            except Exception as e:
                logger.error(f"Final credibility assessment failed: {e}", exc_info=True)
                errors.append(ErrorResponse(
                    error=f"Credibility assessment failed: {str(e)}",
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
    
    def _extract_behavioral_data(self, context) -> Optional[Dict[str, Any]]:
        """
        Extract behavioral data from context service results.
        """
        behavioral_data = {}
        
        # Extract from quantitative metrics
        if context.quantitative_metrics:
            # Hesitation score
            hesitation_count = context.quantitative_metrics.get("hesitation_marker_count", 0)
            word_count = context.quantitative_metrics.get("word_count", 1)
            behavioral_data["hesitation_score"] = hesitation_count / max(1, word_count)
            
            # Confidence indicators
            certainty_count = context.quantitative_metrics.get("certainty_indicator_count", 0)
            qualifier_count = context.quantitative_metrics.get("qualifier_count", 0)
            total_indicators = certainty_count + qualifier_count
            if total_indicators > 0:
                behavioral_data["confidence_indicators"] = certainty_count / total_indicators
        
        # Extract from manipulation service if available
        if context.service_results.get("manipulation"):
            manip_data = context.service_results["manipulation"]
            if "local" in manip_data:
                behavioral_data["manipulation_score"] = manip_data["local"].get("manipulation_score", 0.5)
        
        return behavioral_data if behavioral_data else None
    
    def _extract_consistency_data(self, context) -> Optional[Dict[str, Any]]:
        """
        Extract consistency data from context service results.
        """
        consistency_data = {}
        
        # Extract from enhanced understanding service if available
        if context.service_results.get("enhanced_understanding"):
            understanding_data = context.service_results["enhanced_understanding"]
            if "local" in understanding_data:
                inconsistencies = understanding_data["local"].get("key_inconsistencies", [])
                # Score based on number of inconsistencies (inverse)
                consistency_data["consistency_score"] = max(0.0, 1.0 - len(inconsistencies) * 0.1)
        
        # Extract from session insights if available
        if context.session_summary:
            # Look for consistency indicators in session summary
            consistency_analysis = context.session_summary.get("consistency_analysis")
            if consistency_analysis:
                # Simple heuristic: longer analysis might indicate more issues
                consistency_data["session_consistency"] = 0.7  # Default moderate
        
        return consistency_data if consistency_data else None
    
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
