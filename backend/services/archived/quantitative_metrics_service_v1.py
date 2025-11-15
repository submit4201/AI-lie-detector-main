"""Archived QuantitativeMetricsService v1 implementation.

This copy preserves the original FastAPI v1 service logic for reference
while the active codebase migrates to backend.services.v2_services.
Do not import this module from production code.
"""

try:
    from backend.main_backup import ErrorResponse
except Exception:
    # Avoid importing heavy or optional deps during unit tests (e.g., speech_recognition).
    class ErrorResponse(Exception):
        def __init__(self, message: str = "", status_code: int = 400, **kwargs):
            super().__init__(message)
            self.message = message
            self.status_code = status_code
from backend.models import InteractionMetrics, NumericalLinguisticMetrics # Updated model name
from typing import List, Dict, Optional, Any, TYPE_CHECKING
from backend.services.v2.analysis_protocol import AnalysisService
import json
import re

# Use TYPE_CHECKING to avoid circular import while keeping type hints
if TYPE_CHECKING:
    from backend.services.gemini_service import GeminiService

from backend.services.v2.gemini_client import GeminiClientV2 as DefaultGeminiClient


class QuantitativeMetricsService(AnalysisService):
    serviceName = "quantitative_metrics"
    serviceVersion = "2.0"
    
    def __init__(self, gemini_client: Optional[Any] = None, transcript: str = "", audio_data: Optional[bytes] = None, meta: Optional[Dict[str, Any]] = None):
        # Accept any client that implements the v2 GeminiClient interface
        if gemini_client is None:
            try:
                gemini_client = DefaultGeminiClient()
            except RuntimeError:
                # SDK not installed, use a mock for testing
                class MockClient:
                    async def query_json(self, *args, **kwargs): 
                        return {"text": "mock response"}
                    async def transcribe(self, *args, **kwargs): 
                        return "mock transcript"
                    async def analyze_audio(self, *args, **kwargs): 
                        return {"text": "mock response"}
                gemini_client = MockClient()
                
        self.gemini_client = gemini_client
        super().__init__(transcript=transcript, audio_data=audio_data, meta=meta)
        self.NumericalLinguisticMetrics = None

    def _calculate_numerical_linguistic_metrics(self, text: str, audio_duration_seconds: Optional[float] = None) -> NumericalLinguisticMetrics:
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words)
        unique_word_count = len(set(words))
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        sentence_count = len(sentences)

        hesitation_markers = ["um", "uh", "er", "ah"]
        filler_words = ["like", "you know", "basically", "actually", "literally", "so", "well"]
        qualifiers = ["maybe", "perhaps", "might", "could", "possibly", "sort of", "kind of", "i guess", "i think"]
        certainty_indicators = ["definitely", "absolutely", "certainly", "surely", "clearly", "undoubtedly", "always", "never"]

        hesitation_marker_count = sum(words.count(marker) for marker in hesitation_markers)
        filler_word_count = sum(1 for word in words if word in filler_words) # Simplified for now, can be more nuanced
        # For multi-word fillers, a more complex regex might be needed if counting phrases
        # For now, this counts individual words if they are part of the list.
        # A more accurate count for phrases like "you know" would require text.count("you know")
        filler_word_count += text.lower().count("you know") # Example for a common phrase

        qualifier_count = sum(words.count(q) for q in qualifiers)
        qualifier_count += sum(text.lower().count(q_phrase) for q_phrase in ["sort of", "kind of", "i guess", "i think"])

        certainty_indicator_count = sum(words.count(ci) for ci in certainty_indicators)
        certainty_indicator_count += sum(text.lower().count(ci_phrase) for ci_phrase in []) # Add phrases if any

        # Repetition count (simple version: consecutive identical words)
        repetition_count = 0
        for i in range(len(words) - 1):
            if words[i] == words[i+1]:
                repetition_count += 1

        avg_word_length_chars = sum(len(word) for word in words) / word_count if word_count > 0 else 0.0
        avg_sentence_length_words = word_count / sentence_count if sentence_count > 0 else 0.0
        vocabulary_richness_ttr = unique_word_count / word_count if word_count > 0 else 0.0

        speech_rate_wpm = None
        hesitation_rate_hpm = None
        if audio_duration_seconds and audio_duration_seconds > 0:
            minutes = audio_duration_seconds / 60.0
            speech_rate_wpm = word_count / minutes if minutes > 0 else None
            hesitation_rate_hpm = hesitation_marker_count / minutes if minutes > 0 else None
        
        confidence_metric_ratio = None
        total_confidence_indicators = certainty_indicator_count + qualifier_count
        if total_confidence_indicators > 0:
            confidence_metric_ratio = certainty_indicator_count / total_confidence_indicators

        # Placeholder for calculated formality and complexity - requires more sophisticated algorithms
        formality_score_calculated = 50.0 # Default placeholder
        complexity_score_calculated = 50.0 # Default placeholder
        NumericalLinguisticMetrics(
            word_count=word_count,
            unique_word_count=unique_word_count,
            hesitation_marker_count=hesitation_marker_count,
            filler_word_count=filler_word_count,
            qualifier_count=qualifier_count,
            certainty_indicator_count=certainty_indicator_count,
            repetition_count=repetition_count,
            sentence_count=sentence_count,
            avg_word_length_chars=round(avg_word_length_chars, 2),
            avg_sentence_length_words=round(avg_sentence_length_words, 2),
            speech_rate_wpm=round(speech_rate_wpm, 1) if speech_rate_wpm is not None else None,
            hesitation_rate_hpm=round(hesitation_rate_hpm, 1) if hesitation_rate_hpm is not None else None,
            vocabulary_richness_ttr=round(vocabulary_richness_ttr, 3),
            confidence_metric_ratio=round(confidence_metric_ratio, 2) if confidence_metric_ratio is not None else None,
            formality_score_calculated=formality_score_calculated,
            complexity_score_calculated=complexity_score_calculated
        )
        self.NumericalLinguisticMetrics = NumericalLinguisticMetrics

        return self.NumericalLinguisticMetrics
    async def analyze_interaction_metrics(
        self, 
        text: str, 
        audio_data: Optional[bytes] = None,
        speaker_diarization: Optional[List[Dict[str, Any]]] = None, 
        sentiment_trend_data_input: Optional[List[Dict[str, Any]]] = None,
        audio_duration_seconds: Optional[float] = None
    ) -> InteractionMetrics:
        
        if not text and not speaker_diarization:
            raise ErrorResponse(
                message="Insufficient data for interaction metrics analysis: either transcript text or speaker diarization data must be provided.",
                status_code=400,
                details={},
                suggestion="Provide at least the transcript text or speaker diarization data to perform interaction metrics analysis.",
                user_friendly_message="Please provide the necessary data for analysis.",
                severity="warning",
                location="QuantitativeMetricsService.analyze_interaction_metrics",
                documentation_link="https://docs.example.com/errors#InsufficientDataForInteractionMetrics"
            )

        diarization_summary = "Speaker diarization not available or not provided for this analysis."
        if speaker_diarization:
            try:
                diarization_summary = f"Speaker diarization data: {json.dumps(speaker_diarization)}"
            except TypeError:
                diarization_summary = "Speaker diarization data provided but is not JSON serializable for the prompt."
        
        sentiment_summary = "Sentiment trend data not available or not provided."
        if sentiment_trend_data_input:
            try:
                sentiment_summary = f"Sentiment trend data: {json.dumps(sentiment_trend_data_input)}"
            except TypeError:
                sentiment_summary = "Sentiment trend data provided but is not JSON serializable for the prompt."

        prompt = f"""Analyze the following transcript and associated data to determine interaction metrics.
                            Transcript (may be partial or full, use for context if diarization is primary focus):
                            "{text if text else 'Transcript not provided for this specific analysis, rely on diarization and sentiment data.'}"

                            {diarization_summary}
                            {sentiment_summary}
                            Audio duration (if available): {audio_duration_seconds if audio_duration_seconds else 'Not provided'} seconds.

                            Based on the provided information, calculate or infer the following interaction metrics:
                            1.  Talk-to-Listen Ratio (Optional[float]): If multiple speakers are detailed in diarization, estimate this. This could be the ratio of the primary speaker's time to total time, or to other speakers' time. Specify context. If only one speaker or unclear, this may be null or not applicable.
                            2.  Speaker Turn Duration Average (Optional[float], in seconds): Average duration of speaker turns. If diarization is available, use it. Otherwise, this may be null.
                            3.  Interruptions Count (Optional[int]): Number of interruptions detected. This typically requires diarization providing overlap information or clear textual cues (e.g., "--"). If not inferable, this may be null.
                            4.  Sentiment Trend (List[Dict[str, Any]]): If sentiment_trend_data_input is provided, use it directly. Otherwise, if the transcript is substantial, you can try to infer a basic trend (e.g., positive start, negative end), or default to an empty list. Example: [{{"segment": "opening", "sentiment_score": 0.7, "sentiment_label": "positive"}}].

                            Provide your analysis as a JSON object matching the structure of the InteractionMetrics model:
                            {{
                            "talk_to_listen_ratio": float_or_null,
                            "speaker_turn_duration_avg_seconds": float_or_null,
                            "interruptions_count": int_or_null,
                            "sentiment_trend": [] 
                            }}
                            If specific details cannot be reliably inferred from the provided data, use null for optional fields or appropriate defaults like empty lists for sentiment_trend.
                            Focus on deriving these from speaker diarization and sentiment data primarily. The transcript is for context.
                            Ensure the output is valid JSON and can be parsed directly into the InteractionMetrics model.
                            """
        
        try:
            raw_analysis = await self.gemini_service.query_gemini_for_raw_json(prompt)
            if isinstance(raw_analysis, str):
                # log that this came back as a string
                print("LLM returned raw analysis as string.")
                # try and fix the string to be valid json or dict
                raw_text = raw_analysis.strip()
                if raw_text.startswith("'") and raw_text.endswith("'"):
                    raw_text = raw_text[1:-1]
                raw_text = raw_text.replace("'", '"') # crude replacement, may not always work
                # Attempt to parse again
                try:
                    parsed = json.loads(raw_text)
                except Exception:
                    parsed = None
                if isinstance(parsed, dict):
                    raw_analysis = parsed
                else:
                    # fall back
                    return self._fallback_interaction_analysis(text, speaker_diarization, sentiment_trend_data_input, audio_duration_seconds)

            if isinstance(raw_analysis, dict):
                analysis_data = raw_analysis
                return InteractionMetrics(
                    talk_to_listen_ratio=analysis_data.get("talk_to_listen_ratio"),
                    speaker_turn_duration_avg_seconds=analysis_data.get("speaker_turn_duration_avg_seconds"),
                    interruptions_count=analysis_data.get("interruptions_count"),
                    sentiment_trend=analysis_data.get("sentiment_trend", sentiment_trend_data_input if sentiment_trend_data_input is not None else [])
                )
            else:
                return self._fallback_interaction_analysis(text, speaker_diarization, sentiment_trend_data_input, audio_duration_seconds)
        except Exception as e:
            print(f"Error during LLM interaction metrics analysis: {e}")
            return self._fallback_interaction_analysis(text, speaker_diarization, sentiment_trend_data_input, audio_duration_seconds)

    def _fallback_interaction_analysis(self, text: str, 
                                       speaker_diarization: Optional[List[Dict[str, Any]]] = None, 
                                       sentiment_trend_data_input: Optional[List[Dict[str, Any]]] = None,
                                       audio_duration_seconds: Optional[float] = None) -> InteractionMetrics:
        talk_ratio = None
        avg_turn_duration = None
        interruptions = None

        if speaker_diarization and len(speaker_diarization) > 0:
            total_turn_duration = 0
            num_turns = len(speaker_diarization)
            speaker_times: Dict[str, float] = {}
            total_speech_time_diarized = 0.0

            for segment in speaker_diarization:
                start = segment.get('start_time')
                end = segment.get('end_time')
                speaker = segment.get('speaker_label', 'Unknown')
                if start is not None and end is not None:
                    duration = end - start
                    if duration < 0: continue # Skip invalid segments
                    total_turn_duration += duration
                    speaker_times[speaker] = speaker_times.get(speaker, 0.0) + duration
                    total_speech_time_diarized += duration
            
            if num_turns > 0:
                avg_turn_duration = round(total_turn_duration / num_turns, 2)
            
            # Simplistic interruption count based on high turn frequency if many short turns
            if num_turns > 5 and avg_turn_duration is not None and avg_turn_duration < 5: # e.g. avg turn < 5s
                interruptions = int(num_turns * 0.1) # Arbitrary: 10% of turns are interruptions
            else:
                interruptions = 0

            if audio_duration_seconds and audio_duration_seconds > 0 and speaker_times:
                if len(speaker_times) == 1:
                    talk_ratio = round(total_speech_time_diarized / audio_duration_seconds, 2) if total_speech_time_diarized <= audio_duration_seconds else 1.0
                elif len(speaker_times) > 1:
                    # Example: ratio of the most dominant speaker's time to total audio duration
                    max_speaker_time = max(speaker_times.values())
                    talk_ratio = round(max_speaker_time / audio_duration_seconds, 2) if max_speaker_time <= audio_duration_seconds else 1.0
        
        # Use provided sentiment trend or a default empty list
        final_sentiment_trend = sentiment_trend_data_input if sentiment_trend_data_input is not None else []

        return InteractionMetrics(
            talk_to_listen_ratio=talk_ratio,
            speaker_turn_duration_avg_seconds=avg_turn_duration,
            interruptions_count=interruptions,
            sentiment_trend=final_sentiment_trend
        )

    async def get_numerical_linguistic_metrics(self, text: str, audio_duration_seconds: Optional[float] = None) -> NumericalLinguisticMetrics:
        """Calculates and returns numerical linguistic metrics directly from text and optional audio duration."""
        if not text:
            return NumericalLinguisticMetrics() # Return default if no text
        return self._calculate_numerical_linguistic_metrics(text, audio_duration_seconds)
    
    async def analyze(self, transcript: str, audio: Optional[bytes], meta: Dict[str, Any]) -> Dict[str, Any]:
        """Performs full analysis returning both interaction and numerical linguistic metrics."""
        # Use provided audio if available, otherwise use instance audio_data
        audio_bytes = audio or self.audio_data
        
        # Extract metadata
        audio_duration_seconds = meta.get("duration")
        speaker_diarization = meta.get("speaker_diarization")
        sentiment_trend_data_input = meta.get("sentiment_trend")
        
        try:
            # Try to get Gemini analysis first
            interaction_metrics = await self.analyze_interaction_metrics(
                transcript or "", 
                speaker_diarization, 
                sentiment_trend_data_input,
                audio_duration_seconds
            )
        except Exception as e:
            # Fallback to local-only analysis if Gemini fails
            interaction_metrics = InteractionMetrics()
            
        try:
            numerical_linguistic_metrics = await self.get_numerical_linguistic_metrics(
                transcript or "", 
                audio_duration_seconds
            )
        except Exception as e:
            numerical_linguistic_metrics = NumericalLinguisticMetrics()
            
        return {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {
                "numerical_linguistic_metrics": numerical_linguistic_metrics.__dict__ if hasattr(numerical_linguistic_metrics, '__dict__') else {},
                "transcript_length": len(transcript or ""),
                "audio_duration": audio_duration_seconds
            },
            "gemini": {
                "interaction_metrics": interaction_metrics.__dict__ if hasattr(interaction_metrics, '__dict__') else {}
            },
            "errors": None
        }
