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

### V2 Streaming Architecture (CURRENT - Full Implementation)

The v2 API is now the primary path with comprehensive streaming support:

**Core Components:**
- `AnalysisContext`: Central dataclass managing all analysis state without globals
- `AnalysisService` protocol: `stream_analyze` is the primary method, `analyze` wraps it
- `GeminiClientV2.json_stream`: Structured JSON streaming with Live/Simulated providers
- `context_prompts.py`: Helper module for building prompts with strict JSON schemas
- Phased orchestration: A→B→C→D (Input→Foundation→Metrics→HigherLevel)

**Services:**
- All services implement `stream_analyze` and return standardized shape:
  ```python
  {
    "service_name": str,
    "service_version": str,
    "local": dict,        # Computed metrics
    "gemini": dict,       # LLM insights
    "errors": list,
    "partial": bool,      # True for intermediate, False for final
    "phase": str,         # "coarse", "refine", or "final"
    "chunk_index": int | None
  }
  ```

**Orchestration Flow:**
1. **Phase A (Input)**: Create AnalysisContext with request data
2. **Phase B (Foundation)**: Parallel transcription + audio analysis
3. **Phase C (Metrics)**: Quantitative metrics once transcript threshold met
4. **Phase D (Higher-Level)**: Parallel manipulation + argument analysis

**SSE Events:**
- `analysis.update`: Per-service partial or final results
- `analysis.done`: Complete results with aggregated context

See `STREAMING_EVENTS_V2.md` for comprehensive documentation.

### Migration Plan (v1 -> v2)

- ✅ Implement v2 `AnalysisService` protocol (`backend/services/v2_services/analysis_protocol.py`)
- ✅ Create `AnalysisContext` for state management without globals
- ✅ Implement `json_stream` with provider abstraction
- ✅ Migrate `ManipulationService`, `ArgumentService` to v2 streaming
- ✅ `QuantitativeMetricsService`, `AudioAnalysisService`, `TranscriptionService` leverage existing streaming
- ✅ Runner implements phased orchestration with `stream_run`
- ✅ `run` method consumes `stream_run` for consistency
- 🔄 Frontend migration to v2-only (in progress)
- 📝 v1 code remains for compatibility until frontend migration complete

### Streaming and Real-time Transcription

- Use Gemini (google-genai) streaming surfaces where available (`client.aio.live.chat.connect` for audio, `generate_content_stream` for text)
- `json_stream` abstracts provider details (Live vs Simulated)
- Services implement `stream_analyze` to yield incremental results
- Structured JSON output per chunk for reliable parsing
- Fallbacks: simulated streaming via chunked batch results when Live unavailable
- Privacy: transcript partials are short, no sensitive context in logs

### v2 Service Protocol (Expectations)

- Each v2 service must:
  - Implement `stream_analyze` as primary method
  - Be idempotent and thread-safe (no global SDK state)
  - Accept `transcript: str`, `audio: Optional[bytes]`, `meta: Dict[str, Any]`
  - Use `meta["analysis_context"]` for AnalysisContext instance
  - Return standardized dict with `service_name`, `service_version`, `local`, `gemini`, `errors`, `partial`, `phase`, `chunk_index`
  - Provide real streaming when beneficial, minimum pseudo-stream (coarse→final)
  - Not write raw transcripts or audio into logs; use sanitized hashes/sizes only

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
