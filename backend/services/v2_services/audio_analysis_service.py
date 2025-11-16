"""AudioAnalysisService v2

This service performs low-level audio analysis, such as assessing audio quality
metrics. It does not rely on an LLM and performs all its calculations locally.

Comparison to v1:
- v1 audio assessment lived inside a larger `audio_service.py` module and often
    duplicated audio checks across different endpoints.
- v2 isolates audio quality into a focused service returning `AudioQualityMetrics`.
    This enables better reuse and clearer failure handling when transcriptions or
    other services depend on audio metadata such as duration.
"""
import logging
from typing import Optional, Dict, Any

from pydub import AudioSegment
import numpy as np
import io

from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.models import AudioQualityMetrics, ErrorResponse

logger = logging.getLogger(__name__)


class AudioAnalysisService(AnalysisService):
    """A service for local audio quality analysis."""
    serviceName = "audio_analysis"
    serviceVersion = "2.0"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("AudioAnalysisService initialized.")

    def _assess_audio_quality(self, audio_segment: AudioSegment) -> AudioQualityMetrics:
        """Calculates various audio quality metrics from a Pydub AudioSegment."""
        samples = np.array(audio_segment.get_array_of_samples())
        
        duration = audio_segment.duration_seconds
        sample_rate = audio_segment.frame_rate
        channels = audio_segment.channels
        
        # Loudness (RMS)
        rms = np.sqrt(np.mean(samples.astype(np.float64)**2))
        loudness = 20 * np.log10(rms) if rms > 0 else -100.0
        
        # Signal-to-Noise Ratio (SNR) - simplified
        signal_power = np.mean(samples**2)
        noise_power = signal_power / 100  # Assume 1% noise for a simple SNR
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 0.0
        
        # Clarity Score (based on high-frequency content)
        fft_data = np.fft.fft(samples)
        freqs = np.fft.fftfreq(len(fft_data), 1/sample_rate)
        high_freq_power = np.sum(np.abs(fft_data[np.where(freqs > 4000)])**2)
        total_power = np.sum(np.abs(fft_data)**2)
        clarity_score = (high_freq_power / total_power) * 100 if total_power > 0 else 0.0

        # Overall Quality Score (heuristic)
        quality_score = 0
        if duration > 1: quality_score += 20
        if sample_rate >= 16000: quality_score += 20
        if loudness > -60: quality_score += 20
        if snr > 10: quality_score += 20
        if clarity_score > 10: quality_score += 20

        overall_quality = "good" if quality_score >= 60 else "fair" if quality_score >= 40 else "poor"

        return AudioQualityMetrics(
            duration=round(duration, 2),
            sample_rate=sample_rate,
            channels=channels,
            loudness=round(loudness, 2),
            quality_score=int(quality_score),
            overall_quality=overall_quality,
            signal_to_noise_ratio=round(snr, 2),
            clarity_score=round(clarity_score, 2),
            volume_consistency=0,  # Placeholder
            background_noise_level=0,  # Placeholder
        )

    async def stream_analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ):
        """
        Stream audio quality analysis with incremental results.
        
        Yields:
        - Coarse phase: Quick preliminary metrics (duration, sample rate)
        - Final phase: Complete quality assessment
        """
        if not audio:
            logger.warning("No audio data provided to AudioAnalysisService.")
            error_model = ErrorResponse(
                error="No audio data provided.",
                code=400,
                details={},
                suggestion="Upload a supported audio file (WAV, MP3, etc.)",
            )
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": AudioQualityMetrics().model_dump(),
                "gemini": None,
                "errors": [error_model.model_dump()],
                "partial": False,
                "phase": "final",
                "chunk_index": 0
            }
            return

        try:
            audio_segment = AudioSegment.from_file(io.BytesIO(audio))
            
            # Phase 1: Yield quick preliminary metrics (coarse)
            quick_metrics = {
                "duration": round(audio_segment.duration_seconds, 2),
                "sample_rate": audio_segment.frame_rate,
                "channels": audio_segment.channels,
            }
            
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": quick_metrics,
                "gemini": None,
                "errors": [],
                "partial": True,
                "phase": "coarse",
                "chunk_index": 0
            }
            
            # Phase 2: Complete analysis (final)
            quality_metrics = self._assess_audio_quality(audio_segment)
            logger.info("Audio quality analysis successful.")
            
            # Update meta with duration if not present
            if meta and 'duration' not in meta:
                meta['duration'] = quality_metrics.duration

            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": quality_metrics.model_dump(),
                "gemini": None,
                "errors": [],
                "partial": False,
                "phase": "final",
                "chunk_index": 1
            }
        except Exception as e:
            logger.error(f"Audio quality analysis failed: {e}", exc_info=True)
            error_model = ErrorResponse(
                error="Audio processing failed",
                code=500,
                details={"exception_str": str(e)},
                suggestion="Ensure the uploaded file is a valid audio format and not corrupt.",
            )
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": AudioQualityMetrics().model_dump(),
                "gemini": None,
                "errors": [error_model.model_dump()],
                "partial": False,
                "phase": "final",
                "chunk_index": 0
            }

    async def analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyzes the audio bytes to determine quality metrics (non-streaming)."""
        if not audio:
            logger.warning("No audio data provided to AudioAnalysisService.")
            # Return a structured error using the ErrorResponse model so the API
            # surface is consistent and testable. Note: we intentionally don't
            # include raw audio content in the error log.
            error_model = ErrorResponse(
                error="No audio data provided.",
                code=400,
                details={},
                suggestion="Upload a supported audio file (WAV, MP3, etc.)",
            )
            return {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": AudioQualityMetrics().model_dump(),
                "gemini": None,
                "errors": [error_model.model_dump()],
            }

        async def stream_analyze(self, transcript: Optional[str] = None, audio: Optional[bytes] = None, meta: Optional[Dict[str, Any]] = None):
            """Yield a coarse audio summary immediately (if possible), then the full analysis."""
            if not audio:
                # No audio -> just run analyze path
                yield await self.analyze(transcript, audio, meta or {})
                return

            # Quick, lightweight audio heuristics: length and sample rate if accessible
            try:
                audio_segment = AudioSegment.from_file(io.BytesIO(audio))
                duration = round(audio_segment.duration_seconds, 2)
                initial = {
                    "service_name": self.serviceName,
                    "service_version": self.serviceVersion,
                    "local": {"duration": duration},
                    "gemini": None,
                    "errors": None,
                }
                # Update analysis context
                if meta and meta.get("analysis_context"):
                    try:
                        meta.get("analysis_context").audio_summary.update({"duration": duration})
                    except Exception:
                        pass
                yield initial
            except Exception:
                # Fall through to final analysis which will produce a proper error
                pass

            # Final result
            yield await self.analyze(transcript, audio, meta or {})

        try:
            audio_segment = AudioSegment.from_file(io.BytesIO(audio))
            quality_metrics = self._assess_audio_quality(audio_segment)
            logger.info("Audio quality analysis successful.")
            
            # Update meta with duration if not present
            if meta and 'duration' not in meta:
                meta['duration'] = quality_metrics.duration

            return {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": quality_metrics.model_dump(),
                "gemini": None,
                "errors": None,
            }
        except Exception as e:
            logger.error(f"Audio quality analysis failed: {e}", exc_info=True)
            # Return a structured ErrorResponse with sanitized details
            error_model = ErrorResponse(
                error="Audio processing failed",
                code=500,
                details={"exception_str": str(e)},
                suggestion="Ensure the uploaded file is a valid audio format and not corrupt.",
            )
            return {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": AudioQualityMetrics().model_dump(),
                "gemini": None,
                "errors": [error_model.model_dump()],
            }
