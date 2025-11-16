from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, AsyncGenerator

class AnalysisResult(Dict[str, Any]):
    """Type alias for analysis result dictionaries.

    This simple typed dict collects commonly expected fields. Concrete
    services may add domain-specific keys inside the payload.
    """
    pass

class AnalysisService(ABC):
    """Abstract interface for analysis services.

    The v2 protocol is streaming-first: `stream_analyze` is the primary method
    that yields incremental results. The `analyze` method is a convenience wrapper
    that consumes the full stream and returns the final result.
    
    Each result dict must include:
    - service_name: str
    - service_version: str
    - local: dict (local/computed metrics)
    - gemini: dict (LLM-generated insights)
    - errors: list
    - partial: bool (True for intermediate chunks, False for final)
    - phase: str (e.g., "coarse", "refine", "final")
    - chunk_index: int | None
    """   
    # required variables and methods for analysis services
    serviceName: str
    serviceVersion: str

    # required attributes
    def __init__(self, transcript: str = "", audio_data: Optional[bytes] = None, meta: Optional[Dict[str, Any]] = None) -> None:
        super().__init__()
        self.transcript: str = transcript
        self.audio_data: Optional[bytes] = audio_data
        self.meta: Dict[str, Any] = meta or {}

    @abstractmethod
    async def stream_analyze(self, transcript: str, audio: Optional[bytes], meta: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Primary method: async generator that yields partial and final results.
        
        Services should implement real streaming when possible. At minimum,
        yield intermediate "coarse" results followed by a final result.

        Args:
            transcript: Transcript text (may be empty if audio/diarization provided).
            audio: Raw audio bytes or None.
            meta: Metadata dict that includes "analysis_context" with AnalysisContext instance.

        Yields:
            Dicts with standardized v2 result shape including partial/phase/chunk_index.
        """
        raise NotImplementedError()

    async def analyze(self, transcript: str, audio: Optional[bytes], meta: Dict[str, Any]) -> AnalysisResult:
        """Convenience method: consumes stream_analyze and returns final result.

        Default implementation iterates through stream_analyze and returns
        the last yielded result (which should have partial=False).
        """
        result = None
        async for chunk in self.stream_analyze(transcript, audio, meta):
            result = chunk
        return result or {
            "service_name": self.serviceName,
            "service_version": self.serviceVersion,
            "local": {},
            "gemini": None,
            "errors": [{"error": "No results produced"}],
            "partial": False,
            "phase": "final",
            "chunk_index": None,
        }

    