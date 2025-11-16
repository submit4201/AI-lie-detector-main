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
        """Streaming transcription: yields interim partial transcripts then final.
        
        This follows the v2 streaming protocol with partial/phase/chunk_index fields.
        """
        meta = meta or {}
        ctx = meta.get("analysis_context")
        
        # Prefer client streaming if available
        if hasattr(self.gemini_client, 'transcribe_stream') and audio:
            chunk_index = 0
            async for ev in self.gemini_client.transcribe_stream(audio, context_prompt=None):
<<<<<<< HEAD
                # Interim partial updates from the streaming client
                if ev.get('interim'):
                    # Prefer an explicit partial_transcript field, fall back to payload
                    partial_text = ev.get('partial_transcript') or ev.get('payload') or ""
                    # Update runtime analysis_context if provided
                    if ctx:
=======
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
                        "local": {"partial_transcript": partial_text},
                        "gemini": None,
                        "errors": None,
                        "partial": True,
                        "phase": "coarse",
                        "chunk_index": chunk_index,
                    }
                    chunk_index += 1
                else:
                    # Final transcript
                    final_text = ev.get('transcript', "")
                    if ctx:
                        ctx.transcript_final = final_text
                    
                    yield {
                        "service_name": self.serviceName,
                        "service_version": self.serviceVersion,
                        "local": {"transcript": final_text},
                        "gemini": None,
                        "errors": None,
                        "partial": False,
                        "phase": "final",
                        "chunk_index": chunk_index,
                    }
                    # Update analysis context
                    if meta and meta.get("analysis_context"):
>>>>>>> 5b97954 (Fix runner orchestration and transcription service streaming format)
                        try:
                            # Try common update method first, fall back to attribute set
                            if hasattr(ctx, "update_transcript_partial"):
                                ctx.update_transcript_partial(partial_text)
                            else:
                                ctx.transcript_partial = partial_text
                        except Exception:
                            pass
                    yield {
                        "service_name": self.serviceName,
                        "service_version": self.serviceVersion,
                        "local": {"partial_transcript": partial_text},
                        "gemini": ev.get('gemini', None),
                        "errors": None,
                        "partial": True,
                        "phase": "coarse",
                        "chunk_index": chunk_index,
                    }
                    chunk_index += 1
                else:
                    # Final transcript event
                    final_text = ev.get('transcript', "") or ev.get('final', "")
                    if ctx:
                        try:
                            ctx.transcript_final = final_text
                        except Exception:
                            pass
                    # Yield final chunk
                    yield {
                        "service_name": self.serviceName,
                        "service_version": self.serviceVersion,
                        "local": {"transcript": final_text},
                        "gemini": ev.get('gemini', None),
                        "errors": None,
                        "partial": False,
                        "phase": "final",
                        "chunk_index": chunk_index,
                    }
                    # Update analysis context finalizer if available
                    if meta and meta.get("analysis_context"):
                        try:
                            if hasattr(meta.get("analysis_context"), "finalize_transcript"):
                                meta.get("analysis_context").finalize_transcript(final_text)
                        except Exception:
                            pass
                    return
        
        # Default fallback to non-streaming behavior
        # Yield empty partial first
        yield {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {"partial_transcript": ""},
            "gemini": None,
            "errors": None,
            "partial": True,
            "phase": "coarse",
            "chunk_index": 0,
        }
        
        # Then get final result from analyze
        final = await self.analyze(transcript=transcript, audio=audio, meta=meta)
        
        # Update context
        if ctx and final.get("transcript"):
            ctx.transcript_final = final["transcript"]
        
        # Convert analyze result to streaming format
        yield {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {"transcript": final.get("transcript", "")},
            "gemini": None,
            "errors": final.get("errors"),
            "partial": False,
            "phase": "final",
            "chunk_index": 1,
        }
