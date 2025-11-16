from __future__ import annotations
import json
import logging
from typing import Optional, Dict, Any, AsyncGenerator

from backend.models import ArgumentAnalysis
from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.gemini_client import GeminiClientV2
from backend.services.v2_services.context_prompts import build_argument_prompt

logger = logging.getLogger(__name__)


class ArgumentService(AnalysisService):
    serviceName = "argument"
    serviceVersion = "2.0"

    def __init__(self, gemini_client: Optional[GeminiClientV2] = None, transcript: str = "", meta: Optional[Dict[str, Any]] = None, **kwargs):
        self.gemini_client = gemini_client or GeminiClientV2()
        super().__init__(transcript=transcript, meta=meta)

    async def stream_analyze(self, transcript: str, audio: Optional[bytes] = None, meta: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream argument structure analysis with coarse and final phases."""
        meta = meta or {}
        ctx = meta.get("analysis_context")
        
        if not transcript and not (ctx and (ctx.transcript_partial or ctx.transcript_final)):
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": ArgumentAnalysis().model_dump(),
                "gemini": None,
                "errors": [{"error": "No transcript available"}],
                "partial": False,
                "phase": "final",
                "chunk_index": None,
            }
            return
        
        # Update context if provided
        if ctx:
            ctx.transcript_partial = ctx.transcript_partial or transcript
            if not ctx.transcript_final and len(transcript) > len(ctx.transcript_partial):
                ctx.transcript_partial = transcript
        
        # Get effective transcript
        effective_transcript = transcript
        if ctx:
            effective_transcript = ctx.transcript_final or ctx.transcript_partial or transcript
        
        if not effective_transcript or len(effective_transcript.split()) < 10:
            # Not enough data yet
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": {"status": "waiting_for_data"},
                "gemini": None,
                "errors": [],
                "partial": True,
                "phase": "coarse",
                "chunk_index": 0,
            }
            return
        
        # Phase 1: Coarse analysis
        try:
            prompt, schema = build_argument_prompt(ctx or type('obj', (object,), {
                'transcript_partial': effective_transcript,
                'transcript_final': None,
                'audio_bytes': audio,
                'audio_summary': {},
                'quantitative_metrics': {},
                'service_results': {},
                'speaker_segments': [],
                'session_summary': None,
                'config': {}
            })(), phase="coarse")
            
            chunk_index = 0
            accumulated_data = {}
            
            async for stream_chunk in self.gemini_client.json_stream(
                prompt=prompt,
                schema=schema,
                audio_bytes=audio,
                context=meta
            ):
                if stream_chunk.get("done"):
                    break
                
                chunk_data = stream_chunk.get("data", {})
                accumulated_data.update(chunk_data)
                
                yield {
                    "service_name": self.serviceName,
                    "service_version": self.serviceVersion,
                    "local": {},
                    "gemini": accumulated_data,
                    "errors": [],
                    "partial": True,
                    "phase": "coarse",
                    "chunk_index": chunk_index,
                }
                chunk_index += 1
            
            # Phase 2: Final analysis if we have final transcript
            if ctx and ctx.transcript_final:
                prompt_final, schema_final = build_argument_prompt(ctx, phase="final")
                
                final_data = {}
                async for stream_chunk in self.gemini_client.json_stream(
                    prompt=prompt_final,
                    schema=schema_final,
                    audio_bytes=audio,
                    context=meta
                ):
                    chunk_data = stream_chunk.get("data", {})
                    final_data.update(chunk_data)
                    
                    if stream_chunk.get("done"):
                        break
                    
                    yield {
                        "service_name": self.serviceName,
                        "service_version": self.serviceVersion,
                        "local": {},
                        "gemini": final_data,
                        "errors": [],
                        "partial": not stream_chunk.get("done"),
                        "phase": "final",
                        "chunk_index": chunk_index,
                    }
                    chunk_index += 1
                
                # Store in context
                if ctx:
                    ctx.service_results["argument"] = final_data
                
                # Final result
                yield {
                    "service_name": self.serviceName,
                    "service_version": self.serviceVersion,
                    "local": {},
                    "gemini": final_data,
                    "errors": [],
                    "partial": False,
                    "phase": "final",
                    "chunk_index": chunk_index,
                }
            else:
                # No final transcript yet
                if ctx:
                    ctx.service_results["argument"] = accumulated_data
                    
                yield {
                    "service_name": self.serviceName,
                    "service_version": self.serviceVersion,
                    "local": {},
                    "gemini": accumulated_data,
                    "errors": [],
                    "partial": False,
                    "phase": "coarse",
                    "chunk_index": chunk_index,
                }
                
        except Exception as e:
            logger.error(f"Argument streaming analysis failed: {e}", exc_info=True)
            yield {
                "service_name": self.serviceName,
                "service_version": self.serviceVersion,
                "local": ArgumentAnalysis().model_dump(),
                "gemini": None,
                "errors": [{"error": "Argument analysis failed", "details": str(e)}],
                "partial": False,
                "phase": "final",
                "chunk_index": None,
            }
