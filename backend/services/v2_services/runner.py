from __future__ import annotations

import asyncio
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, AsyncGenerator, Tuple

from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.analysis_context import AnalysisContext
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
    
    # Enhanced metrics
    acoustic_metrics: Optional[Dict[str, Any]] = None  # Enhanced acoustic metrics
    linguistic_metrics: Optional[Dict[str, Any]] = None  # Enhanced linguistic metrics
    
    # Baseline and calibration
    baseline_profile: Optional[Dict[str, Any]] = None  # User baseline for normalization
    
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
        Runs the full v2 analysis pipeline by consuming stream_run.
        Returns the final aggregated results.
        """
        meta = meta or {}
        # Create the per-request AnalysisContext and attach it to meta
        meta.setdefault("analysis_context", AnalysisContext(audio_bytes=audio))
        results: Dict[str, Any] = {
            "services": {},
            "errors": [],
            "timings": {},
            "transcript": "",
            "meta": meta,
        }
        
        # Consume the streaming pipeline
        async for event in self.stream_run(transcript, audio, meta):
            event_type = event.get("event")
            
            if event_type == "analysis.update":
                service = event.get("service")
                payload = event.get("payload", {})
                
                # Only store final results (not partial)
                if not payload.get("partial", False):
                    results["services"][service] = payload
                
                # Extract errors
                if payload.get("errors"):
                    results["errors"].extend(payload["errors"])
            
            elif event_type == "analysis.done":
                # Final event with aggregated data
                done_payload = event.get("payload", {})
                if done_payload.get("results"):
                    results["services"].update(done_payload["results"])
                if done_payload.get("meta"):
                    results["meta"].update(done_payload["meta"])
                    results["transcript"] = done_payload["meta"].get("transcript_final", results["transcript"])
        
        results["timings"]["total_duration"] = time.time() - start_time
        return results

    async def stream_run(
        self,
        transcript: Optional[str] = None,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Yield incremental service results with phased orchestration.
        
        Phase A: Input prep - create AnalysisContext
        Phase B: Foundational services - transcription and audio analysis in parallel
        Phase C: Metrics - quantitative metrics once we have enough data
        Phase D: Higher-level analysis - manipulation and argument once we have context
        """
        meta = meta or {}
        # Create AnalysisContext and inject it to the meta
        ctx = AnalysisContext(audio_bytes=audio)
        meta.setdefault("analysis_context", ctx)
        # If the transcription service provides a streaming interface, use it
        transcript_text, generated = transcript, False
        if self.transcription_service and hasattr(self.transcription_service, 'stream_analyze') and audio:
            # Stream transcript events and yield interim updates
            # Start transcription streaming; updates to ctx.transcript_partial are expected
            async for ev in self.transcription_service.stream_analyze(transcript=transcript, audio=audio, meta=meta):
                # The streaming service may return updates for different services
                svc = ev.get('service_name', 'transcription')
                if ev.get('interim'):
                    # If partial transcript is present, forward as a transcript event
                    if ev.get('partial_transcript') is not None:
                        # Forward updated partial transcript
                        meta['analysis_context'].update_transcript_partial(ev.get('partial_transcript', ''))
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
                        try:
                            meta['analysis_context'].finalize_transcript(transcript_text)
                        except Exception:
                            pass
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
            "event": "analysis.done",
            "payload": {
                "transcript": transcript_text,
                "auto_generated": generated,
            },
        }

        services = self._build_services(transcript_text, audio, meta)
        # Phase orchestration: start audio and transcription then metrics then higher-level services
        # Build the ordered tasks list ensuring audio and transcription are not re-run.
        services_map = {s.serviceName: s for s in services}
        # Start all non-audio/transcription services; but prioritize core ones
        ordered = [s for s in services if s.serviceName not in ("transcription", "audio_analysis")]
        priority = ["quantitative_metrics", "manipulation", "argument"]

        def _priority_key(svc: AnalysisService):
            try:
                idx = priority.index(svc.serviceName)
                return (0, idx)
            except ValueError:
                return (1, 0)

        ordered.sort(key=_priority_key)
        # Start tasks concurrently — individual services can use analysis_context for partials
        # Use an event queue to stream incremental service results from service.stream_analyze
        event_queue: "asyncio.Queue" = asyncio.Queue()

        async def _service_stream_to_queue(service: AnalysisService):
            try:
                if hasattr(service, 'stream_analyze'):
                    async for partial in service.stream_analyze(transcript_text, audio, meta):
                        await event_queue.put({
                            "type": "partial",
                            "service": service.serviceName,
                            "payload": partial,
                        })
                    # After stream finishes we should attempt a final call to ensure consistency
                    final_payload = await service.analyze(transcript_text, audio, meta)
                    await event_queue.put({"type": "final", "service": service.serviceName, "payload": final_payload})
                    return service.serviceName, final_payload, None
                else:
                    final_payload = await service.analyze(transcript_text, audio, meta)
                    await event_queue.put({"type": "final", "service": service.serviceName, "payload": final_payload})
                    return service.serviceName, final_payload, None
            except Exception as ex:
                await event_queue.put({"type": "error", "service": service.serviceName, "payload": str(ex)})
                logger.error(f"Service {service.serviceName} failed: {ex}", exc_info=True)
                return service.serviceName, {}, str(ex)

        # Start audio analysis (if present) immediately so it can emit partials
        tasks = []
        if self.audio_analysis_service and self.audio_analysis_service.serviceName in services_map:
            tasks.append(asyncio.create_task(_service_stream_to_queue(services_map[self.audio_analysis_service.serviceName])))

        # Start other services (metrics, manipulation, argument)
        tasks.extend(asyncio.create_task(_service_stream_to_queue(service)) for service in ordered)

        total = len(tasks) if tasks else 1
        completed = 0

        # Consume events from the queue until all tasks complete
        pending = set(tasks)
        while pending or not event_queue.empty():
            try:
                ev = await asyncio.wait_for(event_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                # Check if tasks finished without emitting new events
                new_pending = {t for t in pending if not t.done()}
                if not new_pending and event_queue.empty():
                    break
                pending = new_pending
                continue

            ttype = ev.get("type")
            svc = ev.get("service")
            payload = ev.get("payload")

            if ttype == "partial":
                # Emit incremental update for service
                yield {"event": "analysis.update", "service": svc, "payload": payload}
                continue

            if ttype in ("final", "error"):
                # find and remove the finished task
                # mark aggregate
                aggregate["services"][svc] = payload
                if ttype == "error":
                    aggregate["errors"].append({"service": svc, "message": payload})

                # Try to locate the task that returned this service
                done_task = None
                for t in list(pending):
                    if t.done():
                        try:
                            res = t.result()
                            if res and res[0] == svc:
                                done_task = t
                                break
                        except Exception:
                            continue
                if done_task:
                    pending.remove(done_task)

                completed += 1

                yield {
                    "event": "analysis.update",
                    "service": svc,
                    "payload": payload,
                }

                yield {
                    "event": "analysis.progress",
                    "service": svc,
                    "completed": completed,
                    "total": len(tasks),
                }
            # already handled above when processing final/error events

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