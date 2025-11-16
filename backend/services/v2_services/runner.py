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
        Runs the full v2 analysis pipeline by consuming stream_run.
        Returns the final aggregated results.
        """
        meta = meta or {}
        start_time = time.time()
        
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
        
        # Phase A: Build AnalysisContext
        ctx = AnalysisContext(
            transcript_partial=transcript or "",
            audio_bytes=audio,
            config=meta.get("config", {}),
            session_summary=meta.get("session_summary"),
        )
        
        # Inject context into meta for services
        meta["analysis_context"] = ctx
        
        # Build service instances
        services_for_request = self._build_services(transcript or "", audio, meta)
        
        # Find specific services
        transcription_svc = next((s for s in services_for_request if s.serviceName == "transcription"), None)
        audio_analysis_svc = next((s for s in services_for_request if s.serviceName == "audio_analysis"), None)
        quantitative_svc = next((s for s in services_for_request if s.serviceName == "quantitative_metrics"), None)
        manipulation_svc = next((s for s in services_for_request if s.serviceName == "manipulation"), None)
        argument_svc = next((s for s in services_for_request if s.serviceName == "argument"), None)
        
        # Phase B: Run foundational services sequentially (for simplicity)
        # Note: True parallel streaming would require more complex orchestration
        
        if transcription_svc and audio and not ctx.transcript_final:
            async for event in self._stream_service(transcription_svc, transcript or "", audio, meta):
                yield event
                
                # Update context based on event
                payload = event.get("payload", {})
                service_name = event.get("service")
                
                if service_name == "transcription":
                    local_data = payload.get("local", {})
                    # Check for transcript in local
                    # For final transcript, prefer "transcript", fallback to "partial_transcript"
                    if not payload.get("partial", True):
                        if local_data.get("transcript"):
                            ctx.transcript_final = local_data["transcript"]
                        elif local_data.get("partial_transcript"):
                            ctx.transcript_final = local_data["partial_transcript"]
                    # For partial transcript, prefer "partial_transcript", fallback to "transcript"
                    else:
                        if local_data.get("partial_transcript"):
                            ctx.transcript_partial = local_data["partial_transcript"]
                        elif local_data.get("transcript"):
                            ctx.transcript_partial = local_data["transcript"]
                    if local_data.get("segments"):
                        ctx.speaker_segments = local_data["segments"]
        
        if audio_analysis_svc and audio:
            async for event in self._stream_service(audio_analysis_svc, transcript or "", audio, meta):
                yield event
                
                # Update context
                payload = event.get("payload", {})
                service_name = event.get("service")
                
                if service_name == "audio_analysis":
                    if payload.get("local"):
                        ctx.audio_summary.update(payload["local"])
        
        # Phase C: Quantitative metrics (if we have enough transcript)
        if quantitative_svc and (ctx.transcript_final or len(ctx.transcript_partial.split()) >= 20):
            effective_transcript = ctx.transcript_final or ctx.transcript_partial
            async for event in quantitative_svc.stream_analyze(effective_transcript, audio, meta):
                yield {
                    "event": "analysis.update",
                    "service": event.get("service_name", "quantitative_metrics"),
                    "payload": event,
                }
                
                # Update context with metrics
                if not event.get("partial", True) and event.get("local"):
                    ctx.quantitative_metrics.update(event["local"])
        
        # Phase D: Higher-level analysis (manipulation and argument)
        # Run sequentially for simplicity
        # Wait until we have minimum context
        if ctx.transcript_final or len(ctx.transcript_partial.split()) >= 30:
            if manipulation_svc:
                async for event in self._stream_service(manipulation_svc, ctx.transcript_final or ctx.transcript_partial, audio, meta):
                    yield event
                    
                    # Store final results in context
                    if not event.get("partial", True):
                        payload = event.get("payload", {})
                        service_name = event.get("service")
                        if service_name and payload:
                            ctx.service_results[service_name] = payload
            
            if argument_svc:
                async for event in self._stream_service(argument_svc, ctx.transcript_final or ctx.transcript_partial, audio, meta):
                    yield event
                    
                    # Store final results in context
                    if not event.get("partial", True):
                        payload = event.get("payload", {})
                        service_name = event.get("service")
                        if service_name and payload:
                            ctx.service_results[service_name] = payload
        
        # Final: Send analysis.done event
        yield {
            "event": "analysis.done",
            "payload": {
                "results": ctx.service_results,
                "meta": {
                    "transcript_final": ctx.transcript_final,
                    "speaker_segments": ctx.speaker_segments,
                    "audio_summary": ctx.audio_summary,
                    "quantitative_metrics": ctx.quantitative_metrics,
                }
            }
        }
    
    async def _stream_service(
        self,
        service: AnalysisService,
        transcript: str,
        audio: Optional[bytes],
        meta: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Helper to stream a single service and wrap results in event format."""
        try:
            async for result in service.stream_analyze(transcript, audio, meta):
                yield {
                    "event": "analysis.update",
                    "service": result.get("service_name", service.serviceName),
                    "payload": result,
                }
        except Exception as e:
            logger.error(f"Service {service.serviceName} streaming failed: {e}", exc_info=True)
            yield {
                "event": "analysis.update",
                "service": service.serviceName,
                "payload": {
                    "service_name": service.serviceName,
                    "errors": [{"error": "Service streaming failed", "details": str(e)}],
                    "partial": False,
                    "phase": "final",
                }
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