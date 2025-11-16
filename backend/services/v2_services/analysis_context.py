from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class AnalysisContext:
    transcript_partial: str = ""
    transcript_final: Optional[str] = None
    audio_bytes: Optional[bytes] = None
    audio_summary: Dict[str, Any] = field(default_factory=dict)
    quantitative_metrics: Dict[str, Any] = field(default_factory=dict)
    service_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    speaker_segments: List[Dict[str, Any]] = field(default_factory=list)
    session_summary: Optional[Dict[str, Any]] = None
    config: Dict[str, Any] = field(default_factory=dict)

    def update_transcript_partial(self, new_partial: str):
        self.transcript_partial = new_partial

    def finalize_transcript(self, final_text: str):
        self.transcript_final = final_text
        self.transcript_partial = final_text

