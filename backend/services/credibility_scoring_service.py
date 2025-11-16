"""
Credibility Scoring Service V2
Implements advanced statistical scoring with baseline normalization,
weighted metric integration, confidence intervals, and inconclusive detection.
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from scipy import stats
from backend.models import (
    CredibilityScore,
    BaselineProfile,
    EnhancedAcousticMetrics,
    LinguisticEnhancementMetrics
)


class CredibilityScoringServiceV2:
    """
    Advanced credibility scoring with statistical rigor.
    
    Features:
    - Z-score normalization with MAD
    - Weighted metric integration
    - Confidence interval calculation
    - Inconclusive state detection
    - EMA smoothing for real-time updates
    """
    
    # Default weights for different components
    DEFAULT_WEIGHTS = {
        "acoustic": 0.3,
        "linguistic": 0.3,
        "behavioral": 0.2,
        "consistency": 0.2
    }
    
    # Thresholds for inconclusive detection
    INCONCLUSIVE_THRESHOLDS = {
        "confidence_min": 0.5,  # Minimum confidence level
        "ci_width_max": 0.4,    # Maximum confidence interval width
        "outlier_ratio_max": 0.3  # Maximum ratio of outlier metrics
    }
    
    # EMA smoothing parameter
    DEFAULT_EMA_ALPHA = 0.3
    
    def __init__(self, weights: Optional[Dict[str, float]] = None, ema_alpha: float = DEFAULT_EMA_ALPHA):
        """
        Initialize the credibility scoring service.
        
        Args:
            weights: Custom weights for score components
            ema_alpha: EMA smoothing parameter (0-1)
        """
        self.weights = weights or self.DEFAULT_WEIGHTS
        self.ema_alpha = ema_alpha
        self._validate_weights()
        
    def _validate_weights(self):
        """Ensure weights sum to 1.0."""
        total = sum(self.weights.values())
        if not np.isclose(total, 1.0):
            # Normalize weights
            self.weights = {k: v / total for k, v in self.weights.items()}
    
    def calculate_z_score(self, value: float, baseline_mean: float, baseline_std: float) -> float:
        """
        Calculate z-score for a metric value.
        
        Args:
            value: Current metric value
            baseline_mean: Baseline mean
            baseline_std: Baseline standard deviation
            
        Returns:
            Z-score (standardized distance from baseline)
        """
        if baseline_std == 0:
            return 0.0
        return (value - baseline_mean) / baseline_std
    
    def calculate_mad(self, values: List[float]) -> float:
        """
        Calculate Median Absolute Deviation (MAD).
        
        Args:
            values: List of metric values
            
        Returns:
            MAD value (robust measure of variability)
        """
        if not values:
            return 0.0
        median = np.median(values)
        mad = np.median([abs(v - median) for v in values])
        return mad
    
    def calculate_mad_score(self, value: float, values: List[float]) -> float:
        """
        Calculate MAD-based score for outlier detection.
        
        Args:
            value: Current value to check
            values: Historical values for comparison
            
        Returns:
            MAD score (distance from median in MAD units)
        """
        if not values:
            return 0.0
        median = np.median(values)
        mad = self.calculate_mad(values)
        if mad == 0:
            return 0.0
        return abs(value - median) / mad
    
    def detect_outliers(
        self, 
        current_metrics: Dict[str, float], 
        baseline: Optional[BaselineProfile] = None,
        threshold: float = 3.0
    ) -> List[str]:
        """
        Detect outlier metrics using MAD-based approach.
        
        Args:
            current_metrics: Current metric values
            baseline: Baseline profile (if available)
            threshold: MAD threshold for outlier detection (default: 3.0)
            
        Returns:
            List of metric names flagged as outliers
        """
        outliers = []
        
        if not baseline:
            return outliers
        
        # Check key metrics against baseline
        baseline_mapping = {
            "pitch_mean": ("baseline_pitch_mean", "baseline_pitch_std"),
            "intensity_mean": ("baseline_intensity_mean", None),
            "speech_rate_wpm": ("baseline_speech_rate", None),
            "pause_rate": ("baseline_pause_rate", None),
            "hnr_mean": ("baseline_hnr_mean", None)
        }
        
        for metric_name, (baseline_attr, std_attr) in baseline_mapping.items():
            if metric_name in current_metrics:
                baseline_value = getattr(baseline, baseline_attr, 0.0)
                
                # Use z-score if std available, otherwise use simple threshold
                if std_attr and hasattr(baseline, std_attr):
                    baseline_std = getattr(baseline, std_attr, 0.0)
                    if baseline_std > 0:
                        z = abs(self.calculate_z_score(
                            current_metrics[metric_name],
                            baseline_value,
                            baseline_std
                        ))
                        if z > threshold:
                            outliers.append(metric_name)
                else:
                    # Simple deviation check (> 50% change)
                    if baseline_value > 0:
                        deviation = abs(current_metrics[metric_name] - baseline_value) / baseline_value
                        if deviation > 0.5:
                            outliers.append(metric_name)
        
        return outliers
    
    def calculate_confidence_interval(
        self, 
        score: float, 
        sample_size: int,
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for a score.
        
        Args:
            score: Point estimate of score
            sample_size: Number of samples/metrics used
            confidence_level: Confidence level (default: 0.95)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if sample_size < 2:
            # Not enough data, return wide interval
            return (0.0, 1.0)
        
        # Use binomial proportion confidence interval (Wilson score interval)
        z = stats.norm.ppf((1 + confidence_level) / 2)
        n = sample_size
        p = score
        
        # Wilson score interval
        denominator = 1 + z**2 / n
        center = (p + z**2 / (2 * n)) / denominator
        margin = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denominator
        
        lower = max(0.0, center - margin)
        upper = min(1.0, center + margin)
        
        return (lower, upper)
    
    def calculate_component_scores(
        self,
        acoustic_metrics: Optional[EnhancedAcousticMetrics],
        linguistic_metrics: Optional[LinguisticEnhancementMetrics],
        behavioral_data: Optional[Dict[str, Any]],
        consistency_data: Optional[Dict[str, Any]],
        baseline: Optional[BaselineProfile] = None
    ) -> Dict[str, float]:
        """
        Calculate individual component scores.
        
        Args:
            acoustic_metrics: Enhanced acoustic metrics
            linguistic_metrics: Enhanced linguistic metrics
            behavioral_data: Behavioral patterns data
            consistency_data: Consistency analysis data
            baseline: Baseline profile for normalization
            
        Returns:
            Dictionary of component scores (0.0-1.0)
        """
        scores = {
            "acoustic": 0.5,
            "linguistic": 0.5,
            "behavioral": 0.5,
            "consistency": 0.5
        }
        
        # Acoustic score (higher quality = higher credibility)
        if acoustic_metrics:
            acoustic_factors = []
            
            # Voice quality (higher is better)
            acoustic_factors.append(acoustic_metrics.voice_quality_score)
            
            # HNR (higher is better, normalize to 0-1 range)
            if acoustic_metrics.hnr_mean > 0:
                hnr_normalized = min(1.0, acoustic_metrics.hnr_mean / 20.0)
                acoustic_factors.append(hnr_normalized)
            
            # Jitter/Shimmer (lower is better, invert)
            jitter_score = max(0.0, 1.0 - min(1.0, acoustic_metrics.pitch_jitter * 100))
            shimmer_score = max(0.0, 1.0 - min(1.0, acoustic_metrics.pitch_shimmer * 10))
            acoustic_factors.extend([jitter_score, shimmer_score])
            
            # Signal-to-noise ratio (higher is better, normalize)
            if acoustic_metrics.signal_to_noise_ratio > 0:
                snr_normalized = min(1.0, acoustic_metrics.signal_to_noise_ratio / 30.0)
                acoustic_factors.append(snr_normalized)
            
            if acoustic_factors:
                scores["acoustic"] = np.mean(acoustic_factors)
        
        # Linguistic score (complexity and coherence)
        if linguistic_metrics:
            linguistic_factors = []
            
            # Sentence complexity (moderate is better)
            complexity = linguistic_metrics.sentence_complexity_score
            complexity_score = 1.0 - abs(complexity - 0.5) * 2  # Peak at 0.5
            linguistic_factors.append(complexity_score)
            
            # Emotional leakage (less is more credible)
            if linguistic_metrics.emotional_leakage_ratio is not None:
                leakage_score = max(0.0, 1.0 - linguistic_metrics.emotional_leakage_ratio * 5)
                linguistic_factors.append(leakage_score)
            
            # Prosodic congruence (higher is better)
            if linguistic_metrics.prosodic_congruence_score is not None:
                linguistic_factors.append(linguistic_metrics.prosodic_congruence_score)
            
            if linguistic_factors:
                scores["linguistic"] = np.mean(linguistic_factors)
        
        # Behavioral score (from patterns)
        if behavioral_data:
            behavioral_factors = []
            
            if "hesitation_score" in behavioral_data:
                # Lower hesitation is better
                hesitation_score = max(0.0, 1.0 - behavioral_data["hesitation_score"])
                behavioral_factors.append(hesitation_score)
            
            if "confidence_indicators" in behavioral_data:
                behavioral_factors.append(behavioral_data["confidence_indicators"])
            
            if behavioral_factors:
                scores["behavioral"] = np.mean(behavioral_factors)
        
        # Consistency score
        if consistency_data:
            if "consistency_score" in consistency_data:
                scores["consistency"] = consistency_data["consistency_score"]
        
        return scores
    
    def calculate_credibility_score(
        self,
        acoustic_metrics: Optional[EnhancedAcousticMetrics] = None,
        linguistic_metrics: Optional[LinguisticEnhancementMetrics] = None,
        behavioral_data: Optional[Dict[str, Any]] = None,
        consistency_data: Optional[Dict[str, Any]] = None,
        baseline: Optional[BaselineProfile] = None,
        previous_score: Optional[float] = None
    ) -> CredibilityScore:
        """
        Calculate comprehensive credibility score.
        
        Args:
            acoustic_metrics: Enhanced acoustic metrics
            linguistic_metrics: Enhanced linguistic metrics
            behavioral_data: Behavioral patterns
            consistency_data: Consistency analysis
            baseline: Baseline profile
            previous_score: Previous score for EMA smoothing
            
        Returns:
            CredibilityScore with detailed assessment
        """
        # Calculate component scores
        component_scores = self.calculate_component_scores(
            acoustic_metrics,
            linguistic_metrics,
            behavioral_data,
            consistency_data,
            baseline
        )
        
        # Weighted integration
        overall_score = sum(
            component_scores[component] * self.weights[component]
            for component in self.weights.keys()
        )
        
        # Collect metrics for outlier detection
        current_metrics = {}
        if acoustic_metrics:
            current_metrics["pitch_mean"] = acoustic_metrics.pitch_mean
            current_metrics["intensity_mean"] = acoustic_metrics.intensity_mean
            current_metrics["speech_rate_wpm"] = acoustic_metrics.speech_rate_wpm
            current_metrics["pause_rate"] = acoustic_metrics.pause_rate
            current_metrics["hnr_mean"] = acoustic_metrics.hnr_mean
        
        # Detect outliers
        outliers = self.detect_outliers(current_metrics, baseline)
        
        # Calculate z-score and MAD if baseline available
        z_score = 0.0
        mad_score = 0.0
        if baseline and "pitch_mean" in current_metrics:
            z_score = self.calculate_z_score(
                current_metrics["pitch_mean"],
                baseline.baseline_pitch_mean,
                baseline.baseline_pitch_std
            )
        
        # Estimate sample size for confidence interval
        sample_size = sum([
            1 if acoustic_metrics else 0,
            1 if linguistic_metrics else 0,
            1 if behavioral_data else 0,
            1 if consistency_data else 0
        ]) * 5  # Approximate number of sub-metrics
        
        # Calculate confidence interval
        ci_lower, ci_upper = self.calculate_confidence_interval(overall_score, sample_size)
        ci_width = ci_upper - ci_lower
        
        # Determine confidence level
        confidence = 1.0 - ci_width
        
        # Detect inconclusive state
        is_inconclusive = False
        inconclusive_reasons = []
        
        if confidence < self.INCONCLUSIVE_THRESHOLDS["confidence_min"]:
            is_inconclusive = True
            inconclusive_reasons.append(f"Low confidence level: {confidence:.2f}")
        
        if ci_width > self.INCONCLUSIVE_THRESHOLDS["ci_width_max"]:
            is_inconclusive = True
            inconclusive_reasons.append(f"Wide confidence interval: {ci_width:.2f}")
        
        if outliers and len(outliers) / max(1, len(current_metrics)) > self.INCONCLUSIVE_THRESHOLDS["outlier_ratio_max"]:
            is_inconclusive = True
            inconclusive_reasons.append(f"High outlier ratio: {len(outliers)}/{len(current_metrics)}")
        
        # Determine credibility level
        if is_inconclusive:
            credibility_level = "Inconclusive"
        elif overall_score >= 0.75:
            credibility_level = "High"
        elif overall_score >= 0.5:
            credibility_level = "Medium"
        else:
            credibility_level = "Low"
        
        # EMA smoothing
        ema_smoothed_score = None
        if previous_score is not None:
            ema_smoothed_score = (self.ema_alpha * overall_score + 
                                 (1 - self.ema_alpha) * previous_score)
        
        # Build explanation
        explanation_parts = [
            f"Credibility score: {overall_score:.2f} ({credibility_level})",
            f"Confidence interval: [{ci_lower:.2f}, {ci_upper:.2f}]",
            f"Component scores: Acoustic={component_scores['acoustic']:.2f}, "
            f"Linguistic={component_scores['linguistic']:.2f}, "
            f"Behavioral={component_scores['behavioral']:.2f}, "
            f"Consistency={component_scores['consistency']:.2f}"
        ]
        
        if baseline:
            explanation_parts.append(f"Normalized against baseline (z-score: {z_score:.2f})")
        
        if outliers:
            explanation_parts.append(f"Outlier metrics detected: {', '.join(outliers)}")
        
        explanation = ". ".join(explanation_parts)
        
        # Build contributing factors
        contributing_factors = [
            {"component": "acoustic", "score": component_scores["acoustic"], "weight": self.weights["acoustic"]},
            {"component": "linguistic", "score": component_scores["linguistic"], "weight": self.weights["linguistic"]},
            {"component": "behavioral", "score": component_scores["behavioral"], "weight": self.weights["behavioral"]},
            {"component": "consistency", "score": component_scores["consistency"], "weight": self.weights["consistency"]}
        ]
        
        # Identify risk indicators
        risk_indicators = []
        if component_scores["acoustic"] < 0.4:
            risk_indicators.append("Low acoustic quality")
        if component_scores["linguistic"] < 0.4:
            risk_indicators.append("Linguistic inconsistencies")
        if component_scores["behavioral"] < 0.4:
            risk_indicators.append("Suspicious behavioral patterns")
        if component_scores["consistency"] < 0.4:
            risk_indicators.append("Internal inconsistencies detected")
        if outliers:
            risk_indicators.append(f"Anomalous metrics: {', '.join(outliers)}")
        
        return CredibilityScore(
            credibility_score=overall_score,
            credibility_level=credibility_level,
            confidence_interval_lower=ci_lower,
            confidence_interval_upper=ci_upper,
            confidence_level=confidence,
            acoustic_score=component_scores["acoustic"],
            linguistic_score=component_scores["linguistic"],
            behavioral_score=component_scores["behavioral"],
            consistency_score=component_scores["consistency"],
            z_score=z_score,
            mad_score=mad_score,
            outlier_flags=outliers,
            is_inconclusive=is_inconclusive,
            inconclusive_reasons=inconclusive_reasons,
            explanation=explanation,
            contributing_factors=contributing_factors,
            risk_indicators=risk_indicators,
            ema_smoothed_score=ema_smoothed_score,
            ema_alpha=self.ema_alpha if ema_smoothed_score is not None else None
        )
