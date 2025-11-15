# layer2_feature_extraction.py

import parselmouth
import numpy as np
import whisper
import spacy
from typing import Dict, Any, List
import io # Added for BytesIO

# Load STT and NLP engines
whisper_model = whisper.load_model("base")  # or "medium" or "large"
nlp = spacy.load("en_core_web_sm")

def extract_acoustic_features_from_data(audio_data: bytes, sample_rate: int, channels: int) -> Dict[str, Any]:
    """Extracts acoustic features from in-memory audio data."""
    # parselmouth.Sound can load from a file path or directly from a numpy array.
    # We need to convert bytes to a numpy array first.
    # Assuming int16 PCM data as common from layer_1_input
    
    # Convert bytes to NumPy array
    # Determine dtype based on typical output of sounddevice 'int16', 'float32' etc.
    # For 'int16', the values range from -32768 to 32767.
    # Parselmouth expects float64 normalized between -1 and 1.
    
    # Assuming data from layer_1_input is 'int16'
    # If layer_1_input.dtype changes, this needs to be adjusted
    numpy_array = np.frombuffer(audio_data, dtype=np.int16)
    
    # Normalize to float64 between -1 and 1
    # Max possible value for int16 is 32767
    numpy_array_float = numpy_array.astype(np.float64) / 32767.0 
    
    # Ensure it's a 1D array if mono, or handle channels appropriately
    # Parselmouth Sound constructor expects a 1D array for mono, or 2D for stereo (samples, channels)
    # Assuming mono for now as per typical layer_1_input default
    if channels > 1:
        # Reshape or take the first channel if stereo, Parselmouth handles mono better for some funcs
        # This might need more sophisticated handling for multi-channel
        numpy_array_float = numpy_array_float[::channels] # Example: take first channel if interleaved

    snd = parselmouth.Sound(numpy_array_float, sampling_frequency=sample_rate)
    
    pitch = snd.to_pitch()
    point_process = snd.to_point_process_cc() # For jitter/shimmer

    # Pitch-related features
    pitch_values = pitch.selected_array['frequency']
    pitch_values_voiced = pitch_values[pitch_values != 0]  # remove unvoiced

    pitch_std = 0.0
    pitch_range = 0.0
    if len(pitch_values_voiced) > 1: # Need at least 2 voiced points for std/range
        pitch_std = np.std(pitch_values_voiced)
        pitch_range = np.max(pitch_values_voiced) - np.min(pitch_values_voiced)
    elif len(pitch_values_voiced) == 1:
        pitch_range = 0.0 # Or consider it undefined/NaN
        # pitch_std is 0 by default

    # Jitter and Shimmer
    # Praat's default arguments for jitter/shimmer might need tuning.
    # Using common defaults here.
    # Ensure the sound segment is long enough for these measures.
    # Praat might error on very short segments.
    min_duration_for_jitter_shimmer = 0.1 # seconds, example threshold
    jitter = 0.0
    shimmer = 0.0

    if snd.get_total_duration() >= min_duration_for_jitter_shimmer:
        try:
            jitter = call(snd, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3) # Adjusted defaults
            shimmer = call(snd, "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6) # Adjusted defaults
        except Exception as e:
            # print(f"Could not calculate jitter/shimmer: {e}") # Or log this
            pass # Keep default 0.0

    # Intensity-based pause analysis
    intensity = snd.to_intensity()
    total_duration = snd.get_total_duration()
    pause_durations = []
    
    # Threshold might need to be dynamic or calibrated. Using a common default.
    # This simple thresholding might not be robust for all environments.
    intensity_threshold_db = intensity.get_minimum() + 10 # Example: 10dB above minimum intensity
    # Or a fixed threshold if you have a calibrated environment:
    # intensity_threshold_db = -40.0 # dB, relative to max possible intensity (0dB)

    if intensity.get_number_of_frames() > 0:
        in_pause = False
        pause_start_time = 0.0
        for i in range(intensity.get_number_of_frames()):
            current_time = intensity.get_time_from_frame_number(i + 1)
            current_intensity_val = intensity.get_value_in_frame(i + 1)
            
            if current_intensity_val < intensity_threshold_db:
                if not in_pause:
                    in_pause = True
                    pause_start_time = current_time
            else:
                if in_pause:
                    in_pause = False
                    pause_durations.append(current_time - pause_start_time)
        if in_pause: # If ends in pause
            pause_durations.append(total_duration - pause_start_time)

    pause_duration_total = sum(pause_durations)
    
    loudness_variability = 0.0
    if intensity.get_number_of_frames() > 0 and len(intensity.values.flatten()) > 1:
         loudness_variability = np.std(intensity.values.flatten())


    return {
        "pitch_jitter": jitter if isinstance(jitter, float) else 0.0,
        "pitch_shimmer": shimmer if isinstance(shimmer, float) else 0.0,
        "pitch_range": pitch_range,
        "pitch_std": pitch_std,
        "pause_duration": pause_duration_total,
        "loudness_variability": loudness_variability
    }

def extract_linguistic_features_from_data(audio_data: bytes, sample_rate: int) -> Dict[str, Any]:
    """Extracts linguistic features from in-memory audio data using Whisper."""
    # Whisper expects a file path or a NumPy array.
    # Convert bytes to NumPy array (float32 for Whisper)
    
    # Assuming audio_data is raw PCM (e.g. int16)
    # Convert to float32, normalized
    numpy_array_int16 = np.frombuffer(audio_data, dtype=np.int16)
    numpy_array_float32 = numpy_array_int16.astype(np.float32) / 32768.0

    # Transcribe
    # Whisper's transcribe function can take a numpy array directly.
    # It expects a mono float32 NumPy array.
    if numpy_array_float32.ndim > 1 and numpy_array_float32.shape[1] > 1: # If stereo
        numpy_array_float32 = np.mean(numpy_array_float32, axis=1) # Convert to mono by averaging channels

    result = whisper_model.transcribe(numpy_array_float32, sample_rate=sample_rate, word_timestamps=True)
    text = result.get('text', "")
    
    word_count = 0
    sent_count = 0
    pronouns = 0
    articles = 0
    duration = 1.0 # Default duration to avoid division by zero

    if text:
        doc = nlp(text)
        pronouns = sum(1 for token in doc if token.pos_ == 'PRON')
        articles = sum(1 for token in doc if token.pos_ == 'DET')
        word_count = len([token for token in doc if token.is_alpha])
        sent_count = len(list(doc.sents))

    # Calculate duration from word timestamps if available and reliable
    # The 'duration' from whisper result['segments'] might be more accurate if transcription is good.
    if result.get('segments'):
        try:
            # Ensure segments have 'end' times
            valid_segments = [seg for seg in result['segments'] if 'end' in seg]
            if valid_segments:
                duration = valid_segments[-1]['end']
                if duration == 0: # If last segment end is 0, try to get from overall result
                    if 'duration' in result and result['duration'] > 0:
                         duration = result['duration']
                    elif len(numpy_array_float32) > 0 and sample_rate > 0:
                         duration = len(numpy_array_float32) / sample_rate
                    else:
                         duration = 1.0 # Fallback
            elif len(numpy_array_float32) > 0 and sample_rate > 0: # Fallback to audio data length
                duration = len(numpy_array_float32) / sample_rate
            else: # Absolute fallback
                duration = 1.0
        except (IndexError, KeyError, TypeError):
            if len(numpy_array_float32) > 0 and sample_rate > 0: # Fallback to audio data length
                duration = len(numpy_array_float32) / sample_rate
            else: # Absolute fallback
                duration = 1.0
    elif len(numpy_array_float32) > 0 and sample_rate > 0: # Fallback if no segments
         duration = len(numpy_array_float32) / sample_rate


    return {
        "pronoun_ratio": pronouns / word_count if word_count > 0 else 0.0,
        "article_usage": articles / word_count if word_count > 0 else 0.0,
        "speech_rate": word_count / duration if duration > 0 else 0.0,
        "sentence_length_avg": word_count / sent_count if sent_count > 0 else 0.0,
        "transcript_segment": text # Include the transcribed text segment
    }

def extract_features_from_data(audio_data: bytes, sample_rate: int, channels: int) -> Dict[str, Any]:
    """Extracts features from in-memory audio data."""
    acoustic = extract_acoustic_features_from_data(audio_data, sample_rate, channels)
    linguistic = extract_linguistic_features_from_data(audio_data, sample_rate) # Whisper handles mono
    return {**acoustic, **linguistic}


# --- Original functions that take audio_path (can be kept for batch processing or testing) ---
def extract_acoustic_features(audio_path: str) -> Dict[str, Any]:
    snd = parselmouth.Sound(audio_path)
    pitch = snd.to_pitch()
    point_process = snd.to_point_process_cc()

    # Pitch-related features
    pitch_values = pitch.selected_array['frequency']
    pitch_values = pitch_values[pitch_values != 0]  # remove unvoiced
    pitch_std = np.std(pitch_values)
    pitch_range = np.max(pitch_values) - np.min(pitch_values)

    jitter = call(snd, "Get jitter (local)", 0, 0.02, 1.3, 1.6)
    shimmer = call(snd, "Get shimmer (local)", 0, 0.02, 1.3, 1.6, 0.03, 0.45)

    # Intensity-based pause analysis
    intensity = snd.to_intensity()
    total_duration = snd.get_total_duration()
    pause_durations = []
    threshold = 50.0  # dB
    frame_len = intensity.get_frame_count()
    frame_duration = total_duration / frame_len

    in_pause = False
    pause_start = 0.0
    for i in range(frame_len):
        time = intensity.xs()[i]
        val = intensity.values[0][i]
        if val < threshold:
            if not in_pause:
                in_pause = True
                pause_start = time
        else:
            if in_pause:
                in_pause = False
                pause_durations.append(time - pause_start)

    pause_duration = sum(pause_durations)

    return {
        "pitch_jitter": jitter,
        "pitch_shimmer": shimmer,
        "pitch_range": pitch_range,
        "pitch_std": pitch_std,
        "pause_duration": pause_duration,
        "loudness_variability": np.std(intensity.values[0])
    }

def extract_linguistic_features(audio_path: str) -> Dict[str, Any]:
    result = whisper_model.transcribe(audio_path, word_timestamps=True)
    text = result['text']
    words = [w for w in result['segments'] if w.get('text')]

    doc = nlp(text)
    pronouns = sum(1 for token in doc if token.pos_ == 'PRON')
    articles = sum(1 for token in doc if token.pos_ == 'DET')
    word_count = len([token for token in doc if token.is_alpha])
    sent_count = len(list(doc.sents))

    duration = result['segments'][-1]['end'] if result['segments'] else 1.0

    return {
        "pronoun_ratio": pronouns / word_count if word_count else 0.0,
        "article_usage": articles / word_count if word_count else 0.0,
        "speech_rate": word_count / duration if duration > 0 else 0.0,
        "sentence_length_avg": word_count / sent_count if sent_count else 0.0
    }

def extract_features(audio_path: str) -> Dict[str, Any]:
    acoustic = extract_acoustic_features(audio_path)
    linguistic = extract_linguistic_features(audio_path)
    return {**acoustic, **linguistic}


# Helper
from parselmouth.praat import call
