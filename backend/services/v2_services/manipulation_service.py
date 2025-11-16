from __future__ import annotations
import json
import logging
from typing import Optional, Dict, Any, AsyncGenerator

from backend.models import ManipulationAssessment
from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.gemini_client import GeminiClientV2

logger = logging.getLogger(__name__)


class ManipulationService(AnalysisService):
    serviceName = "manipulation"
    serviceVersion = "2.0"

    def __init__(self, gemini_client: Optional[GeminiClientV2] = None, transcript: str = "", meta: Optional[Dict[str, Any]] = None, **kwargs):
        self.gemini_client = gemini_client or GeminiClientV2()
        super().__init__(transcript=transcript, meta=meta)

    async def analyze(self, transcript: str, audio: Optional[bytes] = None, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not transcript:
            return {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": ManipulationAssessment().model_dump(),
                "gemini": None,
                "errors": None,
            }

        prompt = f"""Analyze the following transcript for signs of manipulation.
Transcript:
"{transcript}"

Provide a JSON object that matches the ManipulationAssessment model shape.
"""

        try:
            raw = await self.gemini_client.query_json(prompt)
            if isinstance(raw, dict):
                return {
                    "service_name": self.serviceName,
                    "service_version": self.serviceVersion,
                    "local": {},
                    "gemini": raw,
                    "errors": None,
                }
            # fallback to local
            return {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": ManipulationAssessment().model_dump(),
                "gemini": None,
                "errors": None,
            }
        except Exception as e:
            logger.error(f"Manipulation analysis failed: {e}", exc_info=True)
            return {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": ManipulationAssessment().model_dump(),
                "gemini": None,
                "errors": [{"error": "Manipulation analysis failed", "details": str(e)}],
            }

    async def stream_analyze(self, transcript: str, audio: Optional[bytes] = None, meta: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        # This service is not incremental by default. Keep default behavior for now.
        result = await self.analyze(transcript, audio, meta)
        yield result
