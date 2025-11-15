# Tests README

## Test Organization

This folder contains tests organized by type and purpose. Tests are categorized using pytest markers and follow a structured organization based on the test audit.

### Test Markers

- **unit** (default): Fast tests with no external dependencies
- **integration**: Tests requiring server/resources; skipped by default
- **slow**: Long-running tests; skipped by default

### Key Fixtures

See `conftest.py` for shared fixtures:
- `project_root` - Repository root path
- `app` - FastAPI application instance
- `client` - Synchronous test client
- `async_client` - Async test client
- `temp_audio` - Generated audio file for tests
- `session_factory` - Helper to create test sessions
- `mock_gemini` - Mock external LLM calls
- `monkeypatch_model_pipeline` - Mock ML model pipeline
- `skip_if_no_external` - Skip tests when dependencies unavailable

### Running Tests

```bash
# Run unit tests only (default)
pytest -q

# Run integration tests
pytest -q -m integration

# Run all tests including integration and slow
pytest -q -m "integration or slow"

# Run specific test file
pytest tests/test_linguistic_service_pytest.py -v

# Collect tests without running
pytest --collect-only
```

## Test Categories (from audit)

### Action: Keep
- **conftest.py** - Shared pytest fixtures
- **test_linguistic_service_pytest.py** - Existing pytest linguistic tests
- **test_py_legacy_runner.py** - Legacy runner compatibility
- **test_archived_placeholder.py** - Placeholder for archived tests
- **test_audio.wav** - Audio asset for tests
- **test_results.json** - Stored test results artifact
- **BasicAnalysisSection.jsx** - Frontend component snippet for tests

### Action: Convert (to pytest)
These tests should be converted to proper pytest format:
- **test_api_structure.py** - Validate structured output keys/types
- **test_default_structure.py** - Default result structure checks
- **test_direct_patterns.py** - Direct pattern detection unit tests
- **test_emotion_fix.py** - Emotion analysis unit tests
- **test_enhanced_analysis.py** - Enhanced analysis functions
- **test_enhanced_formality.py** - Formality scoring units
- **test_enhanced_patterns.py** - Enhanced pattern detection
- **test_formality_analysis.py** - Formality analysis checks
- **test_formality_final.py** - Formality final validations
- **test_linguistic_service.py** - Linguistic service unit tests
- **test_models_alignment.py** - Model alignment checks
- **test_model_validation.py** - Models schema validation
- **test_new_transcript.py** - New transcript parsing checks
- **test_validation.py** - Validation logic checks
- **test_validation_fix.py** - Validation fixes
- **test_validator.py** - Validator behavior

### Action: Integration
Full integration/E2E tests (require server, audio, external models):
- **test_api.py** - API tests incl. websocket/streaming
- **test_api_data_flow_fixed.py** - API data flow happy/edge paths
- **test_api_response.py** - Analyze endpoint JSON schema
- **test_complete_integration.py** - Full system integration
- **test_complete_system.py** - Complete system end-to-end
- **test_complete_validation.py** - Complete validation of outputs
- **test_e2e_session_insights.py** - Session lifecycle insights end-to-end
- **test_final_verification.py** - Final verification flow
- **test_frontend_integration.py** - Frontend-backend integration
- **test_gemini_validation_fixed.py** - Gemini validation with fixes
- **test_realtime_streaming_display.py** - Realtime streaming display
- **test_real_audio_file.py** - Analysis of real audio asset
- **test_real_transcript_insights.py** - Insights from real transcript
- **test_session_comprehensive.py** - Comprehensive session tests
- **test_session_creation_comprehensive.py** - Session creation flows
- **test_session_creation_fix.py** - Session creation fixes
- **test_streaming_comprehensive.py** - Comprehensive streaming tests
- **test_streaming_integration.py** - Streaming integration tests
- **test_streaming_simple.py** - Simple streaming tests
- **test_updated_backend.py** - Updated backend checks
- **test_updated_backend_clean.py** - Updated backend checks (clean)
- **test_websocket_streaming.py** - WebSocket streaming tests

### Action: Archive
Legacy scripts, demos, and superseded tests (moved to `archived/` folder):
- Debug scripts (debug_data_structure.py, debug_emotion_analysis.py)
- Demo scripts (demo_enhanced_insights.py, demo_streaming_success.py)
- Legacy runners (master_test_runner.py, quick_backend_test.py, run_backend_validation.py)
- Helper pipeline layers (layer_1_input.py, layer_2_feature_extraction.py, layer_3_feature_assembler.py)
- Superseded tests (test_api_data_flow.py, test_gemini_validation.py, test_session_history_debug.py)

### Dependencies by Test Type

- **No deps (unit)**: test_api_structure, test_default_structure, test_direct_patterns, test_enhanced_analysis, test_enhanced_patterns, test_linguistic_service, test_models_alignment, test_model_validation, test_new_transcript, test_validation, test_validator
- **fastapi**: Most integration tests
- **audio**: Tests with audio file processing
- **external_models**: Tests requiring ML models (emotion, formality analysis)
- **external_llm**: Tests requiring Gemini/LLM API
- **network**: Streaming and websocket tests
- **frontend**: Frontend integration tests

### Test Assets

- **test_extras/** - Audio and video samples for testing
- **generated_files/** - Generated test artifacts (API responses, validation results)
