"""
Unit tests for CredibilityScoringServiceV2
"""

import pytest
import numpy as np
from backend.services.credibility_scoring_service import CredibilityScoringServiceV2
from backend.models import (
    EnhancedAcousticMetrics,
    LinguisticEnhancementMetrics,
    BaselineProfile,
    CredibilityScore
)


@pytest.fixture
def scoring_service():
    """Create a scoring service instance."""
    return CredibilityScoringServiceV2()


@pytest.fixture
def sample_acoustic_metrics():
    """Create sample acoustic metrics."""
    return EnhancedAcousticMetrics(
        pitch_jitter=0.01,
        pitch_shimmer=0.05,
        pitch_mean=150.0,
        pitch_std=20.0,
        hnr_mean=15.0,
        voice_quality_score=0.8,
        signal_to_noise_ratio=25.0,
        speech_rate_wpm=120.0,
        pause_rate=5.0,
        intensity_mean=60.0
    )


@pytest.fixture
def sample_linguistic_metrics():
    """Create sample linguistic metrics."""
    return LinguisticEnhancementMetrics(
        pronoun_ratio_first_person=0.05,
        sentence_complexity_score=0.6,
        emotional_leakage_ratio=0.02,
        prosodic_congruence_score=0.75
    )


@pytest.fixture
def sample_baseline():
    """Create sample baseline profile."""
    return BaselineProfile(
        baseline_pitch_mean=145.0,
        baseline_pitch_std=18.0,
        baseline_intensity_mean=58.0,
        baseline_speech_rate=115.0,
        baseline_pause_rate=4.5,
        baseline_hnr_mean=14.0,
        calibration_samples=10,
        confidence_level=0.85
    )


class TestCredibilityScoringService:
    """Test suite for CredibilityScoringServiceV2."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = CredibilityScoringServiceV2()
        assert service.weights is not None
        assert sum(service.weights.values()) == pytest.approx(1.0)
        assert service.ema_alpha == CredibilityScoringServiceV2.DEFAULT_EMA_ALPHA
    
    def test_custom_weights(self):
        """Test initialization with custom weights."""
        custom_weights = {
            "acoustic": 0.4,
            "linguistic": 0.3,
            "behavioral": 0.2,
            "consistency": 0.1
        }
        service = CredibilityScoringServiceV2(weights=custom_weights)
        assert service.weights == custom_weights
    
    def test_weight_normalization(self):
        """Test that weights are normalized to sum to 1.0."""
        unnormalized_weights = {
            "acoustic": 0.5,
            "linguistic": 0.5,
            "behavioral": 0.5,
            "consistency": 0.5
        }
        service = CredibilityScoringServiceV2(weights=unnormalized_weights)
        assert sum(service.weights.values()) == pytest.approx(1.0)
        assert service.weights["acoustic"] == pytest.approx(0.25)
    
    def test_z_score_calculation(self, scoring_service):
        """Test z-score calculation."""
        z = scoring_service.calculate_z_score(150.0, 145.0, 10.0)
        assert z == pytest.approx(0.5)
        
        z = scoring_service.calculate_z_score(140.0, 145.0, 10.0)
        assert z == pytest.approx(-0.5)
        
        # Test with zero std
        z = scoring_service.calculate_z_score(150.0, 145.0, 0.0)
        assert z == 0.0
    
    def test_mad_calculation(self, scoring_service):
        """Test MAD calculation."""
        values = [1, 2, 3, 4, 5]
        mad = scoring_service.calculate_mad(values)
        assert mad == 1.0  # Median is 3, deviations are [2,1,0,1,2], median deviation is 1
        
        # Test with empty list
        mad = scoring_service.calculate_mad([])
        assert mad == 0.0
    
    def test_mad_score_calculation(self, scoring_service):
        """Test MAD-based score calculation."""
        values = [10, 12, 14, 16, 18]
        mad_score = scoring_service.calculate_mad_score(24, values)
        assert mad_score > 0  # Should detect as outlier
        
        mad_score = scoring_service.calculate_mad_score(14, values)
        assert mad_score == 0.0  # Exactly at median
    
    def test_outlier_detection_without_baseline(self, scoring_service):
        """Test outlier detection without baseline."""
        metrics = {"pitch_mean": 150.0, "intensity_mean": 60.0}
        outliers = scoring_service.detect_outliers(metrics, None)
        assert outliers == []
    
    def test_outlier_detection_with_baseline(self, scoring_service, sample_baseline):
        """Test outlier detection with baseline."""
        # Normal metrics
        normal_metrics = {
            "pitch_mean": 148.0,
            "intensity_mean": 59.0,
            "speech_rate_wpm": 118.0
        }
        outliers = scoring_service.detect_outliers(normal_metrics, sample_baseline)
        assert len(outliers) == 0
        
        # Outlier metrics
        outlier_metrics = {
            "pitch_mean": 200.0,  # Very different from baseline
            "intensity_mean": 59.0,
            "speech_rate_wpm": 118.0
        }
        outliers = scoring_service.detect_outliers(outlier_metrics, sample_baseline)
        assert "pitch_mean" in outliers
    
    def test_confidence_interval_calculation(self, scoring_service):
        """Test confidence interval calculation."""
        ci_lower, ci_upper = scoring_service.calculate_confidence_interval(0.75, 10)
        assert 0.0 <= ci_lower < ci_upper <= 1.0
        assert ci_lower < 0.75 < ci_upper
        
        # Test with small sample size
        ci_lower, ci_upper = scoring_service.calculate_confidence_interval(0.75, 1)
        assert ci_lower == 0.0
        assert ci_upper == 1.0
    
    def test_component_scores_acoustic(self, scoring_service, sample_acoustic_metrics):
        """Test acoustic component score calculation."""
        scores = scoring_service.calculate_component_scores(
            acoustic_metrics=sample_acoustic_metrics,
            linguistic_metrics=None,
            behavioral_data=None,
            consistency_data=None
        )
        assert 0.0 <= scores["acoustic"] <= 1.0
        assert scores["acoustic"] > 0.5  # Good metrics should score high
    
    def test_component_scores_linguistic(self, scoring_service, sample_linguistic_metrics):
        """Test linguistic component score calculation."""
        scores = scoring_service.calculate_component_scores(
            acoustic_metrics=None,
            linguistic_metrics=sample_linguistic_metrics,
            behavioral_data=None,
            consistency_data=None
        )
        assert 0.0 <= scores["linguistic"] <= 1.0
    
    def test_component_scores_with_behavioral(self, scoring_service):
        """Test behavioral component score calculation."""
        behavioral_data = {
            "hesitation_score": 0.2,
            "confidence_indicators": 0.8
        }
        scores = scoring_service.calculate_component_scores(
            acoustic_metrics=None,
            linguistic_metrics=None,
            behavioral_data=behavioral_data,
            consistency_data=None
        )
        assert 0.0 <= scores["behavioral"] <= 1.0
        assert scores["behavioral"] > 0.5  # Good behavioral data should score high
    
    def test_full_credibility_score_calculation(
        self, scoring_service, sample_acoustic_metrics, sample_linguistic_metrics
    ):
        """Test full credibility score calculation."""
        score = scoring_service.calculate_credibility_score(
            acoustic_metrics=sample_acoustic_metrics,
            linguistic_metrics=sample_linguistic_metrics
        )
        
        assert isinstance(score, CredibilityScore)
        assert 0.0 <= score.credibility_score <= 1.0
        assert score.credibility_level in ["Low", "Medium", "High", "Inconclusive"]
        assert 0.0 <= score.confidence_interval_lower <= score.credibility_score
        assert score.credibility_score <= score.confidence_interval_upper <= 1.0
        assert 0.0 <= score.confidence_level <= 1.0
    
    def test_credibility_score_with_baseline(
        self, scoring_service, sample_acoustic_metrics, sample_baseline
    ):
        """Test credibility score calculation with baseline."""
        score = scoring_service.calculate_credibility_score(
            acoustic_metrics=sample_acoustic_metrics,
            baseline=sample_baseline
        )
        
        assert isinstance(score, CredibilityScore)
        assert score.z_score != 0.0  # Should calculate z-score with baseline
    
    def test_ema_smoothing(self, scoring_service, sample_acoustic_metrics):
        """Test EMA smoothing."""
        # First score
        score1 = scoring_service.calculate_credibility_score(
            acoustic_metrics=sample_acoustic_metrics
        )
        
        # Second score with previous score for EMA
        score2 = scoring_service.calculate_credibility_score(
            acoustic_metrics=sample_acoustic_metrics,
            previous_score=score1.credibility_score
        )
        
        assert score2.ema_smoothed_score is not None
        assert score2.ema_alpha == scoring_service.ema_alpha
    
    def test_inconclusive_detection_low_confidence(self, scoring_service):
        """Test inconclusive detection with low confidence."""
        # Create metrics that will result in low confidence (small sample size)
        service = CredibilityScoringServiceV2()
        
        # Mock to create wide confidence interval
        score = service.calculate_credibility_score(
            acoustic_metrics=None,  # Minimal data
            linguistic_metrics=None
        )
        
        # With minimal data, should have low confidence or be inconclusive
        assert score.confidence_level < 1.0
    
    def test_inconclusive_detection_outliers(
        self, scoring_service, sample_acoustic_metrics, sample_baseline
    ):
        """Test inconclusive detection with many outliers."""
        # Create metrics with extreme values
        extreme_metrics = EnhancedAcousticMetrics(
            pitch_mean=300.0,  # Very high
            intensity_mean=100.0,  # Very high
            speech_rate_wpm=300.0,  # Very fast
            pause_rate=20.0,  # Many pauses
            hnr_mean=5.0  # Low HNR
        )
        
        score = scoring_service.calculate_credibility_score(
            acoustic_metrics=extreme_metrics,
            baseline=sample_baseline
        )
        
        # Should detect outliers
        assert len(score.outlier_flags) > 0
    
    def test_credibility_levels(self, scoring_service):
        """Test credibility level assignment."""
        # High quality metrics
        high_quality = EnhancedAcousticMetrics(
            voice_quality_score=0.9,
            hnr_mean=20.0,
            pitch_jitter=0.001,
            pitch_shimmer=0.01,
            signal_to_noise_ratio=30.0
        )
        score_high = scoring_service.calculate_credibility_score(acoustic_metrics=high_quality)
        assert score_high.credibility_score > 0.5
        
        # Low quality metrics
        low_quality = EnhancedAcousticMetrics(
            voice_quality_score=0.2,
            hnr_mean=5.0,
            pitch_jitter=0.1,
            pitch_shimmer=0.5,
            signal_to_noise_ratio=5.0
        )
        score_low = scoring_service.calculate_credibility_score(acoustic_metrics=low_quality)
        assert score_low.credibility_score < score_high.credibility_score
    
    def test_risk_indicators(
        self, scoring_service, sample_acoustic_metrics, sample_linguistic_metrics
    ):
        """Test risk indicator generation."""
        # Create metrics with some risk factors
        risky_metrics = EnhancedAcousticMetrics(
            voice_quality_score=0.3,  # Low quality
            hnr_mean=5.0,
            pitch_jitter=0.05,
            pitch_shimmer=0.2
        )
        
        score = scoring_service.calculate_credibility_score(
            acoustic_metrics=risky_metrics,
            linguistic_metrics=sample_linguistic_metrics
        )
        
        assert len(score.risk_indicators) > 0
        assert "Low acoustic quality" in score.risk_indicators
    
    def test_explanation_generation(
        self, scoring_service, sample_acoustic_metrics, sample_linguistic_metrics
    ):
        """Test explanation text generation."""
        score = scoring_service.calculate_credibility_score(
            acoustic_metrics=sample_acoustic_metrics,
            linguistic_metrics=sample_linguistic_metrics
        )
        
        assert len(score.explanation) > 0
        assert "Credibility score" in score.explanation
        assert "Confidence interval" in score.explanation
    
    def test_contributing_factors(
        self, scoring_service, sample_acoustic_metrics, sample_linguistic_metrics
    ):
        """Test contributing factors structure."""
        score = scoring_service.calculate_credibility_score(
            acoustic_metrics=sample_acoustic_metrics,
            linguistic_metrics=sample_linguistic_metrics
        )
        
        assert len(score.contributing_factors) == 4
        for factor in score.contributing_factors:
            assert "component" in factor
            assert "score" in factor
            assert "weight" in factor
            assert 0.0 <= factor["score"] <= 1.0
            assert 0.0 <= factor["weight"] <= 1.0


@pytest.mark.unit
class TestCredibilityScoring:
    """Additional unit tests for credibility scoring."""
    
    def test_empty_metrics(self):
        """Test handling of empty metrics."""
        service = CredibilityScoringServiceV2()
        score = service.calculate_credibility_score()
        
        assert isinstance(score, CredibilityScore)
        assert score.credibility_score == 0.5  # Default middle score
    
    def test_score_bounds(self):
        """Test that scores stay within bounds."""
        service = CredibilityScoringServiceV2()
        
        # Try extreme values
        extreme_metrics = EnhancedAcousticMetrics(
            pitch_jitter=10.0,  # Very high
            pitch_shimmer=10.0,
            hnr_mean=-50.0  # Invalid but extreme
        )
        
        score = service.calculate_credibility_score(acoustic_metrics=extreme_metrics)
        assert 0.0 <= score.credibility_score <= 1.0
        assert 0.0 <= score.confidence_interval_lower <= 1.0
        assert 0.0 <= score.confidence_interval_upper <= 1.0
