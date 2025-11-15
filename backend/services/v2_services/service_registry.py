"""Registry for v2 AnalysisService implementations.

This centralises knowledge of which services participate in the v2
analysis pipeline so both the runner and API endpoints can construct a
consistent list of service instances for each request.
"""
from __future__ import annotations

from typing import Callable, Dict, Any, Iterable, List, Optional

from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.quantitative_metrics_service import QuantitativeMetricsService

ServiceFactory = Callable[[Dict[str, Any]], AnalysisService]


def _quantitative_metrics_factory(context: Dict[str, Any]) -> AnalysisService:
    return QuantitativeMetricsService(
        gemini_client=context["gemini_client"],
        transcript=context.get("transcript", ""),
        audio_data=context.get("audio"),
        meta=context.get("meta"),
    )


DEFAULT_SERVICE_FACTORIES: List[Callable[[Dict[str, Any]], AnalysisService]] = [
    _quantitative_metrics_factory,
]


def build_service_instances(
    *,
    gemini_client,
    transcript: str,
    audio: Optional[bytes],
    meta: Optional[Dict[str, Any]],
    factories: Optional[Iterable[ServiceFactory]] = None,
) -> List[AnalysisService]:
    """Instantiate all registered services for the current request."""

    context = {
        "gemini_client": gemini_client,
        "transcript": transcript,
        "audio": audio,
        "meta": meta or {},
    }

    active_factories = list(factories) if factories is not None else DEFAULT_SERVICE_FACTORIES
    return [factory(context) for factory in active_factories]
