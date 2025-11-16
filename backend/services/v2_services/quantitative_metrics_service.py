"""QuantitativeMetricsService v2

Migrated from backend.services.quantitative_metrics_service (now archived under
backend/services/archived/quantitative_metrics_service_v1.py). The v1 service
combined local linguistic heuristics with Gemini-generated interaction metrics
to power the "quantitative_metrics" slice of the AI Lie Detector pipeline.

This v2 class preserves that utility while adopting the shared v2 AnalysisService
protocol, google-genai SDK client, and richer InteractionMetrics outputs.
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
from typing import List, Dict, Optional, Any, TYPE_CHECKING, Tuple
from backend.services.v2_services.analysis_protocol import AnalysisService
import json
import re
import logging

# Use TYPE_CHECKING to avoid circular import while keeping type hints
if TYPE_CHECKING:
    from backend.services.gemini_service import GeminiService

from backend.services.v2_services.gemini_client import GeminiClientV2 as DefaultGeminiClient

logger = logging.getLogger(__name__)


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
        logger.info(f"QuantitativeMetricsService initialized for transcript of length {len(transcript or '')}")

    def _calculate_numerical_linguistic_metrics(self, text: str, audio_duration_seconds: Optional[float] = None) -> NumericalLinguisticMetrics:
        logger.debug("Calculating numerical linguistic metrics...")
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

    @staticmethod
    def _normalize_sentiment_trend(
        trend_candidate: Optional[Any],
        fallback: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        if isinstance(trend_candidate, list):
            return trend_candidate
        if isinstance(trend_candidate, dict):
            return [trend_candidate]
        if isinstance(trend_candidate, (int, float)):
            return [{"sentiment_score": float(trend_candidate)}]
        if isinstance(trend_candidate, str) and trend_candidate.strip():
            return [{"sentiment_label": trend_candidate.strip()}]
        return fallback or []

    @staticmethod
    def _normalize_emotion_distribution(candidate: Optional[Any]) -> List[Dict[str, Any]]:
        if isinstance(candidate, list):
            return candidate
        if isinstance(candidate, dict):
            return [candidate]
        if isinstance(candidate, str) and candidate.strip():
            return [{"emotion": candidate.strip(), "score": None}]
        return []

    @staticmethod
    def _coerce_string_list(candidate: Optional[Any]) -> List[str]:
        if candidate is None:
            return []
        if isinstance(candidate, list):
            return [str(item) for item in candidate]
        return [str(candidate)]

    @staticmethod
    def _coerce_float(value: Any) -> Optional[float]:
        try:
            if value is None:
                return None
            return float(value)
        except (ValueError, TypeError):
            return None

    def _estimate_sentiment_locally(self, text: str) -> Tuple[str, float, float, List[Dict[str, Any]]]:
        positive_words = {
            "good", "great", "excellent", "positive", "confident", "sure", "clear", "definitely", "absolutely",
            "trust", "honest", "calm", "secure", "upbeat", "happy", "glad", "yes", "agree",
        }
        negative_words = {
            "bad", "poor", "negative", "uncertain", "doubt", "worry", "concern", "angry", "mad", "frustrated",
            "anxious", "sad", "no", "disagree", "hesitant", "nervous", "stress", "confused",
        }
        tokens = re.findall(r"\b\w+\b", text.lower())
        if not tokens:
            return "neutral", 0.5, 0.1, [{"emotion": "neutral", "score": 1.0}]

        positive_hits = sum(1 for token in tokens if token in positive_words)
        negative_hits = sum(1 for token in tokens if token in negative_words)
        total_hits = positive_hits + negative_hits

        if total_hits == 0:
            return "neutral", 0.5, 0.1, [{"emotion": "neutral", "score": 1.0}]

        raw_score = (positive_hits - negative_hits) / total_hits  # -1 to 1
        normalized_score = round((raw_score + 1) / 2, 3)  # 0 to 1
        sentiment_label = "positive" if raw_score > 0.1 else "negative" if raw_score < -0.1 else "neutral"
        sentiment_confidence = round(min(1.0, max(0.1, abs(raw_score))), 3)

        emotion_distribution: List[Dict[str, Any]] = []
        if positive_hits:
            emotion_distribution.append({"emotion": "positive", "score": round(positive_hits / total_hits, 3)})
        if negative_hits:
            emotion_distribution.append({"emotion": "negative", "score": round(negative_hits / total_hits, 3)})
        if not emotion_distribution:
            emotion_distribution.append({"emotion": "neutral", "score": 1.0})

        return sentiment_label, normalized_score, sentiment_confidence, emotion_distribution

    def _derive_engagement_features(self, text: str) -> Tuple[Optional[float], Optional[str], Optional[float], List[str]]:
        if not text:
            return None, None, None, []

        sentences = [segment for segment in re.split(r"[.!?]+", text) if segment.strip()]
        question_count = text.count("?")
        declarative_count = max(len(sentences) - question_count, 1)
        question_ratio = round(question_count / declarative_count, 2) if question_count else 0.0

        exclamation_count = text.count("!")
        emphasis_tokens = re.findall(r"\b[A-Z]{3,}\b", text)
        token_length = max(len(sentences), 1)
        energy_score = round(min(1.0, (question_count + exclamation_count + len(emphasis_tokens)) / token_length), 3)

        if energy_score >= 0.6 or question_ratio >= 0.5:
            engagement_level = "high"
        elif energy_score >= 0.3 or question_ratio >= 0.25:
            engagement_level = "medium"
        else:
            engagement_level = "low"

        notable_events: List[str] = []
        if question_ratio >= 0.5:
            notable_events.append("high inquisitiveness")
        if exclamation_count >= 3:
            notable_events.append("heightened emphasis")
        if len(emphasis_tokens) >= 2:
            notable_events.append("frequent emphasis words")

        filler_words = ["um", "uh", "like", "you know", "sort of", "kind of"]
        words = re.findall(r"\b\w+\b", text.lower())
        filler_hits = sum(1 for token in words if token in filler_words)
        if words:
            filler_ratio = filler_hits / len(words)
            if filler_ratio >= 0.05:
                notable_events.append("high filler usage")

        return question_ratio, engagement_level, energy_score, notable_events
    async def analyze_interaction_metrics(
        self, 
        text: str, 
        audio_data: Optional[bytes] = None,
        speaker_diarization: Optional[List[Dict[str, Any]]] = None, 
        sentiment_trend_data_input: Optional[List[Dict[str, Any]]] = None,
        audio_duration_seconds: Optional[float] = None
    ) -> InteractionMetrics:
        
        if not text and not speaker_diarization:
            logger.warning("Insufficient data for interaction metrics analysis.")
            # Use a conventional exception rather than attempting to raise a Pydantic model
            raise ValueError(
                "Insufficient data: either transcript text or speaker diarization must be provided for interaction metrics."
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
                    1.  Talk-to-Listen Ratio (Optional[float])
                    2.  Speaker Turn Duration Average (Optional[float], in seconds)
                    3.  Interruptions Count (Optional[int])
                    4.  Sentiment Trend (List[Dict[str, Any]])
                    5.  Overall Sentiment Label (str: positive/neutral/negative/etc.)
                    6.  Overall Sentiment Score (float between 0-1) and Sentiment Confidence (float between 0-1)
                    7.  Emotion Distribution (List[Dict] with keys such as emotion/score)
                    8.  Engagement Level (string descriptor such as High/Medium/Low)
                    9.  Question-to-Statement Ratio (float)
                    10. Conversation Energy Score (float 0-1 based on pacing/emphasis cues)
                    11. Notable Interaction Events (List[str] describing important behaviors observed)

                    Provide your analysis as a JSON object matching the structure of the InteractionMetrics model:
                    {{
                    "talk_to_listen_ratio": float_or_null,
                    "speaker_turn_duration_avg_seconds": float_or_null,
                    "interruptions_count": int_or_null,
                    "sentiment_trend": [],
                    "overall_sentiment_label": str_or_null,
                    "overall_sentiment_score": float_or_null,
                    "sentiment_confidence": float_or_null,
                    "emotion_distribution": list_of_dicts,
                    "engagement_level": str_or_null,
                    "question_to_statement_ratio": float_or_null,
                    "conversation_energy_score": float_or_null,
                    "notable_interaction_events": list_of_strings
                    }}
                    If specific details cannot be reliably inferred from the provided data, use null for optional fields or appropriate defaults like empty lists for sentiment_trend.
                    Focus on deriving these from speaker diarization and sentiment data primarily. The transcript is for context.
                    Ensure the output is valid JSON and can be parsed directly into the InteractionMetrics model.
                    """
        
        try:
            logger.info("Querying Gemini for interaction metrics.")
            # Use the v2 Gemini client for structured analysis
            raw_analysis = await self.gemini_client.query_json(prompt)
            if isinstance(raw_analysis, str):
                # log that this came back as a string
                logger.warning("LLM returned raw analysis as a string.")
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
                    logger.warning("Failed to parse string from LLM, falling back to local analysis.")
                    return self._fallback_interaction_analysis(text, speaker_diarization, sentiment_trend_data_input, audio_duration_seconds)

            if isinstance(raw_analysis, dict):
                analysis_data = raw_analysis
                normalized_trend = self._normalize_sentiment_trend(
                    analysis_data.get("sentiment_trend"),
                    sentiment_trend_data_input,
                )
                emotion_distribution = self._normalize_emotion_distribution(analysis_data.get("emotion_distribution"))
                notable_events = self._coerce_string_list(analysis_data.get("notable_interaction_events"))

                return InteractionMetrics(
                    talk_to_listen_ratio=self._coerce_float(analysis_data.get("talk_to_listen_ratio")),
                    speaker_turn_duration_avg_seconds=self._coerce_float(analysis_data.get("speaker_turn_duration_avg_seconds")),
                    interruptions_count=analysis_data.get("interruptions_count"),
                    sentiment_trend=normalized_trend,
                    overall_sentiment_label=analysis_data.get("overall_sentiment_label"),
                    overall_sentiment_score=self._coerce_float(analysis_data.get("overall_sentiment_score")),
                    sentiment_confidence=self._coerce_float(analysis_data.get("sentiment_confidence")),
                    emotion_distribution=emotion_distribution,
                    engagement_level=analysis_data.get("engagement_level"),
                    question_to_statement_ratio=self._coerce_float(analysis_data.get("question_to_statement_ratio")),
                    conversation_energy_score=self._coerce_float(analysis_data.get("conversation_energy_score")),
                    notable_interaction_events=notable_events,
                )
            else:
                logger.warning("LLM analysis did not return a dictionary, falling back to local analysis.")
                return self._fallback_interaction_analysis(text, speaker_diarization, sentiment_trend_data_input, audio_duration_seconds)
        except Exception as e:
            logger.error(f"Error during LLM interaction metrics analysis: {e}", exc_info=True)
            print(f"Error during LLM interaction metrics analysis: {e}")
            return self._fallback_interaction_analysis(text, speaker_diarization, sentiment_trend_data_input, audio_duration_seconds)

    def _fallback_interaction_analysis(self, text: str, 
                                       speaker_diarization: Optional[List[Dict[str, Any]]] = None, 
                                       sentiment_trend_data_input: Optional[List[Dict[str, Any]]] = None,
                                       audio_duration_seconds: Optional[float] = None) -> InteractionMetrics:
        logger.info("Performing fallback local interaction analysis.")
        talk_ratio = None
        avg_turn_duration = None
        interruptions = None

        normalized_trend = self._normalize_sentiment_trend(sentiment_trend_data_input)
        (
            overall_sentiment_label,
            overall_sentiment_score,
            sentiment_confidence,
            emotion_distribution,
        ) = self._estimate_sentiment_locally(text)
        (
            question_ratio,
            engagement_level,
            energy_score,
            notable_events,
        ) = self._derive_engagement_features(text)

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

        if talk_ratio and talk_ratio >= 0.75:
            notable_events.append("dominant speaker detected")
        if interruptions and interruptions > 0:
            notable_events.append("possible interruptions observed")
        
        final_sentiment_trend = normalized_trend
        deduped_events: List[str] = []
        for event in notable_events:
            if event not in deduped_events:
                deduped_events.append(event)

        return InteractionMetrics(
            talk_to_listen_ratio=talk_ratio,
            speaker_turn_duration_avg_seconds=avg_turn_duration,
            interruptions_count=interruptions,
            sentiment_trend=final_sentiment_trend,
            overall_sentiment_label=overall_sentiment_label,
            overall_sentiment_score=overall_sentiment_score,
            sentiment_confidence=sentiment_confidence,
            emotion_distribution=emotion_distribution,
            engagement_level=engagement_level,
            question_to_statement_ratio=question_ratio,
            conversation_energy_score=energy_score,
            notable_interaction_events=deduped_events,
        )

    async def get_numerical_linguistic_metrics(self, text: str, audio_duration_seconds: Optional[float] = None) -> NumericalLinguisticMetrics:
        """Calculates and returns numerical linguistic metrics directly from text and optional audio duration."""
        if not text:
            logger.warning("No text provided for numerical linguistic metrics, returning empty metrics.")
            return NumericalLinguisticMetrics() # Return default if no text
        return self._calculate_numerical_linguistic_metrics(text, audio_duration_seconds)
    
    async def stream_analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ):
        """
        Stream quantitative metrics analysis with incremental results.
        
        Yields:
        - Coarse phase: Quick numerical linguistic metrics
        - Final phase: Complete metrics including Gemini interaction analysis
        """
        meta = meta or {}
        audio_bytes = audio or self.audio_data
        
        # Extract metadata
        audio_duration_seconds = meta.get("duration")
        speaker_diarization = meta.get("speaker_diarization")
        sentiment_trend_data_input = meta.get("sentiment_trend")
        
        logger.info(f"Starting v2 streaming analysis for transcript. Duration: {audio_duration_seconds}s")
        
        # Phase 1: Yield quick numerical linguistic metrics (coarse)
        try:
            numerical_linguistic_metrics = await self.get_numerical_linguistic_metrics(
                transcript or "", 
                audio_duration_seconds
            )
            
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": {
                    "numerical_linguistic_metrics": numerical_linguistic_metrics.__dict__ if hasattr(numerical_linguistic_metrics, '__dict__') else {},
                    "transcript_length": len(transcript or ""),
                    "audio_duration": audio_duration_seconds
                },
                "gemini": {},
                "errors": [],
                "partial": True,
                "phase": "coarse",
                "chunk_index": 0
            }
        except Exception as e:
            logger.error(f"Numerical linguistic metrics calculation failed: {e}", exc_info=True)
            numerical_linguistic_metrics = NumericalLinguisticMetrics()
        
        # Phase 2: Add Gemini interaction analysis (final)
        try:
            interaction_metrics = await self.analyze_interaction_metrics(
                text=transcript or "",
                audio_data=audio_bytes,
                speaker_diarization=speaker_diarization,
                sentiment_trend_data_input=sentiment_trend_data_input,
                audio_duration_seconds=audio_duration_seconds,
            )
        except Exception as e:
            logger.error(f"Interaction metrics analysis failed: {e}", exc_info=True)
            interaction_metrics = self._fallback_interaction_analysis(
                transcript or "", 
                speaker_diarization, 
                sentiment_trend_data_input, 
                audio_duration_seconds
            )
            
        yield {
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
            "errors": [],
            "partial": False,
            "phase": "final",
            "chunk_index": 1
        }
    
    async def analyze(self, transcript: str, audio: Optional[bytes], meta: Dict[str, Any]) -> Dict[str, Any]:
        """Performs full analysis returning both interaction and numerical linguistic metrics (non-streaming)."""
        # Use provided audio if available, otherwise use instance audio_data
        audio_bytes = audio or self.audio_data
        
        # Extract metadata
        audio_duration_seconds = meta.get("duration")
        speaker_diarization = meta.get("speaker_diarization")
        sentiment_trend_data_input = meta.get("sentiment_trend")
        
        logger.info(f"Starting v2 analysis for transcript. Duration: {audio_duration_seconds}s")
        
        try:
            # Try to get Gemini analysis first
            interaction_metrics = await self.analyze_interaction_metrics(
                text=transcript or "",
                audio_data=audio_bytes,
                speaker_diarization=speaker_diarization,
                sentiment_trend_data_input=sentiment_trend_data_input,
                audio_duration_seconds=audio_duration_seconds,
            )
        except Exception as e:
            logger.error(f"Interaction metrics analysis failed: {e}", exc_info=True)
            # Fallback to local-only analysis if Gemini fails
            interaction_metrics = self._fallback_interaction_analysis(transcript or "", speaker_diarization, sentiment_trend_data_input, audio_duration_seconds)
            
        try:
            numerical_linguistic_metrics = await self.get_numerical_linguistic_metrics(
                transcript or "", 
                audio_duration_seconds
            )
        except Exception as e:
            logger.error(f"Numerical linguistic metrics calculation failed: {e}", exc_info=True)
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
