"""
Enhanced Acoustic Analysis Service
Integrates parselmouth-based acoustic feature extraction with the analysis pipeline.
"""

import numpy as np
from typing import Optional, Dict, Any, List
from backend.models import EnhancedAcousticMetrics

# Optional import of layer_2_feature_extraction (may have heavy dependencies)
try:
    from backend.layer_2_feature_extraction import extract_acoustic_features_from_data
    ACOUSTIC_EXTRACTION_AVAILABLE = True
except ImportError:
    ACOUSTIC_EXTRACTION_AVAILABLE = False


class EnhancedAcousticService:
    """
    Service for extracting comprehensive acoustic features from audio data.
    Integrates with existing parselmouth-based extraction.
    """
    
    def __init__(self):
        """Initialize the enhanced acoustic service."""
        pass
    
    def calculate_speech_rate_sps(
        self, 
        transcript: str, 
        duration_seconds: float,
        exclude_pauses: bool = True,
        pause_duration: float = 0.0
    ) -> float:
        """
        Calculate speech rate in syllables per second.
        
        Args:
            transcript: Transcript text
            duration_seconds: Audio duration in seconds
            exclude_pauses: Whether to exclude pauses (articulation rate)
            pause_duration: Total pause duration in seconds
            
        Returns:
            Speech rate in syllables per second
        """
        if duration_seconds <= 0:
            return 0.0
        
        # Estimate syllables (rough approximation based on vowel groups)
        # More sophisticated: use pyphen or similar library
        syllables = self._estimate_syllables(transcript)
        
        if exclude_pauses and pause_duration > 0:
            effective_duration = duration_seconds - pause_duration
        else:
            effective_duration = duration_seconds
        
        if effective_duration <= 0:
            return 0.0
        
        return syllables / effective_duration
    
    def _estimate_syllables(self, text: str) -> int:
        """
        Estimate syllable count from text.
        Simple vowel-group counting method.
        
        Args:
            text: Input text
            
        Returns:
            Estimated syllable count
        """
        text = text.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False
        
        for char in text:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent 'e' at end
        if text.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        # Ensure at least one syllable per word
        word_count = len(text.split())
        if syllable_count < word_count:
            syllable_count = word_count
        
        return syllable_count
    
    def calculate_vocal_tremor(self, pitch_values: np.ndarray, sample_rate: float = 100.0) -> Dict[str, Optional[float]]:
        """
        Detect and quantify vocal tremor from pitch contour.
        
        Args:
            pitch_values: Array of pitch values (F0) over time
            sample_rate: Sampling rate of pitch values (default: 100 Hz)
            
        Returns:
            Dictionary with tremor_rate and tremor_intensity
        """
        tremor_info = {
            "tremor_rate": None,
            "tremor_intensity": None
        }
        
        if len(pitch_values) < 10:
            return tremor_info
        
        # Remove zeros (unvoiced segments)
        voiced_pitch = pitch_values[pitch_values != 0]
        if len(voiced_pitch) < 10:
            return tremor_info
        
        # Detrend the pitch contour
        detrended = voiced_pitch - np.mean(voiced_pitch)
        
        # Calculate FFT to find dominant tremor frequency
        fft = np.fft.fft(detrended)
        frequencies = np.fft.fftfreq(len(detrended), 1.0 / sample_rate)
        
        # Focus on tremor range (typically 4-12 Hz)
        tremor_range = (frequencies >= 4) & (frequencies <= 12)
        if not np.any(tremor_range):
            return tremor_info
        
        tremor_spectrum = np.abs(fft[tremor_range])
        tremor_freqs = frequencies[tremor_range]
        
        # Find peak in tremor range
        if len(tremor_spectrum) > 0:
            peak_idx = np.argmax(tremor_spectrum)
            tremor_info["tremor_rate"] = float(tremor_freqs[peak_idx])
            
            # Tremor intensity as ratio of tremor peak to total power
            total_power = np.sum(np.abs(fft) ** 2)
            tremor_power = tremor_spectrum[peak_idx] ** 2
            if total_power > 0:
                tremor_info["tremor_intensity"] = float(tremor_power / total_power)
        
        return tremor_info
    
    def calculate_formant_dispersion(
        self, 
        f1_values: np.ndarray, 
        f2_values: np.ndarray, 
        f3_values: np.ndarray
    ) -> float:
        """
        Calculate formant dispersion as a measure of vowel space.
        
        Args:
            f1_values: First formant frequencies
            f2_values: Second formant frequencies
            f3_values: Third formant frequencies
            
        Returns:
            Formant dispersion measure
        """
        # Remove zeros
        f1_nonzero = f1_values[f1_values != 0]
        f2_nonzero = f2_values[f2_values != 0]
        f3_nonzero = f3_values[f3_values != 0]
        
        if len(f1_nonzero) == 0 or len(f2_nonzero) == 0 or len(f3_nonzero) == 0:
            return 0.0
        
        # Calculate standard deviations (spread in formant space)
        f1_std = np.std(f1_nonzero)
        f2_std = np.std(f2_nonzero)
        f3_std = np.std(f3_nonzero)
        
        # Combined dispersion measure
        dispersion = (f1_std + f2_std + f3_std) / 3.0
        
        return float(dispersion)
    
    def calculate_intensity_slope(self, intensity_values: np.ndarray, time_values: np.ndarray) -> Optional[float]:
        """
        Calculate slope of intensity curve over time.
        
        Args:
            intensity_values: Array of intensity values
            time_values: Corresponding time values
            
        Returns:
            Slope of intensity curve (dB/second)
        """
        if len(intensity_values) < 2 or len(time_values) < 2:
            return None
        
        # Linear regression to find slope
        coefficients = np.polyfit(time_values, intensity_values, 1)
        slope = coefficients[0]
        
        return float(slope)
    
    def extract_enhanced_metrics(
        self,
        audio_bytes: bytes,
        sample_rate: int,
        channels: int,
        transcript: Optional[str] = None,
        duration_seconds: Optional[float] = None
    ) -> EnhancedAcousticMetrics:
        """
        Extract comprehensive enhanced acoustic metrics.
        
        Args:
            audio_bytes: Raw audio data
            sample_rate: Sample rate in Hz
            channels: Number of channels
            transcript: Optional transcript for speech rate calculation
            duration_seconds: Optional audio duration
            
        Returns:
            EnhancedAcousticMetrics with comprehensive features
        """
        # Check if acoustic extraction is available
        if not ACOUSTIC_EXTRACTION_AVAILABLE:
            # Return minimal metrics if extraction not available
            return self._get_minimal_metrics(
                audio_bytes, sample_rate, channels, transcript, duration_seconds
            )
        
        # Extract base acoustic features using existing function
        base_features = extract_acoustic_features_from_data(audio_bytes, sample_rate, channels)
        
        # Calculate duration if not provided
        if duration_seconds is None:
            duration_seconds = len(audio_bytes) / (sample_rate * channels * 2)  # 16-bit audio
        
        # Calculate additional metrics
        
        # Speech rate
        speech_rate_wpm = 0.0
        speech_rate_sps = 0.0
        articulation_rate = 0.0
        
        if transcript and duration_seconds > 0:
            word_count = len(transcript.split())
            speech_rate_wpm = (word_count / duration_seconds) * 60.0
            
            pause_duration = base_features.get("pause_duration", 0.0)
            speech_rate_sps = self.calculate_speech_rate_sps(
                transcript, duration_seconds, exclude_pauses=False, pause_duration=pause_duration
            )
            articulation_rate = self.calculate_speech_rate_sps(
                transcript, duration_seconds, exclude_pauses=True, pause_duration=pause_duration
            )
        
        # Pause metrics
        pause_count = base_features.get("pause_count", 0)
        pause_duration_total = base_features.get("pause_duration", 0.0)
        pause_duration_mean = pause_duration_total / max(1, pause_count)
        pause_duration_std = 0.0  # Would need individual pause durations
        pause_rate = (pause_count / duration_seconds) * 60.0 if duration_seconds > 0 else 0.0
        
        # Calculate voice quality score (composite of HNR, jitter, shimmer)
        hnr_mean = base_features.get("hnr_std", 0.0)  # Note: existing code might have hnr in different field
        jitter = base_features.get("pitch_jitter", 0.0)
        shimmer = base_features.get("pitch_shimmer", 0.0)
        
        # Voice quality: high HNR, low jitter/shimmer = high quality
        hnr_normalized = min(1.0, hnr_mean / 20.0) if hnr_mean > 0 else 0.5
        jitter_score = max(0.0, 1.0 - min(1.0, jitter * 100))
        shimmer_score = max(0.0, 1.0 - min(1.0, shimmer * 10))
        voice_quality_score = (hnr_normalized + jitter_score + shimmer_score) / 3.0
        
        # Build EnhancedAcousticMetrics
        metrics = EnhancedAcousticMetrics(
            # Pitch metrics
            pitch_jitter=base_features.get("pitch_jitter", 0.0),
            pitch_shimmer=base_features.get("pitch_shimmer", 0.0),
            pitch_mean=0.0,  # Would need to calculate from pitch values
            pitch_std=base_features.get("pitch_std", 0.0),
            pitch_range=base_features.get("pitch_range", 0.0),
            
            # Vocal tremor (placeholder - needs implementation)
            vocal_tremor_rate=None,
            vocal_tremor_intensity=None,
            
            # Formants
            formant_f1_mean=0.0,  # Would need formant extraction
            formant_f2_mean=0.0,
            formant_f3_mean=0.0,
            formant_dispersion=0.0,
            formant_std=base_features.get("formant_std", 0.0),
            formant_range=base_features.get("formant_range", 0.0),
            
            # Intensity and loudness
            intensity_mean=0.0,
            intensity_std=base_features.get("intensity_std", 0.0),
            intensity_range=base_features.get("intensity_range", 0.0),
            intensity_slope=None,
            loudness_mean=0.0,
            loudness_std=base_features.get("loudness_std", 0.0),
            loudness_range=base_features.get("loudness_range", 0.0),
            loudness_slope=None,
            
            # Pauses
            pause_duration_total=pause_duration_total,
            pause_count=pause_count,
            pause_duration_mean=pause_duration_mean,
            pause_duration_std=pause_duration_std,
            pause_rate=pause_rate,
            
            # Speech rate
            speech_rate_wpm=speech_rate_wpm,
            speech_rate_sps=speech_rate_sps,
            articulation_rate=articulation_rate,
            
            # HNR
            hnr_mean=hnr_mean,
            hnr_std=base_features.get("hnr_std", 0.0),
            hnr_range=base_features.get("hnr_range", 0.0),
            
            # Energy
            energy_mean=0.0,
            energy_std=base_features.get("energy_std", 0.0),
            energy_range=base_features.get("energy_range", 0.0),
            
            # Point process
            point_process_mean=0.0,
            point_process_std=base_features.get("point_process_std", 0.0),
            point_process_range=base_features.get("point_process_range", 0.0),
            
            # Quality
            voice_quality_score=voice_quality_score,
            signal_to_noise_ratio=0.0  # Would need SNR calculation
        )
        
        return metrics
    
    def _get_minimal_metrics(
        self,
        audio_bytes: bytes,
        sample_rate: int,
        channels: int,
        transcript: Optional[str] = None,
        duration_seconds: Optional[float] = None
    ) -> EnhancedAcousticMetrics:
        """
        Return minimal metrics when full extraction is not available.
        
        Args:
            audio_bytes: Raw audio data
            sample_rate: Sample rate in Hz
            channels: Number of channels
            transcript: Optional transcript
            duration_seconds: Optional duration
            
        Returns:
            EnhancedAcousticMetrics with basic/default values
        """
        # Calculate duration if not provided
        if duration_seconds is None:
            duration_seconds = len(audio_bytes) / (sample_rate * channels * 2)
        
        # Basic speech rate calculation if transcript available
        speech_rate_wpm = 0.0
        if transcript and duration_seconds > 0:
            word_count = len(transcript.split())
            speech_rate_wpm = (word_count / duration_seconds) * 60.0
        
        return EnhancedAcousticMetrics(
            speech_rate_wpm=speech_rate_wpm,
            voice_quality_score=0.5  # Neutral default
        )
