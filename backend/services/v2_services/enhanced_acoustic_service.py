"""EnhancedAcousticService v2

Advanced acoustic feature extraction for deception detection and credibility analysis.
Uses parselmouth (Praat Python library) for sophisticated voice analysis.

Extracts metrics including:
- Pitch jitter and shimmer (vocal fold instability)
- Formants (vocal tract resonance)
- HNR (Harmonics-to-Noise Ratio)
- Intensity and spectral features
- Pause detection and speech rate

Based on forensic phonetics research showing these metrics correlate with
cognitive load, stress, and deceptive behavior.
"""
import logging
import numpy as np
from typing import Optional, Dict, Any, AsyncGenerator
import io

from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.models import EnhancedAcousticMetrics

logger = logging.getLogger(__name__)

# Try to import parselmouth (Praat library)
try:
    import parselmouth
    from parselmouth.praat import call
    PARSELMOUTH_AVAILABLE = True
except ImportError:
    PARSELMOUTH_AVAILABLE = False
    logger.warning("parselmouth not available - enhanced acoustic analysis will be limited")


class EnhancedAcousticService(AnalysisService):
    """V2 service for advanced acoustic analysis with streaming support."""
    
    serviceName = "enhanced_acoustic"
    serviceVersion = "2.0"
    
    def __init__(self, transcript: str = "", audio_data: Optional[bytes] = None, meta: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(transcript=transcript, audio_data=audio_data, meta=meta)
        self.audio_data = audio_data
    
    def _extract_acoustic_features(self, audio_bytes: bytes) -> EnhancedAcousticMetrics:
        """Extract advanced acoustic features using parselmouth/Praat."""
        
        if not PARSELMOUTH_AVAILABLE:
            return EnhancedAcousticMetrics(
                analysis_quality="failed",
                insufficient_voiced=True
            )
        
        try:
            # Load audio into Praat Sound object
            sound = parselmouth.Sound(io.BytesIO(audio_bytes))
            
            # Check if we have enough audio
            if sound.duration < 0.5:
                return EnhancedAcousticMetrics(
                    analysis_quality="poor",
                    insufficient_voiced=True
                )
            
            # Extract pitch (F0)
            pitch = sound.to_pitch(time_step=0.01)  # 10ms frames
            
            # Get pitch statistics
            pitch_values = pitch.selected_array['frequency']
            pitch_values = pitch_values[pitch_values > 0]  # Only voiced frames
            
            if len(pitch_values) < 10:
                return EnhancedAcousticMetrics(
                    analysis_quality="poor",
                    insufficient_voiced=True
                )
            
            pitch_mean = float(np.mean(pitch_values))
            pitch_std = float(np.std(pitch_values))
            pitch_range = float(np.max(pitch_values) - np.min(pitch_values))
            
            # Extract jitter and shimmer (requires PointProcess)
            try:
                point_process = call(sound, "To PointProcess (periodic, cc)", 75, 500)
                jitter = call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
                shimmer = call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
                
                # Convert to percentage
                jitter_pct = jitter * 100 if jitter and not np.isnan(jitter) else None
                shimmer_pct = shimmer * 100 if shimmer and not np.isnan(shimmer) else None
            except Exception as e:
                logger.debug(f"Could not extract jitter/shimmer: {e}")
                jitter_pct = None
                shimmer_pct = None
            
            # Extract formants
            try:
                formant = sound.to_formant_burg(time_step=0.01)
                
                # Get mean formants (F1, F2, F3)
                n_frames = formant.get_number_of_frames()
                f1_values, f2_values, f3_values = [], [], []
                
                for i in range(1, min(n_frames + 1, 200)):  # Limit to first 200 frames
                    try:
                        f1 = formant.get_value_at_time(1, formant.get_time_from_frame_number(i))
                        f2 = formant.get_value_at_time(2, formant.get_time_from_frame_number(i))
                        f3 = formant.get_value_at_time(3, formant.get_time_from_frame_number(i))
                        
                        if f1 and not np.isnan(f1):
                            f1_values.append(f1)
                        if f2 and not np.isnan(f2):
                            f2_values.append(f2)
                        if f3 and not np.isnan(f3):
                            f3_values.append(f3)
                    except Exception:
                        continue
                
                f1_mean = float(np.mean(f1_values)) if f1_values else None
                f2_mean = float(np.mean(f2_values)) if f2_values else None
                f3_mean = float(np.mean(f3_values)) if f3_values else None
                
                # Formant dispersion (simple approximation)
                if f1_mean and f2_mean and f3_mean:
                    formant_dispersion = float(np.std([f1_mean, f2_mean, f3_mean]))
                else:
                    formant_dispersion = None
                    
            except Exception as e:
                logger.debug(f"Could not extract formants: {e}")
                f1_mean = f2_mean = f3_mean = formant_dispersion = None
            
            # Extract HNR (Harmonics-to-Noise Ratio)
            try:
                harmonicity = sound.to_harmonicity()
                hnr_values = harmonicity.values[harmonicity.values > -200]  # Filter invalid values
                
                if len(hnr_values) > 0:
                    hnr_mean = float(np.mean(hnr_values))
                    hnr_std = float(np.std(hnr_values))
                else:
                    hnr_mean = hnr_std = None
            except Exception as e:
                logger.debug(f"Could not extract HNR: {e}")
                hnr_mean = hnr_std = None
            
            # Extract intensity
            try:
                intensity = sound.to_intensity()
                intensity_values = intensity.values[0]
                intensity_values = intensity_values[intensity_values > 0]
                
                if len(intensity_values) > 0:
                    intensity_mean = float(np.mean(intensity_values))
                    intensity_std = float(np.std(intensity_values))
                    intensity_range = float(np.max(intensity_values) - np.min(intensity_values))
                else:
                    intensity_mean = intensity_std = intensity_range = None
            except Exception as e:
                logger.debug(f"Could not extract intensity: {e}")
                intensity_mean = intensity_std = intensity_range = None
            
            # Detect pauses (simplified - using intensity drops)
            try:
                # Threshold for pause: intensity below 40% of mean
                if intensity_mean:
                    pause_threshold = intensity_mean * 0.4
                    intensity_array = intensity.values[0]
                    
                    # Count pauses (consecutive frames below threshold)
                    is_pause = intensity_array < pause_threshold
                    pause_starts = np.where(np.diff(is_pause.astype(int)) == 1)[0]
                    pause_count = len(pause_starts)
                    
                    # Total pause duration (rough estimate)
                    pause_frames = np.sum(is_pause)
                    pause_duration_total = pause_frames * 0.01  # Assuming 10ms frames
                    
                    # Pause rate (per minute)
                    pause_rate = (pause_count / sound.duration) * 60 if sound.duration > 0 else 0
                else:
                    pause_count = pause_duration_total = pause_rate = None
            except Exception as e:
                logger.debug(f"Could not detect pauses: {e}")
                pause_count = pause_duration_total = pause_rate = None
            
            # Spectral features (using FFT)
            try:
                samples = sound.values[0]
                fft = np.fft.fft(samples)
                freqs = np.fft.fftfreq(len(fft), 1/sound.sampling_frequency)
                
                # Only positive frequencies
                positive_freqs = freqs[:len(freqs)//2]
                magnitude = np.abs(fft[:len(fft)//2])
                
                # Spectral centroid
                if np.sum(magnitude) > 0:
                    spectral_centroid = float(np.sum(positive_freqs * magnitude) / np.sum(magnitude))
                else:
                    spectral_centroid = None
                
                # Spectral entropy (simplified)
                if np.sum(magnitude) > 0:
                    normalized_magnitude = magnitude / np.sum(magnitude)
                    # Avoid log(0)
                    normalized_magnitude = normalized_magnitude[normalized_magnitude > 0]
                    spectral_entropy = float(-np.sum(normalized_magnitude * np.log2(normalized_magnitude)))
                else:
                    spectral_entropy = None
                    
            except Exception as e:
                logger.debug(f"Could not extract spectral features: {e}")
                spectral_centroid = spectral_entropy = None
            
            # Determine analysis quality
            features_extracted = sum([
                pitch_mean is not None,
                jitter_pct is not None,
                f1_mean is not None,
                hnr_mean is not None,
                intensity_mean is not None
            ])
            
            if features_extracted >= 4:
                quality = "good"
            elif features_extracted >= 2:
                quality = "fair"
            else:
                quality = "poor"
            
            return EnhancedAcousticMetrics(
                pitch_jitter=jitter_pct,
                pitch_shimmer=shimmer_pct,
                pitch_mean=pitch_mean,
                pitch_std=pitch_std,
                pitch_range=pitch_range,
                formant_f1_mean=f1_mean,
                formant_f2_mean=f2_mean,
                formant_f3_mean=f3_mean,
                formant_dispersion=formant_dispersion,
                hnr_mean=hnr_mean,
                hnr_std=hnr_std,
                intensity_mean=intensity_mean,
                intensity_std=intensity_std,
                intensity_range=intensity_range,
                pause_count=pause_count,
                pause_duration_total=pause_duration_total,
                pause_rate=pause_rate,
                spectral_centroid=spectral_centroid,
                spectral_entropy=spectral_entropy,
                analysis_quality=quality,
                insufficient_voiced=False
            )
            
        except Exception as e:
            logger.error(f"Enhanced acoustic analysis failed: {e}", exc_info=True)
            return EnhancedAcousticMetrics(
                analysis_quality="failed",
                insufficient_voiced=True
            )
    
    async def stream_analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream enhanced acoustic analysis with pseudo-streaming (coarse → final)."""
        meta = meta or {}
        ctx = meta.get("analysis_context")
        
        # Get audio bytes
        audio_bytes = audio or self.audio_data
        
        if not audio_bytes or len(audio_bytes) < 1000:
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": {},
                "gemini": None,
                "errors": [{"error": "Insufficient audio data for enhanced acoustic analysis"}],
                "partial": False,
                "phase": "final",
                "chunk_index": None,
            }
            return
        
        # Phase 1: Coarse - quick placeholder
        yield {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {"status": "extracting_acoustic_features"},
            "gemini": None,
            "errors": [],
            "partial": True,
            "phase": "coarse",
            "chunk_index": 0,
        }
        
        # Phase 2: Extract features
        acoustic_metrics = self._extract_acoustic_features(audio_bytes)
        
        # Convert to dict safely
        if hasattr(acoustic_metrics, 'model_dump'):
            result_dict = acoustic_metrics.model_dump()
        elif hasattr(acoustic_metrics, '__dict__'):
            result_dict = acoustic_metrics.__dict__
        else:
            result_dict = {}
        
        # Update context
        if ctx:
            if not hasattr(ctx, 'enhanced_acoustic_metrics'):
                ctx.enhanced_acoustic_metrics = {}
            ctx.enhanced_acoustic_metrics.update(result_dict)
            ctx.service_results["enhanced_acoustic"] = result_dict
        
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
