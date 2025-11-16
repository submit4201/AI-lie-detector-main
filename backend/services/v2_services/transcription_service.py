"""TranscriptionService v2

A dedicated service to handle audio transcription using the Gemini API.
This service implements the v2 AnalysisService protocol and is designed to
be run early in the v2 pipeline so other services receive the transcript.

Comparison to v1:
- v1 transcription was embedded in the older `gemini_service.py` flow.
- v2 extracts transcription to a dedicated service with clearer error handling,
  improved model selection (via `GEMINI_MODEL_TRANSCRIBE`) and faster
  upload-based transcriptions when the SDK supports it.
- v2 should be streaming-capable or its not useful for real-time applications. #FIXME
"""
"""Transcription service for v2.

This module no longer prints or warns loudly about API versions. The
service accepts any object that implements an async `transcribe` method
so it can be unit-tested with mocks.
"""
import logging
from typing import Optional, Dict, Any

from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.gemini_client import GeminiClientV2

logger = logging.getLogger(__name__)


class TranscriptionService(AnalysisService):
    """A service dedicated to transcribing audio."""
    serviceName = "transcription"
    serviceVersion = "2.0"

    def __init__(self, gemini_client: Optional[GeminiClientV2] = None, **kwargs):
        # Accept either a properly constructed GeminiClientV2 or any object
        # implementing an async `transcribe` method (for test injection).
        if gemini_client is None:
            gemini_client = GeminiClientV2()
        elif not hasattr(gemini_client, "transcribe"):
            # Do not fail; warn and allow tests to supply alternate clients
            logger.warning("Provided gemini_client does not implement 'transcribe'.")

        self.gemini_client = gemini_client
        super().__init__(**kwargs)
        logger.info("TranscriptionService initialized.")

    async def analyze(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Transcribes the given audio. If a transcript is already provided,
        it returns it directly.
        """
        errors = []
        # add v1 client use error to list if present
        if not isinstance(self.gemini_client, GeminiClientV2):
            errors.append({
                "error": "Invalid Gemini client",
                "details": "A GeminiClientV2 instance is required for TranscriptionService."
            })
        # TODO: we want streaming transcription which means this "final transcript" will have to change.
        # Implementing low-latency partial transcripts requires a streaming SDK or slicing the audio and
        # progressively transcribing chunks — we'll add streaming support to the runtime pipeline and
        # the gemini client when SDK streaming is available.
        final_transcript = transcript
        logger.warning("we are still using a non streaming transcription method, this needs to be updated for real-time use cases")

        if final_transcript:
            logger.info("Transcript provided, skipping transcription.")
        elif audio:
            logger.info("Audio provided, starting transcription.")
            try:
                final_transcript = await self.gemini_client.transcribe(audio)
                logger.info(f"Transcription successful. Length: {len(final_transcript)}")
            except Exception as e:
                logger.error(f"Transcription failed: {e}", exc_info=True)
                errors.append({"error": "Transcription failed", "details": str(e)})
                final_transcript = ""
        else:
            logger.warning("No transcript or audio provided to TranscriptionService.")
            final_transcript = ""
            errors.append({"error": "No audio data provided for transcription.", "details": ""})

        return {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "transcript": final_transcript,
            "errors": errors if errors else None,
            "local": {},
            "gemini": None,
        }

    async def stream_analyze(self, transcript: Optional[str] = None, audio: Optional[bytes] = None, meta: Optional[Dict[str, Any]] = None):
        """Optional streaming analysis - yields interim updates followed by final transcript.

        This is a simple compatibility shim until the Gemini SDK exposes true
        streaming transcription; it yields two events: an initial placeholder
        then the final result returned by `analyze`.
        """
        # Prefer client streaming if available
        if hasattr(self.gemini_client, 'transcribe_stream') and audio:
            # Forward any existing transcript text as context to Gemini streaming
            # Build context prompt with optional streaming analysis instructions
            context_prompt = None
            if transcript:
                context_prompt = f"TranscriptContext:{transcript}\nPlease continue or refine as needed."  # guideline to the model

            # Allow meta to include a custom analysis instruction for the streaming session.
            # If the front-end passes `meta['streaming_analysis'] = True` and provides
            # `meta['analysis_instructions']`, we'll append these instructions to the context
            # so the live model can emit JSON objects that include analysis results.
            if meta and meta.get("streaming_analysis"):
                ai = meta.get("analysis_instructions") or (
                    "Also analyze the text for manipulation and argument structure. "
                    "Return JSON containing keys 'manipulation' and 'argument' alongside 'transcription'."
                )
                if context_prompt:
                    context_prompt = context_prompt + "\n" + ai
                else:
                    context_prompt = ai
            async for ev in self.gemini_client.transcribe_stream(audio, context_prompt=context_prompt):
                # ev: {'interim': bool, 'partial_transcript': str} or final {'interim': False, 'transcript': '...'}
                # If the gemini client included a service name (structured analysis), honor it
                svc_name = ev.get('service_name', self.serviceName)
                if ev.get('interim'):
                    if 'partial_transcript' in ev:
                        # Update runtime analysis_context if provided
                        if meta and meta.get("analysis_context"):
                            try:
                                meta.get("analysis_context").update_transcript_partial(ev.get('partial_transcript', ""))
                            except Exception:
                                pass
                        yield {"service_name": svc_name, "interim": True,"partial_transcript": ev.get('partial_transcript', "")}
                    elif 'payload' in ev:
                        yield {"service_name": svc_name, "interim": True, "payload": ev.get('payload')}
                else:
                    final_payload = {
                        "service_name": self.serviceName,
                        "service_version": self.serviceVersion,
                        "transcript": ev.get('transcript', ""),
                        "errors": None,
                        "local": {},
                        "gemini": None,
                    }
                    # Update analysis context
                    if meta and meta.get("analysis_context"):
                        try:
                            meta.get("analysis_context").finalize_transcript(ev.get('transcript', ""))
                        except Exception:
                            pass
                    yield {"service_name": svc_name, "interim": False, "payload": final_payload}
                    return

        # Default fallback to non-streaming behavior
        yield {"service_name": self.serviceName, "interim": True, "partial_transcript": ""}
        final = await self.analyze(transcript=transcript, audio=audio, meta=meta)
        yield {"service_name": self.serviceName, "interim": False, "payload": final}
