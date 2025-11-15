from __future__ import annotations

import asyncio
import time
from typing import Dict, Any, Optional, List, AsyncGenerator, Tuple

from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.gemini_client import GeminiClientV2
from backend.services.v2_services.service_registry import build_service_instances, ServiceFactory


class V2AnalysisRunner:
    """Coordinator for v2 AnalysisService implementations."""

    def __init__(
        self,
        *,
        gemini_client: Optional[GeminiClientV2] = None,
        service_factories: Optional[List[ServiceFactory]] = None,
    ) -> None:
        self.gemini_client = gemini_client or GeminiClientV2()
        self.service_factories = service_factories

    async def _ensure_transcript(self, transcript: str, audio: Optional[bytes], meta: Dict[str, Any]) -> Tuple[str, bool]:
        if transcript:
            return transcript, False
        if not audio:
            raise ValueError("Transcript or audio bytes are required for analysis")

        mime_type = meta.get("audio_mime_type") or meta.get("content_type")
        transcript_text = await self.gemini_client.transcribe(audio, mime_type=mime_type)
        return transcript_text, True

    def _build_services(self, transcript: str, audio: Optional[bytes], meta: Dict[str, Any]) -> List[AnalysisService]:
        return build_service_instances(
            gemini_client=self.gemini_client,
            transcript=transcript,
            audio=audio,
            meta=meta,
            factories=self.service_factories,
        )

    async def _execute_service(
        self,
        service: AnalysisService,
        transcript: str,
        audio: Optional[bytes],
        meta: Dict[str, Any],
    ) -> Tuple[str, Dict[str, Any], Optional[str]]:
        service_name = getattr(service, "serviceName", service.__class__.__name__)
        start = time.perf_counter()
        try:
            payload = await service.analyze(transcript, audio, meta)
            error_message = None
        except Exception as exc:  # pragma: no cover - defensive
            error_message = str(exc)
            payload = {
                "service_name": service_name,
                "service_version": getattr(service, "serviceVersion", "unknown"),
                "local": {},
                "gemini": {},
                "errors": error_message,
            }

        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        payload.setdefault("timings", {})["latency_ms"] = latency_ms
        return service_name, payload, error_message

    async def run(
        self,
        transcript: str,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run all registered services and aggregate their results."""

        meta = meta or {}
        transcript_text, generated = await self._ensure_transcript(transcript, audio, meta)
        services = self._build_services(transcript_text, audio, meta)

        tasks = [
            self._execute_service(service, transcript_text, audio, meta)
            for service in services
        ]
        results = await asyncio.gather(*tasks)

        aggregate = {
            "transcript": transcript_text,
            "services": {},
            "errors": [],
            "meta": {**meta, "transcript_auto_generated": generated},
        }

        for service_name, payload, error_message in results:
            aggregate["services"][service_name] = payload
            if error_message:
                aggregate["errors"].append({"service": service_name, "message": error_message})

        return aggregate

    async def stream_run(
        self,
        transcript: str,
        audio: Optional[bytes] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Yield incremental service results for streaming responses."""

        meta = meta or {}
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