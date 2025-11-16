from __future__ import annotations
import json
import logging
from typing import Optional, Dict, Any, AsyncGenerator

from backend.models import ArgumentAnalysis
from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.gemini_client import GeminiClientV2

logger = logging.getLogger(__name__)


class ArgumentService(AnalysisService):
    serviceName = "argument"
    serviceVersion = "2.0"

    def __init__(self, gemini_client: Optional[GeminiClientV2] = None, transcript: str = "", meta: Optional[Dict[str, Any]] = None, **kwargs):
        self.gemini_client = gemini_client or GeminiClientV2()
        super().__init__(transcript=transcript, meta=meta)

    async def analyze(self, transcript: str, audio: Optional[bytes] = None, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not transcript:
            return {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": ArgumentAnalysis().model_dump(),
                "gemini": None,
                "errors": None,
            }

        prompt = f"""Analyze the argument structure of the following transcript and return JSON matching the ArgumentAnalysis model.
Transcript:
"{transcript}"
"""

        try:
            raw = await self.gemini_client.query_json(prompt)
            return {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": {},
                "gemini": raw,
                "errors": None,
            }
        except Exception as e:
            logger.error(f"Argument analysis failed: {e}", exc_info=True)
            return {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": ArgumentAnalysis().model_dump(),
                "gemini": None,
                "errors": [{"error": "Argument analysis failed", "details": str(e)}],
            }

    async def stream_analyze(self, transcript: str, audio: Optional[bytes] = None, meta: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        prompt = f"Analyze the argument structure of the following transcript and return JSON matching the ArgumentAnalysis model.\nTranscript:\n\"{transcript}\"\n"
        try:
            if hasattr(self.gemini_client, 'json_stream'):
                async for chunk in self.gemini_client.json_stream(prompt, audio_bytes=audio):
                    data = chunk.get('data') or {}
                    yield {
                        "service_name": self.serviceName,
                        "service_version": self.serviceVersion,
                        "local": {},
                        "gemini": data,
                        "errors": None,
                    }
                final = await self.analyze(transcript, audio, meta)
                yield final
                return
        except Exception:
            pass

        result = await self.analyze(transcript, audio, meta)
        yield result
