"""SessionInsightsService v2

Migrated from backend.services.session_insights_service to follow the v2 streaming protocol.
Provides intelligent session analysis based on conversation history and patterns.
"""
import logging
import statistics
from typing import Optional, Dict, Any, AsyncGenerator, List

from backend.services.v2_services.analysis_protocol import AnalysisService

logger = logging.getLogger(__name__)


class SessionInsightsServiceV2(AnalysisService):
    """V2 service for session-level insights with streaming support."""
    
    serviceName = "session_insights"
    serviceVersion = "2.0"
    
    def __init__(self, transcript: str = "", meta: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(transcript=transcript, meta=meta)
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate simple linear trend from list of values."""
        if len(values) < 2:
            return 0.0
        # Simple trend: difference between avg of last half vs first half
        mid = len(values) // 2
        first_half_avg = statistics.mean(values[:mid]) if values[:mid] else 0
        second_half_avg = statistics.mean(values[mid:]) if values[mid:] else 0
        return second_half_avg - first_half_avg
    
    def _analyze_consistency(
        self,
        session_history: List[Dict[str, Any]],
        current_results: Dict[str, Any]
    ) -> str:
        """Analyze consistency patterns across the session."""
        if len(session_history) < 1:
            return "Initial analysis - consistency patterns will develop with more conversation."
        
        # Extract credibility scores if available
        scores = []
        for entry in session_history:
            score = entry.get("credibility_score") or entry.get("analysis", {}).get("credibility_score")
            if score is not None:
                scores.append(float(score))
        
        if len(scores) < 2:
            return "Insufficient data for consistency analysis."
        
        variance = statistics.variance(scores)
        avg_score = statistics.mean(scores)
        
        if variance < 100:
            return f"HIGH consistency with stable patterns (avg: {avg_score:.1f})"
        elif variance < 400:
            return f"MODERATE consistency with some variation (variance: {variance:.1f})"
        else:
            return f"LOW consistency with significant variation (variance: {variance:.1f})"
    
    def _analyze_behavioral_evolution(
        self,
        session_history: List[Dict[str, Any]],
        current_results: Dict[str, Any]
    ) -> str:
        """Analyze how behavior has evolved over the session."""
        if len(session_history) < 2:
            return "Not enough data to analyze behavioral evolution."
        
        # Check for changes in speech patterns
        hesitation_counts = []
        for entry in session_history:
            hesitation = entry.get("hesitation_count") or entry.get("analysis", {}).get("hesitation_count", 0)
            hesitation_counts.append(hesitation)
        
        if len(hesitation_counts) >= 2:
            trend = self._calculate_trend(hesitation_counts)
            if trend > 2:
                return "Increasing hesitation over time - possible growing discomfort"
            elif trend < -2:
                return "Decreasing hesitation - speaker becoming more comfortable"
            else:
                return "Stable behavioral patterns throughout session"
        
        return "Behavioral patterns stable"
    
    def _analyze_risk_trajectory(
        self,
        session_history: List[Dict[str, Any]],
        current_results: Dict[str, Any]
    ) -> str:
        """Analyze risk level trajectory over the session."""
        if len(session_history) < 2:
            return "Insufficient data for risk trajectory analysis."
        
        risk_scores = []
        for entry in session_history:
            overall_risk = entry.get("overall_risk") or entry.get("analysis", {}).get("overall_risk")
            if overall_risk:
                # Convert risk levels to scores
                risk_map = {"low": 25, "medium": 50, "high": 75}
                risk_scores.append(risk_map.get(str(overall_risk).lower(), 50))
        
        if len(risk_scores) >= 2:
            trend = self._calculate_trend(risk_scores)
            if trend > 10:
                return "Risk levels increasing - growing concerns"
            elif trend < -10:
                return "Risk levels decreasing - improving credibility"
            else:
                return "Risk levels stable throughout session"
        
        return "Risk trajectory stable"
    
    def _perform_analysis(
        self,
        session_history: List[Dict[str, Any]],
        current_results: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate session insights."""
        if not session_history:
            return {
                "status": "No session history available",
                "consistency_analysis": "Initial analysis",
                "behavioral_evolution": "Initial analysis",
                "risk_trajectory": "Initial analysis"
            }
        
        return {
            "consistency_analysis": self._analyze_consistency(session_history, current_results),
            "behavioral_evolution": self._analyze_behavioral_evolution(session_history, current_results),
            "risk_trajectory": self._analyze_risk_trajectory(session_history, current_results),
            "total_analyses": len(session_history)
        }
    
    async def stream_analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream session insights with pseudo-streaming (coarse → final)."""
        meta = meta or {}
        ctx = meta.get("analysis_context")
        
        # Get session history from meta
        session_summary = meta.get("session_summary") or (ctx.session_summary if ctx else None)
        session_history = []
        if session_summary and isinstance(session_summary, dict):
            session_history = session_summary.get("history", [])
        
        # Get current results from context
        current_results = {}
        if ctx and ctx.service_results:
            current_results = ctx.service_results
        
        # Phase 1: Coarse - quick placeholder
        yield {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {
                "status": "analyzing_session",
                "history_size": len(session_history)
            },
            "gemini": None,
            "errors": [],
            "partial": True,
            "phase": "coarse",
            "chunk_index": 0,
        }
        
        # Phase 2: Perform analysis
        insights = self._perform_analysis(session_history, current_results)
        
        # Update context
        if ctx:
            ctx.service_results["session_insights"] = insights
        
        # Phase 3: Final result
        yield {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": insights,
            "gemini": None,
            "errors": [],
            "partial": False,
            "phase": "final",
            "chunk_index": 1,
        }
