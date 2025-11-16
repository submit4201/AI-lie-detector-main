from __future__ import annotations

import asyncio
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, AsyncGenerator, Tuple

from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.gemini_client import GeminiClientV2
from backend.services.v2_services.service_registry import build_service_instances, ServiceFactory, REGISTERED_SERVICES

logger = logging.getLogger(__name__)


@dataclass
class AnalysisContext:
    """Central context object for v2 analysis pipeline.
    
    This dataclass holds all state for a single analysis request,
    avoiding global mutable state. Services receive this via meta["analysis_context"].
    """
    # Transcript state
    transcript_partial: str = ""
    transcript_final: Optional[str] = None
    
    # Audio state
    audio_bytes: Optional[bytes] = None
    audio_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Metrics and analysis results
    quantitative_metrics: Dict[str, Any] = field(default_factory=dict)
    service_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Speaker and diarization
    speaker_segments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Session context (compact, privacy-safe)
    session_summary: Optional[Dict[str, Any]] = None
    
    # Configuration flags
    config: Dict[str, Any] = field(default_factory=dict)


class V2AnalysisRunner:
    """Orchestrates the execution of v2 analysis services."""

    def __init__(
        self,
        gemini_client: Optional[GeminiClientV2] = None,
        service_factories: Optional[List[ServiceFactory]] = None,
    ):
        self.gemini_client = gemini_client or GeminiClientV2()
        # Instantiate services using either provided factories (testable) or the default registry
        self._service_factories = service_factories or REGISTERED_SERVICES
        self.services = [factory({"gemini_client": self.gemini_client}) for factory in self._service_factories]
        self.transcription_service = next((s for s in self.services if s.serviceName == 'transcription'), None)
        self.audio_analysis_service = next((s for s in self.services if s.serviceName == 'audio_analysis'), None)

    async def run(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Runs the full v2 analysis pipeline.
        1. Transcribes audio if no transcript is provided.
        2. Runs all other registered services concurrently.
        3. Aggregates and returns the results.
        """
        meta = meta or {}
        results: Dict[str, Any] = {
            "services": {},
            "errors": [],
            "timings": {},
        }
        start_time = time.time()

        # Build service instances for this run with current context (so they capture the transcript)
        services_for_request = self._build_services(transcript or "", audio, meta)

        # --- 1. Concurrent Audio Analysis and Transcription ---
        initial_tasks = []
        transcription_service = next((s for s in services_for_request if s.serviceName == "transcription"), None)
        audio_analysis_service = next((s for s in services_for_request if s.serviceName == "audio_analysis"), None)

        if audio_analysis_service and audio:
            initial_tasks.append(audio_analysis_service.analyze(audio=audio, meta=meta))

        final_transcript = transcript
        if not final_transcript and transcription_service and audio:
            initial_tasks.append(transcription_service.analyze(audio=audio, meta=meta))

        if initial_tasks:
            initial_results = await asyncio.gather(*initial_tasks, return_exceptions=True)
            for result in initial_results:
                if isinstance(result, Exception):
                    logger.error(f"Initial service failed during gather: {result}", exc_info=True)
                    results["errors"].append({"service": "initialization", "error": str(result)})
                    continue

                service_name = result.get("service_name")
                if service_name:
                    results["services"][service_name] = result
                    if service_name == "audio_analysis" and not result.get("errors"):
                        meta['duration'] = result.get("local", {}).get("duration")
                    elif service_name == "transcription" and not result.get("errors"):
                        final_transcript = result.get("transcript")

        # If transcription didn't happen via a transcription service, try gemini client
        auto_generated = False
        if not final_transcript and audio:
            final_transcript, auto_generated = await self._ensure_transcript(final_transcript or transcript or "", audio, meta)

        results["transcript"] = final_transcript
        results["meta"] = {**meta, "transcript_auto_generated": auto_generated}

        # --- 2. Concurrent Analysis of Other Services ---
        other_services = [
            s for s in services_for_request
            if s.serviceName not in ["transcription", "audio_analysis"]
        ]
        
        async def run_service(service: AnalysisService):
            try:
                return service.serviceName, await service.analyze(
                    transcript=final_transcript, audio=audio, meta=meta
                )
            except Exception as e:
                logger.error(f"Service {service.serviceName} failed during run: {e}", exc_info=True)
                return service.serviceName, {
                    "service_name": service.serviceName,
                    "errors": [{"error": "Service execution failed", "details": str(e)}],
                    "local": {}, "gemini": None
                }

        if other_services:
            service_tasks = [run_service(service) for service in other_services]
            service_results = await asyncio.gather(*service_tasks)
            for service_name, result_data in service_results:
                results["services"][service_name] = result_data

        results["timings"]["total_duration"] = time.time() - start_time
        return results

    async def stream_run(
        self,
        transcript: str,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Yield incremental service results for streaming responses."""

        meta = meta or {}
        # If the transcription service provides a streaming interface, use it
        transcript_text, generated = transcript, False
        if self.transcription_service and hasattr(self.transcription_service, 'stream_analyze') and audio:
            # Stream transcript events and yield interim updates
            async for ev in self.transcription_service.stream_analyze(transcript=transcript, audio=audio, meta=meta):
                # The streaming service may return updates for different services
                svc = ev.get('service_name', 'transcription')
                if ev.get('interim'):
                    # If partial transcript is present, forward as a transcript event
                    if ev.get('partial_transcript') is not None:
                        yield {
                            "event": "analysis.update",
                            "service": "transcript",
                            "payload": {"partial_transcript": ev.get('partial_transcript', '')}
                        }
                    # If the service also emits additional keys (e.g., manipulation), forward them
                    elif ev.get('payload'):
                        yield {
                            "event": "analysis.update",
                            "service": svc,
                            "payload": ev.get('payload')
                        }
                else:
                    # final transcript event; support other service payloads
                    payload = ev.get('payload') or {}
                    # If this is a final transcript payload, update transcript_text
                    if svc == 'transcription' or payload.get('transcript'):
                        transcript_text = payload.get('transcript', transcript_text)
                        generated = True
                        yield {
                            "event": "analysis.update",
                            "service": "transcript",
                            "payload": {"transcript": transcript_text, "auto_generated": generated},
                        }
                    else:
                        # Final payload for another service
                        yield {
                            "event": "analysis.update",
                            "service": svc,
                            "payload": payload,
                        }
                    # break after final transcript or if this stream concluded
                    break
        else:
            transcript_text, generated = await self._ensure_transcript(transcript, audio, meta)

        aggregate = {
            "transcript": transcript_text,
            "services": {},
            "errors": [],
            "meta": {**meta, "transcript_auto_generated": generated},
        }

        yield {
            "event": "analysis.update",
            "service": "transcript",
            "payload": {
                "transcript": transcript_text,
                "auto_generated": generated,
            },
        }

        services = self._build_services(transcript_text, audio, meta)
        tasks = [
            asyncio.create_task(self._execute_service(service, transcript_text, audio, meta))
            for service in services
        ]

        total = len(tasks) if tasks else 1
        completed = 0

        for task in asyncio.as_completed(tasks):
            service_name, payload, error_message = await task
            aggregate["services"][service_name] = payload
            if error_message:
                aggregate["errors"].append({"service": service_name, "message": error_message})

            completed += 1

            yield {
                "event": "analysis.update",
                "service": service_name,
                "payload": payload,
                "errors": error_message,
            }

            yield {
                "event": "analysis.progress",
                "service": service_name,
                "completed": completed,
                "total": total,
            }

        yield {
            "event": "analysis.done",
            "payload": aggregate,
        }

    async def _ensure_transcript(self, transcript: str, audio: Optional[bytes], meta: Dict[str, Any]) -> tuple[str, bool]:
        """Ensure we have a transcript text. If missing and audio provided, try to transcribe.

        Returns (transcript_text, auto_generated_bool)
        """
        if transcript and transcript.strip():
            return transcript, False

        # If a configured transcription service exists, use it
        if self.transcription_service and audio:
            try:
                result = await self.transcription_service.analyze(transcript=None, audio=audio, meta=meta)
                text = result.get("transcript", "")
                return text, True
            except Exception:
                # Fall back to gemini client
                pass

        # As a fallback, use the gemini client directly if available
        if audio and hasattr(self.gemini_client, "transcribe"):
            try:
                text = await self.gemini_client.transcribe(audio)
                return text, True
            except Exception:
                logger.warning("Fallback transcription via gemini client failed", exc_info=True)

        return transcript or "", False

    def _build_services(self, transcript: str, audio: Optional[bytes], meta: Dict[str, Any]) -> List[AnalysisService]:
        """Instantiate service instances using the configured factories for the runner."""
        context = {
            "gemini_client": self.gemini_client,
            "transcript": transcript,
            "audio": audio,
            "meta": meta or {},
        }
        return [factory(context) for factory in self._service_factories]

    async def _execute_service(self, service: AnalysisService, transcript: str, audio: Optional[bytes], meta: Dict[str, Any]) -> Tuple[str, Dict[str, Any], Optional[str]]:
        """Run a single AnalysisService and return (service_name, payload, error_message)."""
        try:
            payload = await service.analyze(transcript, audio, meta)
            return service.serviceName, payload, None
        except Exception as e:
            logger.error(f"Error executing service {service.serviceName}: {e}", exc_info=True)
            return service.serviceName, {}, str(e)