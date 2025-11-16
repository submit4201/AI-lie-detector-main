"""Utilities for Server-Sent Events streaming of v2 analysis results."""
from __future__ import annotations

import json
from typing import AsyncGenerator, Dict, Any, Awaitable, Callable, Optional
from fastapi.encoders import jsonable_encoder

from backend.services.v2_services.runner import V2AnalysisRunner


async def stream_runner_events(
    runner: V2AnalysisRunner,
    *,
    transcript: str,
    audio: bytes,
    meta: Dict[str, Any],
    on_event: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
) -> AsyncGenerator[str, None]:
    async for event in runner.stream_run(transcript, audio, meta):
        if on_event is not None:
            await on_event(event)
        # Ensure event is JSON serializable (Pydantic models, mappingproxy, etc.)
        safe = jsonable_encoder(event, by_alias=True, exclude_none=True)
        yield f"data: {json.dumps(safe, ensure_ascii=False)}\n\n"
