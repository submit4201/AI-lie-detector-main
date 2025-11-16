# layer2_feature_extraction.py

import parselmouth
import numpy as np
import spacy
from typing import Dict, Any, List
from faster_whisper import WhisperModel
from parselmouth.praat import call

model_size = "tiny"

# Initialize the WhisperModel (using faster_whisper)
# Run on GPU with FP16
# model = WhisperModel(model_size, device="cuda", compute_type="float16")
# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
model = WhisperModel(model_size, device="cpu", compute_type="int8")  # Defaulting to CPU

nlp = spacy.load("en_core_web_sm")


def calculate_pause_metrics(intensity, snd, threshold=50.0):
    """Calculate pause-related metrics from intensity and sound objects."""
    pause_durations = []
    frame_len = intensity.get_frame_count()

    in_pause = False
    pause_start = 0.0
    pause_duration_total = 0.0
    pause_count = 0

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
                pause_count += 1
                pause_duration_total += time - pause_start

    if in_pause:  # If ends in pause
        pause_duration_total += snd.get_total_duration() - pause_start
        pause_count += 1

    return pause_duration_total, pause_count


def transcribe_audio_with_timestamps(mono_audio_data_np: np.ndarray) -> List[Dict[str, Any]]:
    """Transcribe audio data (mono float32 NumPy array) and return word-level timestamps."""
    transcription_seg_with_timestamps = []
    # Assuming mono_audio_data_np is a float32 NumPy array, which faster-whisper expects.
    # Whisper models are typically trained on 16kHz audio. Resampling might be needed if input SR differs.
    segments, info = model.transcribe(mono_audio_data_np, word_timestamps=True, beam_size=5)
    # Optional: log language info
    # logger.info(f"Detected language '{info.language}' with probability {info.language_probability}")

    for segment in segments:
        for word in segment.words:
            word_data = {
                "start": word.start,
                "end": word.end,
                "text": word.word
            }
            transcription_seg_with_timestamps.append(word_data)
            # print("[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word)) # Keep for debugging if needed

    return transcription_seg_with_timestamps


def extract_acoustic_features_from_data(audio_data: bytes, sample_rate: int, channels: int) -> Dict[str, Any]:
    """Extracts acoustic features from in-memory audio data."""
    # Convert bytes to NumPy array
    numpy_array = np.frombuffer(audio_data, dtype=np.int16)
    numpy_array_float = numpy_array.astype(np.float64) / 32767.0

    if channels > 1:
        # Assuming interleaved audio, take the first channel for parselmouth analysis
        # More sophisticated channel handling might be needed depending on requirements
        numpy_array_float = numpy_array_float[::channels]

    snd = parselmouth.Sound(numpy_array_float, sampling_frequency=sample_rate)

    intensity = snd.to_intensity()
    pitch = snd.to_pitch()
    formant = snd.to_formant()
    point_process = snd.to_point_process_cc()  # For jitter/shimmer
    hnr = snd.to_harmonics_to_noise_ratio()
    loudness = snd.to_loudness()
    energy = snd.to_energy()
    # Intensity-based pause analysis
    pause_duration_total, pause_count = calculate_pause_metrics(intensity, snd)

    # Pitch-related features
    pitch_values = pitch.selected_array['frequency']
    pitch_values_voiced = pitch_values[pitch_values != 0]  # remove unvoiced

    pitch_std = 0.0
    pitch_range = 0.0
    if len(pitch_values_voiced) > 1:  # Need at least 2 voiced points for std/range
        pitch_std = np.std(pitch_values_voiced)
        pitch_range = np.max(pitch_values_voiced) - np.min(pitch_values_voiced)
    elif len(pitch_values_voiced) == 1:
        pitch_range = 0.0  # Or consider it undefined/NaN
        # pitch_std is 0 by default
    # Formant features
    formant_values = formant.selected_array['frequency']
    formant_std = np.std(formant_values)
    formant_range = np.max(formant_values) - np.min(formant_values)

    # HNR features
    hnr_values = hnr.selected_array['hnr']
    hnr_std = np.std(hnr_values)
    hnr_range = np.max(hnr_values) - np.min(hnr_values)

    # Loudness features
    loudness_values = loudness.selected_array['loudness']
    loudness_std = np.std(loudness_values)
    loudness_range = np.max(loudness_values) - np.min(loudness_values)

    # Energy features
    energy_values = energy.selected_array['energy']
    energy_std = np.std(energy_values)
    energy_range = np.max(energy_values) - np.min(energy_values)

    # Intensity features
    intensity_values = intensity.selected_array['intensity']
    intensity_std = np.std(intensity_values)
    intensity_range = np.max(intensity_values) - np.min(intensity_values)

    # Point process features
    point_process_values = point_process.selected_array['point_process']
    point_process_std = np.std(point_process_values)
    point_process_range = np.max(point_process_values) - np.min(point_process_values)

    # Jitter and Shimmer (Single corrected block)
    # Praat's default arguments for jitter/shimmer might need tuning.
    # Using common defaults here.
    # Ensure the sound segment is long enough for these measures.
    # Praat might error on very short segments.
    min_duration_for_jitter_shimmer = 0.1  # seconds, example threshold
    jitter = 0.0
    shimmer = 0.0

    if snd.get_total_duration() >= min_duration_for_jitter_shimmer:
        try:
            jitter = call(snd, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
            shimmer = call(snd, "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        except Exception as e:
            # print(f"Could not calculate jitter/shimmer: {e}") # Or log this
            pass  # Keep default 0.0

    # Loudness variability
    loudness_variability = 0.0
    if intensity.get_number_of_frames() > 0 and len(intensity.values.flatten()) > 1:
        loudness_variability = np.std(intensity.values.flatten())

    # Intensity-based pause analysis (already calculated, ensure correct values are used)
    # The print statements for pause metrics can be removed or kept for debugging.
    # print("Pause duration: ", pause_duration_total)
    # print("Pause count: ", pause_count)

    return {
        "pitch_jitter": jitter if isinstance(jitter, float) else 0.0,
        "pitch_shimmer": shimmer if isinstance(shimmer, float) else 0.0,
        "pitch_range": pitch_range,
        "pitch_std": pitch_std,
        "pause_duration": pause_duration_total,
        "pause_count": pause_count,
        "loudness_variability": loudness_variability,
        "formant_range": formant_range,
        "formant_std": formant_std,
        "hnr_range": hnr_range,
        "hnr_std": hnr_std,
        "loudness_range": loudness_range,
        "loudness_std": loudness_std,
        "energy_range": energy_range,
        "energy_std": energy_std,
        "intensity_range": intensity_range,
        "intensity_std": intensity_std,
        "point_process_range": point_process_range,
        "point_process_std": point_process_std,
        # Removed: "transcript_segment": TRANSCRIPTION_SEG_WITH_TIMESTAMPS
    }


def extract_linguistic_features_from_data(audio_data: bytes, sample_rate: int, channels: int, start_time: float, end_time: float, transcription_seg_with_timestamps: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Extracts linguistic features from in-memory audio data using Whisper."""

    if not transcription_seg_with_timestamps:
        # Convert audio_data bytes to mono float32 NumPy array for transcription
        numpy_array_int16 = np.frombuffer(audio_data, dtype=np.int16)
        numpy_array_float32 = numpy_array_int16.astype(np.float32) / 32768.0

        mono_audio_for_transcription: np.ndarray
        if channels > 1:
            # Assuming interleaved audio data if multi-channel
            # Reshape to (num_samples, num_channels) and then take the mean across channels
            try:
                reshaped_array = numpy_array_float32.reshape(-1, channels)
                mono_audio_for_transcription = np.mean(reshaped_array, axis=1)
            except ValueError as e:
                # Fallback or error handling if reshape fails (e.g. not perfectly divisible)
                # For now, just take the first channel if reshape fails and it's 1D already from a bad previous step
                # This part might need more robust handling based on expected audio_data structure
                if numpy_array_float32.ndim == 1:  # If it's already 1D, assume it's mono or take as is
                    mono_audio_for_transcription = numpy_array_float32
                else:  # if still multi-channel but not reshapeable, this is an issue
                    raise ValueError(f"Cannot convert multi-channel audio to mono for transcription. Shape: {numpy_array_float32.shape}, Channels: {channels}. Error: {e}")

        else:  # Mono
            mono_audio_for_transcription = numpy_array_float32

        transcription_seg_with_timestamps = transcribe_audio_with_timestamps(mono_audio_for_transcription)

    text = ""
    nouns = []
    verbs = []
    adjectives = []
    adverbs = []

    for segment in transcription_seg_with_timestamps:
        if segment['start'] >= start_time and segment['end'] <= end_time:
            text += segment['text'] + " "
            doc = nlp(segment['text'])
            for token in doc:
                if token.pos_ == 'NOUN':
                    nouns.append(token.text)
                elif token.pos_ == 'VERB':
                    verbs.append(token.text)
                elif token.pos_ == 'ADJ':
                    adjectives.append(token.text)
                elif token.pos_ == 'ADV':
                    adverbs.append(token.text)
    word_count = 0
    sent_count = 0
    pronouns = 0
    articles = 0
    duration = end_time - start_time
    if duration <= 0:  # Avoid division by zero if start_time and end_time are problematic
        duration = 1.0  # Default to 1 second if duration is zero or negative
        # logger.warning("Audio segment duration is zero or negative, defaulting to 1.0s for rate calculations.")

    for segment in transcription_seg_with_timestamps:
        if segment['start'] >= start_time and segment['end'] <= end_time:
            word_count += 1
            sent_count += 1
            if text:
                doc = nlp(text)
                pronouns = sum(1 for token in doc if token.pos_ == 'PRON')
                articles = sum(1 for token in doc if token.pos_ == 'DET')
                word_count = len([token for token in doc if token.is_alpha])
                sent_count = len(list(doc.sents))

    return {
        "pronoun_ratio": pronouns / word_count if word_count > 0 else 0.0,
        "article_usage": articles / word_count if word_count > 0 else 0.0,
        "speech_rate": word_count / duration if duration > 0 else 0.0,  # Ensure duration > 0
        "sentence_length_avg": word_count / sent_count if sent_count > 0 else 0.0,
        "transcript_segment": text.strip(),  # Include the transcribed text segment, strip trailing space
        "nouns": nouns,
        "verbs": verbs,
        "adjectives": adjectives,
        "adverbs": adverbs
        # TODO: Add more linguistic features here
        # TODO: Add part of speech tagging
        # TODO: Add named entity recognition
        # TODO: Add sentiment analysis
        # TODO: Add emotion analysis
        # TODO: Add topic modeling
        # TODO: Add more complex analysis like syntax parsing, dependency parsing, etc.
    }


def extract_features_from_data(audio_data: bytes, sample_rate: int, channels: int) -> Dict[str, Any]:
    """Extracts features from in-memory audio data."""
    acoustic = extract_acoustic_features_from_data(audio_data, sample_rate, channels)

    # Prepare audio data for transcription (mono float32 numpy array)
    numpy_array_int16 = np.frombuffer(audio_data, dtype=np.int16)
    numpy_array_float32 = numpy_array_int16.astype(np.float32) / 32768.0  # Normalize to [-1.0, 1.0]

    mono_audio_data_np: np.ndarray
    if channels > 1:
        # Assuming interleaved audio data if multi-channel
        # Reshape to (num_samples, num_channels) and then take the mean across channels
        try:
            reshaped_array = numpy_array_float32.reshape(-1, channels)
            mono_audio_data_np = np.mean(reshaped_array, axis=1)
        except ValueError:  # Fallback if reshape fails (e.g. not perfectly divisible)
            # This logic should be robust. For now, if it's 1D, assume it was meant to be mono.
            if numpy_array_float32.ndim == 1:
                mono_audio_data_np = numpy_array_float32
            else:  # if still multi-channel but not reshapeable, this is an issue
                # Or, could attempt to take the first channel: mono_audio_data_np = reshaped_array[:, 0]
                # For simplicity, raising an error or logging a warning might be better here.
                # For now, let's assume it can be processed or was already mono.
                # This matches the logic in extract_linguistic_features_from_data if transcription is done there.
                # A consistent way to get mono float32 from (audio_data, channels) is needed.
                if numpy_array_float32.ndim == 1:  # Already mono or error in channel info
                    mono_audio_data_np = numpy_array_float32
                else:  # Attempt to average channels
                    mono_audio_data_np = np.mean(numpy_array_float32.reshape(-1, channels), axis=1)

    else:  # Mono
        mono_audio_data_np = numpy_array_float32

    transcription_results = transcribe_audio_with_timestamps(mono_audio_data_np)

    # Calculate duration for linguistic features
    # Number of samples in the mono array / sample_rate
    num_samples_mono = len(mono_audio_data_np)
    duration_seconds = num_samples_mono / sample_rate if sample_rate > 0 else 0.0

    # Call linguistic feature extraction
    linguistic = extract_linguistic_features_from_data(
        audio_data,  # Original bytes
        sample_rate,
        channels,  # Original channels; linguistic_features will handle mono conversion if it re-transcribes
        start_time=0.0,
        end_time=duration_seconds,
        transcription_seg_with_timestamps=transcription_results
    )

    return {**acoustic, **linguistic}
