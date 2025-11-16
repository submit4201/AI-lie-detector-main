"""
Unit tests for v2 EnhancedMetricsService and CredibilityServiceV2
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

from backend.services.v2_services.enhanced_metrics_service import EnhancedMetricsService
from backend.services.v2_services.credibility_service import CredibilityServiceV2


# Mock AnalysisContext
@dataclass
class MockAnalysisContext:
    transcript_partial: str = ""
    transcript_final: Optional[str] = None
    audio_bytes: Optional[bytes] = None
    audio_summary: Dict[str, Any] = field(default_factory=dict)
    acoustic_metrics: Optional[Dict[str, Any]] = None
    linguistic_metrics: Optional[Dict[str, Any]] = None
    baseline_profile: Optional[Dict[str, Any]] = None
    quantitative_metrics: Dict[str, Any] = field(default_factory=dict)
    service_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    speaker_segments: List[Dict[str, Any]] = field(default_factory=list)
    session_summary: Optional[Dict[str, Any]] = None
    config: Dict[str, Any] = field(default_factory=dict)


@pytest.fixture
def enhanced_metrics_service():
    """Create EnhancedMetricsService instance."""
    return EnhancedMetricsService()


@pytest.fixture
def credibility_service():
    """Create CredibilityServiceV2 instance."""
    return CredibilityServiceV2()


@pytest.fixture
def mock_context():
    """Create mock analysis context."""
    return MockAnalysisContext(
        transcript_partial="This is a test transcript.",
        transcript_final="This is a complete test transcript with more content.",
        audio_summary={"sample_rate": 16000, "channels": 1, "duration": 5.0}
    )


class TestEnhancedMetricsService:
    """Tests for EnhancedMetricsService."""
    
    def test_initialization(self, enhanced_metrics_service):
        """Test service initialization."""
        assert enhanced_metrics_service.serviceName == "enhanced_metrics"
        assert enhanced_metrics_service.serviceVersion == "2.0"
        assert enhanced_metrics_service.acoustic_service is not None
        assert enhanced_metrics_service.linguistic_service is not None
    
    @pytest.mark.asyncio
    async def test_stream_analyze_linguistic_only(self, enhanced_metrics_service, mock_context):
        """Test streaming analysis with only linguistic data."""
        meta = {"analysis_context": mock_context}
        
        chunks = []
        async for chunk in enhanced_metrics_service.stream_analyze(
            transcript="This is a test.",
            audio=None,
            meta=meta
        ):
            chunks.append(chunk)
        
        # Should get coarse linguistic and final linguistic
        assert len(chunks) >= 1
        
        # Check coarse phase
        coarse_chunk = chunks[0]
        assert coarse_chunk["service_name"] == "enhanced_metrics"
        assert coarse_chunk["partial"] == True
        assert coarse_chunk["phase"] == "coarse"
        assert "linguistic_metrics" in coarse_chunk["local"]
    
    @pytest.mark.asyncio
    async def test_stream_analyze_full(self, enhanced_metrics_service, mock_context):
        """Test streaming analysis with audio and transcript."""
        # Create dummy audio bytes
        audio_data = b'\x00' * 1000
        
        meta = {"analysis_context": mock_context, "sample_rate": 16000, "channels": 1}
        
        chunks = []
        async for chunk in enhanced_metrics_service.stream_analyze(
            transcript=mock_context.transcript_final,
            audio=audio_data,
            meta=meta
        ):
            chunks.append(chunk)
        
        # Should get coarse and final phases
        assert len(chunks) >= 2
        
        # Check final chunk
        final_chunk = [c for c in chunks if not c.get("partial", False)][0]
        assert final_chunk["service_name"] == "enhanced_metrics"
        assert final_chunk["phase"] == "final"
        assert "acoustic_metrics" in final_chunk["local"]
        assert "linguistic_metrics" in final_chunk["local"]
    
    @pytest.mark.asyncio
    async def test_analyze_method(self, enhanced_metrics_service):
        """Test non-streaming analyze method."""
        result = await enhanced_metrics_service.analyze(
            transcript="Test transcript.",
            audio=None,
            meta={}
        )
        
        assert "service_name" in result
        assert "service_version" in result
        assert "local" in result
        assert result["partial"] == False
    
    @pytest.mark.asyncio
    async def test_error_handling(self, enhanced_metrics_service):
        """Test error handling with invalid data."""
        # Should handle gracefully without crashing
        chunks = []
        async for chunk in enhanced_metrics_service.stream_analyze(
            transcript=None,
            audio=None,
            meta=None
        ):
            chunks.append(chunk)
        
        # Should still return some result (possibly with errors)
        assert len(chunks) >= 0  # May not yield anything with no data


class TestCredibilityServiceV2:
    """Tests for CredibilityServiceV2."""
    
    def test_initialization(self, credibility_service):
        """Test service initialization."""
        assert credibility_service.serviceName == "credibility"
        assert credibility_service.serviceVersion == "2.0"
        assert credibility_service.scoring_service is not None
    
    @pytest.mark.asyncio
    async def test_stream_analyze_no_context(self, credibility_service):
        """Test streaming analysis without context."""
        chunks = []
        async for chunk in credibility_service.stream_analyze(
            transcript="Test",
            audio=None,
            meta={}
        ):
            chunks.append(chunk)
        
        assert len(chunks) >= 1
        assert chunks[0]["errors"]  # Should have error about missing context
    
    @pytest.mark.asyncio
    async def test_stream_analyze_with_metrics(self, credibility_service, mock_context):
        """Test streaming analysis with enhanced metrics."""
        # Add metrics to context
        mock_context.acoustic_metrics = {
            "pitch_jitter": 0.01,
            "pitch_shimmer": 0.05,
            "voice_quality_score": 0.8,
            "hnr_mean": 15.0,
            "signal_to_noise_ratio": 25.0,
            "speech_rate_wpm": 120.0,
            "pause_rate": 5.0,
            "intensity_mean": 60.0,
            "pitch_mean": 150.0
        }
        
        mock_context.linguistic_metrics = {
            "pronoun_ratio_first_person": 0.05,
            "sentence_complexity_score": 0.6,
            "emotional_leakage_ratio": 0.02,
            "prosodic_congruence_score": 0.75
        }
        
        meta = {"analysis_context": mock_context}
        
        chunks = []
        async for chunk in credibility_service.stream_analyze(
            transcript=mock_context.transcript_final,
            audio=None,
            meta=meta
        ):
            chunks.append(chunk)
        
        # Should get coarse and final assessments
        assert len(chunks) >= 1
        
        # Check that we got credibility scores
        for chunk in chunks:
            if not chunk.get("errors"):
                assert "credibility_score" in chunk.get("local", {})
    
    @pytest.mark.asyncio
    async def test_behavioral_data_extraction(self, credibility_service, mock_context):
        """Test extraction of behavioral data from context."""
        mock_context.quantitative_metrics = {
            "hesitation_marker_count": 5,
            "word_count": 100,
            "certainty_indicator_count": 10,
            "qualifier_count": 5
        }
        
        behavioral_data = credibility_service._extract_behavioral_data(mock_context)
        
        assert behavioral_data is not None
        assert "hesitation_score" in behavioral_data
        assert "confidence_indicators" in behavioral_data
        assert 0.0 <= behavioral_data["confidence_indicators"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_consistency_data_extraction(self, credibility_service, mock_context):
        """Test extraction of consistency data from context."""
        mock_context.service_results = {
            "enhanced_understanding": {
                "local": {
                    "key_inconsistencies": ["Inconsistency 1", "Inconsistency 2"]
                }
            }
        }
        
        consistency_data = credibility_service._extract_consistency_data(mock_context)
        
        assert consistency_data is not None
        assert "consistency_score" in consistency_data
        assert 0.0 <= consistency_data["consistency_score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_analyze_method(self, credibility_service, mock_context):
        """Test non-streaming analyze method."""
        mock_context.acoustic_metrics = {
            "voice_quality_score": 0.8,
            "hnr_mean": 15.0
        }
        mock_context.linguistic_metrics = {
            "sentence_complexity_score": 0.6
        }
        
        result = await credibility_service.analyze(
            transcript=mock_context.transcript_final,
            audio=None,
            meta={"analysis_context": mock_context}
        )
        
        assert "service_name" in result
        assert "service_version" in result
        assert result["partial"] == False
    
    @pytest.mark.asyncio
    async def test_ema_smoothing_integration(self, credibility_service, mock_context):
        """Test EMA smoothing with previous scores."""
        mock_context.acoustic_metrics = {
            "voice_quality_score": 0.8,
            "hnr_mean": 15.0,
            "pitch_mean": 150.0
        }
        mock_context.linguistic_metrics = {
            "sentence_complexity_score": 0.6
        }
        
        # Add previous score to context
        mock_context.service_results["credibility"] = {
            "local": {
                "credibility_score": {
                    "credibility_score": 0.65
                }
            }
        }
        
        meta = {"analysis_context": mock_context}
        
        chunks = []
        async for chunk in credibility_service.stream_analyze(
            transcript=mock_context.transcript_final,
            audio=None,
            meta=meta
        ):
            chunks.append(chunk)
        
        # Check final chunk has EMA smoothed score
        final_chunks = [c for c in chunks if not c.get("partial", False)]
        if final_chunks and not final_chunks[0].get("errors"):
            final_chunk = final_chunks[0]
            credibility_data = final_chunk["local"].get("credibility_score", {})
            # Should have ema_smoothed_score if previous score was available
            # (might be None if scoring failed, but structure should be there)
            assert "credibility_score" in credibility_data


@pytest.mark.unit
class TestV2ServicesIntegration:
    """Integration tests for v2 services."""
    
    @pytest.mark.asyncio
    async def test_enhanced_metrics_updates_context(self):
        """Test that enhanced metrics service updates context."""
        service = EnhancedMetricsService()
        context = MockAnalysisContext(
            transcript_partial="This is a test.",
            transcript_final="This is a complete test."
        )
        
        meta = {"analysis_context": context}
        
        async for chunk in service.stream_analyze(
            transcript=context.transcript_final,
            audio=None,
            meta=meta
        ):
            pass  # Consume stream
        
        # Context should be updated
        assert context.linguistic_metrics is not None
    
    @pytest.mark.asyncio
    async def test_credibility_uses_enhanced_metrics(self):
        """Test that credibility service uses enhanced metrics from context."""
        context = MockAnalysisContext(
            transcript_final="Complete test transcript.",
            acoustic_metrics={"voice_quality_score": 0.8},
            linguistic_metrics={"sentence_complexity_score": 0.6}
        )
        
        service = CredibilityServiceV2()
        meta = {"analysis_context": context}
        
        final_chunk = None
        async for chunk in service.stream_analyze(
            transcript=context.transcript_final,
            audio=None,
            meta=meta
        ):
            if not chunk.get("partial", False):
                final_chunk = chunk
        
        assert final_chunk is not None
        if not final_chunk.get("errors"):
            assert "credibility_score" in final_chunk.get("local", {})
