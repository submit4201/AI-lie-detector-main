"""CredibilityScoringService v2

Integrated credibility analysis using baseline-normalized multivariate scoring.

Implements the statistical framework described in the forensic psychophysiology research:
1. Baseline normalization using z-scores
2. Direction-aware weighting of metrics  
3. Confidence interval calculation
4. Inconclusive state detection for poor quality signals

This service does NOT claim to detect deception directly. It quantifies deviations
from baseline that correlate with cognitive load, stress, and speech production
instability - states associated with but not exclusive to deceptive behavior.
"""
import logging
import numpy as np
from typing import Optional, Dict, Any, AsyncGenerator, List
from scipy import stats

from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.models import (
    CredibilityScore,
    MetricContribution,
    BaselineProfile,
    MetricBaseline
)

logger = logging.getLogger(__name__)


class CredibilityScoringService(AnalysisService):
    """V2 service for credibility scoring with baseline normalization."""
    
    serviceName = "credibility_scoring"
    serviceVersion = "2.0"
    
    # Metric weights based on literature effect sizes (r ≈ 0.25-0.45)
    # Higher weight = stronger correlation with deception/stress
    METRIC_WEIGHTS = {
        # Acoustic metrics (high weights)
        "pitch_jitter": 0.85,
        "pitch_shimmer": 0.85,
        "vocal_tremor": 0.80,
        "pause_rate": 0.75,
        "formant_dispersion": 0.70,
        "hnr_mean": 0.65,
        
        # Prosodic metrics (medium weights)
        "pitch_std": 0.60,
        "intensity_std": 0.55,
        "speech_rate": 0.60,
        
        # Linguistic metrics (medium weights)
        "hesitation_rate": 0.70,
        "pronoun_ratio": 0.55,
        "qualifier_ratio": 0.60,
        "response_latency": 0.65,
        
        # Derived metrics (high weights)
        "prosodic_congruence": 0.80,
    }
    
    # Metric directions: 1 = increase is suspicious, -1 = decrease is suspicious
    METRIC_DIRECTIONS = {
        "pitch_jitter": 1,
        "pitch_shimmer": 1,
        "vocal_tremor": 1,
        "pause_rate": 1,
        "formant_dispersion": 1,
        "hnr_mean": -1,  # Lower HNR = more suspicious
        "pitch_std": 0,  # Context-dependent
        "intensity_std": 1,
        "speech_rate": -1,  # Slower = more suspicious (cognitive load)
        "hesitation_rate": 1,
        "pronoun_ratio": -1,  # Less self-reference = more suspicious
        "qualifier_ratio": 1,
        "response_latency": 1,
        "prosodic_congruence": 1,  # Mismatch = suspicious
    }
    
    def __init__(self, baseline_profile: Optional[BaselineProfile] = None, **kwargs):
        super().__init__(**kwargs)
        self.baseline_profile = baseline_profile
    
    def _calculate_z_score(
        self,
        value: float,
        baseline: Optional[MetricBaseline]
    ) -> Optional[float]:
        """Calculate z-score with MAD-based outlier robustness."""
        if baseline is None or baseline.std == 0:
            return None
        
        z = (value - baseline.mean) / baseline.std
        
        # Clip extreme outliers using MAD if available
        if baseline.mad is not None and baseline.mad > 0:
            mad_z = 0.6745 * (value - baseline.mean) / baseline.mad
            # Use MAD-based z if more conservative
            if abs(mad_z) < abs(z):
                return mad_z
        
        return z
    
    def _extract_metrics_from_context(
        self,
        ctx
    ) -> Dict[str, float]:
        """Extract all available metrics from AnalysisContext."""
        metrics = {}
        
        # Enhanced acoustic metrics
        if hasattr(ctx, 'enhanced_acoustic_metrics'):
            acoustic = ctx.enhanced_acoustic_metrics
            if isinstance(acoustic, dict):
                if acoustic.get('pitch_jitter') is not None:
                    metrics['pitch_jitter'] = acoustic['pitch_jitter']
                if acoustic.get('pitch_shimmer') is not None:
                    metrics['pitch_shimmer'] = acoustic['pitch_shimmer']
                if acoustic.get('pitch_std') is not None:
                    metrics['pitch_std'] = acoustic['pitch_std']
                if acoustic.get('formant_dispersion') is not None:
                    metrics['formant_dispersion'] = acoustic['formant_dispersion']
                if acoustic.get('hnr_mean') is not None:
                    metrics['hnr_mean'] = acoustic['hnr_mean']
                if acoustic.get('intensity_std') is not None:
                    metrics['intensity_std'] = acoustic['intensity_std']
                if acoustic.get('pause_rate') is not None:
                    metrics['pause_rate'] = acoustic['pause_rate']
        
        # Quantitative metrics
        if hasattr(ctx, 'quantitative_metrics'):
            quant = ctx.quantitative_metrics
            if isinstance(quant, dict):
                numerical = quant.get('numerical_linguistic_metrics', {})
                if isinstance(numerical, dict):
                    # Speech rate
                    if numerical.get('speech_rate_wpm'):
                        metrics['speech_rate'] = numerical['speech_rate_wpm']
                    
                    # Hesitation rate
                    if numerical.get('hesitation_rate_hpm'):
                        metrics['hesitation_rate'] = numerical['hesitation_rate_hpm']
                    
                    # Qualifier ratio
                    word_count = numerical.get('word_count', 0)
                    if word_count > 0:
                        qualifier_count = numerical.get('qualifier_count', 0)
                        metrics['qualifier_ratio'] = qualifier_count / word_count
        
        return metrics
    
    def _calculate_credibility_score(
        self,
        metrics: Dict[str, float],
        baseline: Optional[BaselineProfile]
    ) -> CredibilityScore:
        """Calculate credibility score using baseline-normalized z-scores."""
        
        # Track contributions
        contributions: List[MetricContribution] = []
        primary_indicators: List[str] = []
        quality_warnings: List[str] = []
        
        # Calculate weighted sum
        weighted_sum = 0.0
        total_weight = 0.0
        z_scores: List[float] = []
        
        for metric_name, value in metrics.items():
            # Get baseline for this metric
            metric_baseline = None
            if baseline and hasattr(baseline, metric_name):
                metric_baseline = getattr(baseline, metric_name)
            
            # Calculate z-score
            z_score = self._calculate_z_score(value, metric_baseline)
            
            if z_score is None:
                continue
            
            # Get weight and direction
            weight = self.METRIC_WEIGHTS.get(metric_name, 0.5)
            direction = self.METRIC_DIRECTIONS.get(metric_name, 1)
            
            # Calculate contribution (positive = suspicious)
            contribution = direction * z_score * weight
            weighted_sum += contribution
            total_weight += weight
            z_scores.append(z_score)
            
            # Record contribution
            contributions.append(MetricContribution(
                metric_name=metric_name,
                z_score=z_score,
                direction=direction,
                weight=weight,
                contribution=contribution
            ))
            
            # Flag significant deviations (|z| > 1.5)
            if abs(z_score) > 1.5:
                if direction * z_score > 0:
                    primary_indicators.append(
                        f"{metric_name}: {'+' if z_score > 0 else ''}{z_score:.2f}σ (suspicious)"
                    )
        
        # Normalize score to 0-100 scale
        # weighted_sum ranges roughly -5 to +5, map to 100-0 (higher sum = lower credibility)
        if total_weight > 0:
            normalized_sum = weighted_sum / total_weight
            # Map: -2 = 100 (very credible), 0 = 50, +2 = 0 (not credible)
            raw_score = 50 - (normalized_sum * 25)
            credibility_score = max(0, min(100, raw_score))
        else:
            credibility_score = 50  # Neutral if no metrics
            quality_warnings.append("Insufficient metrics for credibility assessment")
        
        # Calculate confidence interval using standard error
        if len(z_scores) >= 3:
            sem = stats.sem(z_scores)
            ci_margin = sem * 1.96 * 25  # Convert to score scale
            ci_low = max(0, credibility_score - ci_margin)
            ci_high = min(100, credibility_score + ci_margin)
        else:
            # Wide CI for few metrics
            ci_low = max(0, credibility_score - 30)
            ci_high = min(100, credibility_score + 30)
            quality_warnings.append("Wide confidence interval due to limited metrics")
        
        # Determine category
        if ci_high - ci_low > 50:
            category = "inconclusive"
            inconclusive_reason = "Confidence interval too wide - insufficient data"
        elif credibility_score >= 70:
            category = "high_credibility"
            inconclusive_reason = None
        elif credibility_score >= 40:
            category = "moderate"
            inconclusive_reason = None
        elif credibility_score >= 20:
            category = "low_credibility"
            inconclusive_reason = None
        else:
            category = "very_low_credibility"
            inconclusive_reason = None
        
        # Confidence level
        ci_width = ci_high - ci_low
        if ci_width < 20:
            confidence = "high"
        elif ci_width < 40:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Baseline quality
        baseline_quality = "none"
        if baseline:
            baseline_quality = baseline.calibration_quality
        
        # Calculate composite scores
        # Physiological load: acoustic metrics
        acoustic_z = [c.z_score for c in contributions if c.z_score and ('pitch' in c.metric_name or 'hnr' in c.metric_name or 'formant' in c.metric_name)]
        if acoustic_z:
            physiological_load = min(100, max(0, 50 + np.mean(acoustic_z) * 20))
        else:
            physiological_load = None
        
        # Cognitive load: linguistic + temporal metrics
        cognitive_z = [c.z_score for c in contributions if c.z_score and ('hesitation' in c.metric_name or 'pause' in c.metric_name or 'speech_rate' in c.metric_name)]
        if cognitive_z:
            cognitive_load = min(100, max(0, 50 + np.mean(cognitive_z) * 20))
        else:
            cognitive_load = None
        
        return CredibilityScore(
            credibility_score=round(credibility_score, 1),
            confidence_interval_low=round(ci_low, 1),
            confidence_interval_high=round(ci_high, 1),
            credibility_category=category,
            confidence_level=confidence,
            primary_indicators=primary_indicators[:5],  # Top 5
            metric_breakdown=sorted(contributions, key=lambda x: abs(x.contribution), reverse=True),
            baseline_quality=baseline_quality,
            quality_warnings=quality_warnings,
            inconclusive_reason=inconclusive_reason,
            physiological_load_score=round(physiological_load, 1) if physiological_load else None,
            cognitive_load_indicator=round(cognitive_load, 1) if cognitive_load else None
        )
    
    async def stream_analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream credibility scoring with pseudo-streaming (coarse → final)."""
        meta = meta or {}
        ctx = meta.get("analysis_context")
        
        if not ctx:
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": {},
                "gemini": None,
                "errors": [{"error": "No analysis context available for credibility scoring"}],
                "partial": False,
                "phase": "final",
                "chunk_index": None,
            }
            return
        
        # Phase 1: Coarse - placeholder
        yield {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {"status": "calculating_credibility"},
            "gemini": None,
            "errors": [],
            "partial": True,
            "phase": "coarse",
            "chunk_index": 0,
        }
        
        # Phase 2: Extract metrics and calculate score
        metrics = self._extract_metrics_from_context(ctx)
        
        # Get baseline from meta if available
        baseline = meta.get("baseline_profile") or self.baseline_profile
        
        if not metrics:
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": {},
                "gemini": None,
                "errors": [{"error": "No metrics available for credibility analysis"}],
                "partial": False,
                "phase": "final",
                "chunk_index": 1,
            }
            return
        
        # Calculate credibility score
        credibility_result = self._calculate_credibility_score(metrics, baseline)
        
        # Convert to dict
        if hasattr(credibility_result, 'model_dump'):
            result_dict = credibility_result.model_dump()
        else:
            result_dict = credibility_result.__dict__
        
        # Update context
        if ctx:
            ctx.service_results["credibility_scoring"] = result_dict
        
        # Phase 3: Final result
        yield {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": result_dict,
            "gemini": None,
            "errors": [],
            "partial": False,
            "phase": "final",
            "chunk_index": 1,
        }
