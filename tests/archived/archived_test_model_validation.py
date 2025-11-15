import pytest
from pydantic import ValidationError
from backend.models import (
    LinguisticAnalysis,
    RiskAssessment,
    GeminiSummary,
    SessionInsights,
    AudioQualityMetrics,
)


@pytest.mark.unit
@pytest.mark.parametrize("model_cls", [
    LinguisticAnalysis,
    RiskAssessment,
    GeminiSummary,
    SessionInsights,
    AudioQualityMetrics,
])
def test_models_require_fields(model_cls):
    with pytest.raises(ValidationError):
        model_cls(**{})
