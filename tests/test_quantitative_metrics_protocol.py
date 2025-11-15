import asyncio

from backend.services.quantitative_metrics_service import QuantitativeMetricsService
from backend.services.gemini_client import GeminiClient


def test_quantitative_metrics_analyze_basic():
    """Ensure QuantitativeMetricsService implements analyze and returns expected keys."""
    client = GeminiClient()
    svc = QuantitativeMetricsService(gemini_service=client)

    result = asyncio.run(svc.analyze("This is a short test transcript.", None, {}))

    assert isinstance(result, dict), "analyze must return a dict"
    assert "interaction_metrics" in result, "result should include 'interaction_metrics'"
    assert "numerical_linguistic_metrics" in result, "result should include 'numerical_linguistic_metrics'"
