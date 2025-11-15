from backend.models import AudioAnalysis
import json
from typing import Optional, Dict, Any, TYPE_CHECKING

# Use TYPE_CHECKING to avoid circular import while keeping type hints
if TYPE_CHECKING:
    from backend.services.gemini_service import GeminiService

class AudioAnalysisService:
    def __init__(self, gemini_service: Optional["GeminiService"] = None):
        if gemini_service is None:
            # Import here to avoid circular import at module level
            from backend.services.gemini_service import GeminiService
            gemini_service = GeminiService()
        self.gemini_service = gemini_service

    async def analyze(self, transcript: str, audio_file_path: Optional[str] = None, audio_duration_seconds: Optional[float] = None, session_context: Optional[Dict[str, Any]] = None) -> AudioAnalysis:
        # If only transcript is available, we might have limited audio analysis.
        # The prompt will guide the LLM to use audio if referenced, otherwise infer from text.

        # Constructing a context string for the prompt
        audio_context_parts = []
        if audio_file_path:
            audio_context_parts.append(f"An audio file is associated with this transcript at path: {audio_file_path}.")
        if audio_duration_seconds:
            audio_context_parts.append(f"The duration of this audio is {audio_duration_seconds:.2f} seconds.")
        
        audio_info_for_prompt = " ".join(audio_context_parts)
        if not audio_info_for_prompt:
            audio_info_for_prompt = "No direct audio file path or duration provided; infer from transcript where possible."

        prompt = f'''Analyze the provided transcript and associated audio information (if any) to assess audio characteristics.
You are a multimodal AI capable of analyzing audio if audio data is made available to you alongside this prompt.

Transcript:
"{transcript if transcript else "Transcript not available."}"

Audio Information:
{audio_info_for_prompt}

Session Context (if available, use for nuanced understanding):
{json.dumps(session_context) if session_context else "No additional session context provided."}

Based on the transcript and, more importantly, THE AUDIO DATA if available to you, provide your analysis as a JSON object matching the AudioAnalysis model fields below.
If audio data is not available for a specific metric, clearly state that the analysis is an inference from text.

1.  speech_clarity_score (float, 0.0 to 1.0): Assess from audio. If audio unavailable, infer from text coherence.
2.  speech_clarity_analysis (str): Explain the speech clarity assessment based on audio (e.g., articulation, mumbling) or text.
3.  background_noise_assessment (str, e.g., "Low", "Medium", "High"): Assess from audio. If audio unavailable, infer from textual cues or assume "Low" if no cues.
4.  background_noise_analysis (str): Detail background noise characteristics from audio (e.g., type of noise, impact) or textual inference.
5.  average_speech_rate_wpm (int): Calculate from transcript word count and 'audio_duration_seconds' if provided. If duration unknown, estimate from text or state as not calculable.
6.  speech_rate_variability_analysis (str): From audio, analyze speech rate consistency. If audio unavailable, infer from text patterns (e.g., rushed passages, long pauses implied).
7.  intonation_patterns_analysis (str): From audio, describe intonation (monotonous, expressive). If audio unavailable, infer from text (punctuation, emotional language).
8.  overall_audio_quality_assessment (str): Overall qualitative assessment of audio technical quality from audio. If audio unavailable, infer based on other textual inferences.
9.  audio_duration_seconds (Optional[float]): Use the provided 'audio_duration_seconds' or state if derived/unavailable.
10. loudness_dbfs (Optional[float]): Assess average loudness from audio. Null if audio unavailable.
11. loudness_analysis (str): Analyze audio volume levels from audio. If audio unavailable, "Analysis not available."
12. signal_to_noise_ratio_db (Optional[float]): Estimate SNR from audio. Null if audio unavailable.
13. signal_to_noise_ratio_analysis (str): Explain SNR and its impact from audio. If audio unavailable, "Analysis not available."
14. pitch_profile_analysis (str): Analyze pitch characteristics from audio. If audio unavailable, "Analysis not available."
15. voice_timbre_description (str): Describe voice timbre from audio. If audio unavailable, "Analysis not available."
16. vocal_effort_assessment (str): Assess vocal effort from audio. If audio unavailable, "Analysis not available."
17. acoustic_event_detection (List[str]): Detect non-speech acoustic events from audio (e.g., cough, door slam). Empty list if audio unavailable or no events.
18. acoustic_event_analysis (str): Analyze detected acoustic events from audio. If audio unavailable, "Analysis not available."
19. pause_characteristics_analysis (str): Analyze pause frequency/duration from audio (silence detection). If audio unavailable, infer from textual markers like "..." or implied pauses.
20. vocal_stress_indicators_acoustic (List[str]): Identify vocal stress indicators from audio (pitch breaks, tremors). Empty list if audio unavailable.
21. vocal_stress_indicators_acoustic_analysis (str): Explain acoustically identified vocal stress indicators from audio. If audio unavailable, "Analysis not available."

JSON structure to be returned:
{{
  "speech_clarity_score": float,
  "speech_clarity_analysis": "...",
  "background_noise_assessment": "...",
  "background_noise_analysis": "...",
  "average_speech_rate_wpm": int,
  "speech_rate_variability_analysis": "...",
  "intonation_patterns_analysis": "...",
  "overall_audio_quality_assessment": "...",
  "audio_duration_seconds": float_or_null,
  "loudness_dbfs": float_or_null,
  "loudness_analysis": "...",
  "signal_to_noise_ratio_db": float_or_null,
  "signal_to_noise_ratio_analysis": "...",
  "pitch_profile_analysis": "...",
  "voice_timbre_description": "...",
  "vocal_effort_assessment": "...",
  "acoustic_event_detection": [],
  "acoustic_event_analysis": "...",
  "pause_characteristics_analysis": "...",
  "vocal_stress_indicators_acoustic": [],
  "vocal_stress_indicators_acoustic_analysis": "..."
}}
Prioritize analysis from actual audio data if available to you. If not, make reasonable inferences from the transcript. For analysis fields (e.g., *_analysis), clearly state the basis of your analysis (audio or text).
'''
        
        try:
            raw_analysis_json = await self.gemini_service.query_gemini_for_raw_json(prompt)
            
            if raw_analysis_json:
                analysis_data = json.loads(raw_analysis_json)
                
                # Ensure audio_duration_seconds from input is preserved if not in LLM response or if LLM should not override
                if audio_duration_seconds is not None and "audio_duration_seconds" not in analysis_data:
                    analysis_data["audio_duration_seconds"] = audio_duration_seconds
                
                # Calculate WPM if possible and not provided by LLM, or to verify
                calculated_wpm = analysis_data.get("average_speech_rate_wpm")
                if transcript and audio_duration_seconds and audio_duration_seconds > 0:
                    word_count = len(transcript.split())
                    minutes = audio_duration_seconds / 60.0
                    if minutes > 0:
                        wpm_from_data = int(word_count / minutes)
                        # If LLM didn't provide WPM, or if you prefer to always use calculated WPM:
                        if calculated_wpm is None or calculated_wpm == 0: # Or some other condition to override
                           analysis_data["average_speech_rate_wpm"] = wpm_from_data
                elif calculated_wpm is None: # If no way to calculate and LLM didn't provide
                     analysis_data["average_speech_rate_wpm"] = 0


                return AudioAnalysis(**analysis_data)
            else:
                return self._fallback_text_analysis(transcript, audio_duration_seconds)
        except Exception as e:
            print(f"Error during LLM audio analysis: {e}")
            return self._fallback_text_analysis(transcript, audio_duration_seconds)

    def _fallback_text_analysis(self, text: str, audio_duration_seconds: Optional[float] = None) -> AudioAnalysis:
        # This fallback is purely text-based and very basic.
        # It won't populate most of the new audio-centric fields.
        wpm = 0
        if text and audio_duration_seconds and audio_duration_seconds > 0:
            word_count = len(text.split())
            minutes = audio_duration_seconds / 60.0
            if minutes > 0:
                wpm = int(word_count / minutes)
        
        clarity_score = 0.5 if text else 0.0
        quality_assessment = "Fair (text-based fallback)" if text else "Poor (no text)"

        return AudioAnalysis(
            speech_clarity_score=clarity_score,
            speech_clarity_analysis="Fallback: Inferred from text presence.",
            background_noise_assessment="Low (fallback assumption)",
            background_noise_analysis="Fallback: No specific background noise analysis from text.",
            average_speech_rate_wpm=wpm,
            speech_rate_variability_analysis="Fallback: Not analyzed from text.",
            intonation_patterns_analysis="Fallback: Not analyzed from text.",
            overall_audio_quality_assessment=quality_assessment,
            audio_duration_seconds=audio_duration_seconds,
            # Most other fields will use their defaults (None, "Analysis not available", [])
            # as they are hard to infer meaningfully from just text in a simple fallback.
            loudness_analysis="Fallback: Analysis not available.",
            signal_to_noise_ratio_analysis="Fallback: Analysis not available.",
            pitch_profile_analysis="Fallback: Analysis not available.",
            voice_timbre_description="Fallback: Analysis not available.",
            vocal_effort_assessment="Fallback: Analysis not available.",
            acoustic_event_analysis="Fallback: Analysis not available.",
            pause_characteristics_analysis="Fallback: Inferred from text if possible, otherwise not available.",
            vocal_stress_indicators_acoustic_analysis="Fallback: Analysis not available."
        )
