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

    Implementations should provide an async `analyze` method that accepts
    a transcript (string), optional raw audio bytes, and a metadata dict,
    then returns a dictionary of structured analysis results.

    Optionally services can implement `stream_analyze` to yield partial
    results as they become available.
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
    async def analyze(self, transcript: str, audio: bytes, meta: Dict[str, Any]) -> AnalysisResult:
        """Perform analysis and return a JSON-serializable dict.

        Args:
            transcript: Transcript text (may be empty if audio/diarization provided).
            audio: Raw audio bytes or None.
            meta: Optional additional metadata (duration, speaker info, config overrides).

        Returns:
            A AnalysisResult dict with structured analysis data.
        """
        raise NotImplementedError()

    async def stream_analyze(self, transcript: str, audio: Optional[bytes], meta: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Optional: async generator that yields partial results.

        Default implementation simply yields the full `analyze` result once.
        """
        result = await self.analyze(transcript, audio, meta)
        yield result

    