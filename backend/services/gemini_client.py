from typing import Optional, Dict, Any
import asyncio


class GeminiClient:
    """Lightweight async stub of a Gemini client used for tests.

    This stub provides deterministic responses for unit tests. In the
    full implementation this client will make async HTTP calls to the
    provider and perform model selection, retries, and streaming.
    """

    def __init__(self):
        pass

    async def transcribe(self, audio_bytes: Optional[bytes]) -> str:
        await asyncio.sleep(0)  # yield control
        if not audio_bytes:
            return ""
        return "[mock transcript] This is a short mocked transcript for tests."

    async def analyze_text(self, prompt: str) -> Dict[str, Any]:
        await asyncio.sleep(0)
        # Return a predictable structure that services can parse
        return {"mocked": True, "text_result": "analysis ok", "prompt_excerpt": prompt[:120]}

    async def query_gemini_for_raw_json(self, prompt: str) -> Any:
        # Provide a simple JSON-like dict as a consistent fallback
        await asyncio.sleep(0)
        return {"talk_to_listen_ratio": 0.45, "speaker_turn_duration_avg_seconds": 6.5, "interruptions_count": 1, "sentiment_trend": []}
