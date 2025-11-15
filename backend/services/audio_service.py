import base64
import os
from pydub import AudioSegment
from typing import List, Dict, Any
import logging

# Remove speech recognition dependency and use Gemini directly
# from services.gemini_service import transcribe_and_analyze_with_gemini  # Remove unused import

logger = logging.getLogger(__name__)

# Import sanitization function for secure logging
from backend.services.logging_utils import sanitize_for_logging as _sanitize_for_logging

def assess_audio_quality(audio_segment: AudioSegment) -> Dict[str, Any]:
    """Assess the quality of the audio for better analysis"""
    quality_metrics = {
        "duration": len(audio_segment) / 1000.0,  # seconds
        "sample_rate": audio_segment.frame_rate,
        "channels": audio_segment.channels,
        "loudness": audio_segment.dBFS,
        "quality_score": 0
    }

    # Calculate quality score
    if quality_metrics["duration"] >= 1.0:  # At least 1 second
        quality_metrics["quality_score"] += 25
    if quality_metrics["sample_rate"] >= 16000:  # Good sample rate
        quality_metrics["quality_score"] += 25
    if quality_metrics["loudness"] > -30:  # Not too quiet
        quality_metrics["quality_score"] += 25
    if quality_metrics["channels"] >= 1:  # Has audio channels
        quality_metrics["quality_score"] += 25

    return quality_metrics

# other audio processing functions can be added here

def convert_audio_to_wav(audio_path: str) -> str:
    """Convert audio to WAV format for consistency"""
    audio_segment = AudioSegment.from_file(audio_path)
    wav_path = audio_path.replace('.wav', '_converted.wav')
    audio_segment.export(wav_path, format="wav")
    return wav_path

# transcribe_audio, analyze_emotion, and analyze_emotion_with_gemini are removed
# as they are now handled directly by Gemini so their in the gemini_service.py

async def streaming_audio_analysis_pipeline(audio_path: str, session_id: str = None) -> Dict[str, Any]:
    """
    Audio-first streaming analysis pipeline that sends results as they complete.
    Always uses Gemini with audio data for comprehensive analysis.
    """
    try:
        from .streaming_service import analysis_streamer
        from .gemini_service import transcribe_with_gemini, query_gemini_with_audio, analyze_emotions_with_gemini
        from .linguistic_service import linguistic_analysis_pipeline
        
        # Convert audio to WAV for consistency
        wav_path = convert_audio_to_wav(audio_path)
        
        # Assess audio quality first
        audio_segment = AudioSegment.from_file(wav_path)
        audio_quality = assess_audio_quality(audio_segment)
        
        if session_id:
            await analysis_streamer.send_analysis_update(session_id, "audio_quality", audio_quality)
            await analysis_streamer.send_progress_update(session_id, "Audio Quality Assessment", 1, 5)
        
        # Step 1: Transcription with Gemini (audio-based)
        logger.info("Starting audio transcription with Gemini")
        transcript = transcribe_with_gemini(wav_path)
        logger.info(f"Transcription completed: {_sanitize_for_logging(transcript)}")
        
        if session_id:
            await analysis_streamer.send_analysis_update(session_id, "transcript", {"transcript": transcript})
            await analysis_streamer.send_progress_update(session_id, "Audio Transcription", 2, 5)
        
        # Step 2: Comprehensive Gemini audio analysis
        logger.info("Starting comprehensive Gemini audio analysis")
        gemini_result = query_gemini_with_audio(wav_path, transcript, {}, None)
        logger.info("Gemini audio analysis completed")
        
        if session_id:
            await analysis_streamer.send_analysis_update(session_id, "gemini_analysis", gemini_result)
            await analysis_streamer.send_progress_update(session_id, "Gemini Audio Analysis", 3, 5)
        
        # Step 3: Emotion analysis with audio
        logger.info("Starting emotion analysis with audio")
        emotions = analyze_emotions_with_gemini(wav_path, transcript)
        logger.info(f"Emotion analysis completed: {len(emotions)} emotions detected")
        
        if session_id:
            await analysis_streamer.send_analysis_update(session_id, "emotion_analysis", emotions)
            await analysis_streamer.send_progress_update(session_id, "Emotion Analysis", 4, 5)
        
        # Step 4: Linguistic analysis (based on transcript)
        logger.info("Starting linguistic analysis")
        linguistic_analysis = linguistic_analysis_pipeline(transcript, audio_quality.get('duration', 30.0))
        logger.info("Linguistic analysis completed")
        
        if session_id:
            await analysis_streamer.send_analysis_update(session_id, "linguistic_analysis", linguistic_analysis)
            await analysis_streamer.send_progress_update(session_id, "Linguistic Analysis", 5, 5)
        
        # Combine all results
        final_result = {
            "transcript": transcript,
            "audio_quality": audio_quality,
            "emotion_analysis": emotions,
            "linguistic_analysis": linguistic_analysis,
            **gemini_result  # Include all Gemini analysis results
        }
        
        logger.info("Audio analysis pipeline completed successfully")
        return final_result
        
    except Exception as e:
        logger.error(f"Exception in streaming audio analysis pipeline: {str(e)}", exc_info=True)
        if session_id:
            await analysis_streamer.send_error(session_id, f"Audio analysis error: {str(e)}")
        raise Exception(f"Audio analysis pipeline error: {str(e)}")

def audio_analysis_pipeline(audio_path: str) -> Dict[str, Any]:
    """
    Synchronous wrapper for the streaming audio analysis pipeline.
    Maintains backward compatibility while using audio-first approach.
    """
    try:
        # Run the async pipeline synchronously
        import asyncio
        return asyncio.run(streaming_audio_analysis_pipeline(audio_path, None))
    except Exception as e:
        logger.error(f"Exception in audio analysis pipeline: {str(e)}", exc_info=True)
        raise Exception(f"Audio analysis pipeline error: {str(e)}")
   