<general_rules>
When creating new functions or modules, always first search in the relevant `backend/` or `frontend/` subdirectories to see if similar functionality exists. If not, create it and place it in an existing or new file that logically groups related code.

For frontend development, ensure your code adheres to the ESLint rules defined in `frontend/eslint.config.js`. You can run the linter using `npm run lint` in the `frontend/` directory.
</general_rules>

<repository_structure>
The repository is structured into two main applications: `backend` and `frontend`, along with a `tests` directory for comprehensive testing and a `memory` directory for project documentation and notes.

- **`backend/`**: This directory contains the Python-based FastAPI application. It's responsible for core AI logic, speech processing, session management, and exposing API endpoints. Key subdirectories include `api/` for route definitions and `services/` for business logic and integrations (e.g., `gemini_service.py`, `audio_analysis_service.py`).
- **`frontend/`**: This directory houses the React application built with Vite. It provides the user interface for interacting with the backend, including audio input, real-time analysis display, and session management.
- **`tests/`**: Contains various test scripts for both backend and frontend components, including unit, integration, and end-to-end tests. The `master_test_runner.py` orchestrates the execution of these tests.
- **`memory/`**: Stores project-related documentation, summaries, and todo lists.
</repository_structure>

<dependencies_and_installation>
Dependencies are managed separately for the backend and frontend.

- **Backend (Python)**:

- Dependencies are listed in `backend/requirements.txt`.
- To install, navigate to the `backend/` directory and run `pip install -r requirements.txt`.

- **Frontend (Node.js/React)**:

- Dependencies are listed in `frontend/package.json`.
- To install, navigate to the `frontend/` directory and run `npm install` (or `yarn install` if using Yarn).
</dependencies_and_installation>

<testing_instructions>
The repository utilizes pytest for running tests. Tests are organized in the `tests/` directory with markers for different test types.

- **Test Markers**:

- `unit` (default): Fast tests with no external dependencies
- `integration`: Tests requiring server/resources; skipped by default
- `slow`: Long-running tests; skipped by default

- **Running Tests**:
  - Run unit tests only: `pytest -q` or `pytest tests/`
  - Run integration tests: `pytest -q -m integration`
  - Run all tests: `pytest -q -m "integration or slow"`
  - Run specific test file: `pytest tests/test_direct_patterns.py -v`
  - Collect tests without running: `pytest --collect-only`

- **Test Organization** (see tests/README.md for full legend):

- Unit tests: test_default_structure.py, test_direct_patterns.py, test_linguistic_service_pytest.py, test_session_utils.py
- Integration tests: test_api.py, test_api_structure.py, test_complete_integration.py, test_streaming_*.py
- Legacy/archived tests: Located in tests/archived/ folder

- **Test Frameworks**:

- Backend tests (Python) use `pytest` with fixtures defined in `tests/conftest.py`
- Frontend tests (React) are not explicitly defined with a testing framework yet

- **Test Scope**: Tests cover backend API functionality, linguistic analysis, data structure validation, session management, and streaming capabilities.
</testing_instructions>

<v2_migration_plans>

## Migration & v2 service design / expectations

### Migration Plan (v1 -> v2)

- Implement v2 `AnalysisService` protocol (`backend/services/v2_services/analysis_protocol.py`) and migrate services to implement this interface.
- Migrate `ManipulationService`, `ArgumentService`, `QuantitativeMetricsService`, and `AudioAnalysisService` to v2. Keep v1 code in `backend/services/archived/` until v2 is validated.
- Ensure v2 services accept a `GeminiClientV2` to centralize LLM calls, and avoid global or per-service state to make services testable.
- Add per-service unit tests first, then runner-level tests. Only archive v1 code after v2 provides matching or improved functionality and tests are green.

### Streaming and Real-time Transcription

- Use Gemini (google-genai) streaming surfaces where available (`client.aio.live.chat.connect` for audio, `generate_content_stream` for text). See `structured_streaming_output_for_gemini_example.py` for a reference implementation and structured output examples.
- Services should support an optional `stream_analyze(transcript, audio, meta)` async generator to yield incremental results. This allows the runner to stream partial transcripts and per-service progress to the frontend.
- Prefer structured JSON output in streaming calls (e.g., JSON per chunk) rather than free-form text to make parsing reliable and reduce post-processing.
- When SDK streaming is unavailable, implement a safe fallback that yields a small interim event followed by the final result (this preserves UX without breaking the connector).
- Keep transcript partials short and avoid sending sensitive context or audio data in interim events.

### v2 Service Protocol (Expectations)

- Each v2 service must:
  - Be idempotent and thread-safe (no global SDK state)
  - Accept `transcript: str`, `audio: Optional[bytes]`, `meta: Dict[str, Any]`
  - Return a dict containing `service_name`, `service_version`, `local` and `gemini` keys (use `local` for metrics and `gemini` for LLM outputs)
  - Provide `stream_analyze` if service benefits from incremental outputs (transcription, large LLM analysis)
  - Not write raw transcripts or audio into logs; use sanitized contextual hashes or sizes only

### Archiving v1

- Only archive the v1 module once:
    1. v2 implementation of the same service exists and is covered by unit tests.
    2. Integration tests (v2 runner and v2 /v2/analyze endpoints) validate that v1 behavior is covered or improved.
    3. Update documentation (`AGENTS.md`) to mark v1 archived and provide a migration summary for users.
</v2_migration_plans>

<pull_request_formatting>

### Pull Request Template

#### Summary

- Provide a concise overview of the changes and their motivation.

#### Related Issues

- Closes #

#### Changes

- Backend:
- Frontend:
- Documentation:
- Other:

#### Testing

- [ ] `pytest`
- [ ] `pytest -m integration`
- [ ] `npm run test -- --run`
- [ ] Additional coverage details:

#### Deployment

- Outline any deployment steps or migration notes.

#### Checklist

- [ ] Added or updated automated tests
- [ ] Ran linters (`npm run lint`, `pytest --collect-only`)
- [ ] Updated documentation or release notes as needed
- [ ] Verified backward compatibility and configuration impacts

</pull_request_formatting>
