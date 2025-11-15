import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.services.linguistic_service import (
    analyze_numerical_linguistic_metrics,
    analyze_linguistic_patterns,
)


def test_analyze_numerical_linguistic_metrics_basic():
    text = "Well, um, I think maybe I was there around 8 PM. I\'m not sure, but I definitely remember it."
    duration = 12.0

    metrics = analyze_numerical_linguistic_metrics(text, duration)

    # Basic type checks
    assert isinstance(metrics, dict)
    assert metrics.get("word_count", 0) > 0

    # Hesitation markers should be detected (um)
    assert metrics.get("hesitation_marker_count", 0) >= 1

    # Formally-scored fields should be in range
    assert 0 <= metrics.get("formality_score_calculated", 0) <= 100
    assert 0 <= metrics.get("complexity_score_calculated", 0) <= 100

    # Speech rate should be computed when duration provided
    assert metrics.get("speech_rate_wpm") is not None
    assert metrics.get("speech_rate_wpm") > 0


def test_analyze_linguistic_patterns_legacy_interface():
    text = "I\'m absolutely sure this happened."
    duration = 5.0

    result = analyze_linguistic_patterns(text, duration)

    # Legacy keys expected
    expected_keys = [
        "word_count",
        "hesitation_count",
        "qualifier_count",
        "certainty_count",
        "filler_count",
        "repetition_count",
        "formality_score",
        "complexity_score",
    ]

    for k in expected_keys:
        assert k in result

    assert result["word_count"] > 0
    # certainty_count should reflect 'absolutely'
    assert result["certainty_count"] >= 1
