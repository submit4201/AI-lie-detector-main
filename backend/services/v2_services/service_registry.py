"""Registry for v2 AnalysisService implementations.

This centralises knowledge of which services participate in the v2
analysis pipeline so both the runner and API endpoints can construct a
consistent list of service instances for each request.
"""
from __future__ import annotations

from typing import Callable, Dict, Any, Iterable, List, Optional

from backend.services.v2_services.analysis_protocol import AnalysisService
from backend.services.v2_services.gemini_client import GeminiClientV2
from backend.services.v2_services.quantitative_metrics_service import QuantitativeMetricsService
from backend.services.v2_services.transcription_service import TranscriptionService
from backend.services.v2_services.audio_analysis_service import AudioAnalysisService

ServiceFactory = Callable[[Dict[str, Any]], AnalysisService]

#################
# v2: use a consistent GeminiClientV2 passed in the request context.
# The v2 runner and the service factories accept a context dict so tests
# can inject fake or mock clients into every service instance. This avoids
# noisy global state in the SDK and makes unit tests deterministic.
#################

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

# Mapping from service name to a factory function that returns a service instance.
# A factory is used to allow for dependency injection and context-passing at runtime.
SERVICE_FACTORIES: Dict[str, Callable[[Dict[str, Any]], AnalysisService]] = {
    "transcription": lambda context: TranscriptionService(
        gemini_client=context.get("gemini_client"),
        transcript=context.get("transcript", ""),
        meta=context.get("meta", {}),
    ),
    "audio_analysis": lambda context: AudioAnalysisService(
        transcript=context.get("transcript", ""),
        audio_data=context.get("audio"),
        meta=context.get("meta", {}),
    ),
    "quantitative_metrics": lambda context: QuantitativeMetricsService(
        gemini_client=context.get("gemini_client"),
        transcript=context.get("transcript", ""),
        audio_data=context.get("audio"),
        meta=context.get("meta", {}),
    ),
    "manipulation": lambda context: __import__('backend.services.v2_services.manipulation_service', fromlist=['ManipulationService']).ManipulationService(
        gemini_client=context.get("gemini_client"),
        transcript=context.get("transcript", ""),
        meta=context.get("meta", {}),
    ),
    "argument": lambda context: __import__('backend.services.v2_services.argument_service', fromlist=['ArgumentService']).ArgumentService(
        gemini_client=context.get("gemini_client"),
        transcript=context.get("transcript", ""),
        meta=context.get("meta", {}),
    ),
    "speaker_attitude": lambda context: __import__('backend.services.v2_services.speaker_attitude_service', fromlist=['SpeakerAttitudeServiceV2']).SpeakerAttitudeServiceV2(
        gemini_client=context.get("gemini_client"),
        transcript=context.get("transcript", ""),
        meta=context.get("meta", {}),
    ),
    "psychological": lambda context: __import__('backend.services.v2_services.psychological_service', fromlist=['PsychologicalServiceV2']).PsychologicalServiceV2(
        gemini_client=context.get("gemini_client"),
        transcript=context.get("transcript", ""),
        meta=context.get("meta", {}),
    ),
    "enhanced_understanding": lambda context: __import__('backend.services.v2_services.enhanced_understanding_service', fromlist=['EnhancedUnderstandingServiceV2']).EnhancedUnderstandingServiceV2(
        gemini_client=context.get("gemini_client"),
        transcript=context.get("transcript", ""),
        meta=context.get("meta", {}),
    ),
    "conversation_flow": lambda context: __import__('backend.services.v2_services.conversation_flow_service', fromlist=['ConversationFlowServiceV2']).ConversationFlowServiceV2(
        gemini_client=context.get("gemini_client"),
        transcript=context.get("transcript", ""),
        meta=context.get("meta", {}),
    ),
    "session_insights": lambda context: __import__('backend.services.v2_services.session_insights_service', fromlist=['SessionInsightsServiceV2']).SessionInsightsServiceV2(
        transcript=context.get("transcript", ""),
        meta=context.get("meta", {}),
    ),
    "linguistic": lambda context: __import__('backend.services.v2_services.linguistic_service', fromlist=['LinguisticServiceV2']).LinguisticServiceV2(
        gemini_client=context.get("gemini_client"),
        transcript=context.get("transcript", ""),
        meta=context.get("meta", {}),
    ),
    "enhanced_acoustic": lambda context: __import__('backend.services.v2_services.enhanced_acoustic_service', fromlist=['EnhancedAcousticService']).EnhancedAcousticService(
        transcript=context.get("transcript", ""),
        audio_data=context.get("audio"),
        meta=context.get("meta", {}),
    ),
    "credibility_scoring": lambda context: __import__('backend.services.v2_services.credibility_scoring_service', fromlist=['CredibilityScoringService']).CredibilityScoringService(
        baseline_profile=context.get("meta", {}).get("baseline_profile"),
        transcript=context.get("transcript", ""),
        meta=context.get("meta", {}),
    ),
    # All v1 services now have v2 equivalents + advanced credibility analysis
}

REGISTERED_SERVICES: List[Callable[[Dict[str, Any]], AnalysisService]] = [
    SERVICE_FACTORIES["transcription"],
    SERVICE_FACTORIES["audio_analysis"],
    SERVICE_FACTORIES["quantitative_metrics"],
    SERVICE_FACTORIES["manipulation"],
    SERVICE_FACTORIES["argument"],
]
