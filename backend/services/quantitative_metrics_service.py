"""Deprecated shim for the legacy QuantitativeMetricsService import path.

The v1 implementation now lives in backend.services.archived.quantitative_metrics_service_v1
for reference only. Runtime code should depend on backend.services.v2_services.
"""

from backend.services.v2_services.quantitative_metrics_service import QuantitativeMetricsService  # noqa: F401
