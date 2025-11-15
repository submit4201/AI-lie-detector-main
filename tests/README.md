# Tests README

Markers:
- unit (default): fast, no external deps
- integration: requires server/resources; skipped by default
- slow: long-running; skipped by default

Key fixtures (see conftest.py): project_root, app, client, async_client, temp_audio, session_factory, mock_gemini, monkeypatch_model_pipeline, skip_if_no_external.

Run:
- pytest -q (unit only)
- pytest -q -m integration
- pytest -q -m "integration or slow"
