<general_rules>
When creating new functions or modules, always first search in the relevant `backend/` or `frontend/` subdirectories to see if similar functionality exists. If not, create it and place it in an existing or new file that logically groups related code.

For frontend development, ensure your code adheres to the ESLint rules defined in `frontend/eslint.config.js`. You can run the linter using `npm run lint` in the `frontend/` directory.
</general_rules>

<repository_structure>
The repository is structured into two main applications: `backend` and `frontend`, along with a `tests` directory for comprehensive testing and a `memory` directory for project documentation and notes.

-   **`backend/`**: This directory contains the Python-based FastAPI application. It's responsible for core AI logic, speech processing, session management, and exposing API endpoints. Key subdirectories include `api/` for route definitions and `services/` for business logic and integrations (e.g., `gemini_service.py`, `audio_analysis_service.py`).
-   **`frontend/`**: This directory houses the React application built with Vite. It provides the user interface for interacting with the backend, including audio input, real-time analysis display, and session management.
-   **`tests/`**: Contains various test scripts for both backend and frontend components, including unit, integration, and end-to-end tests. The `master_test_runner.py` orchestrates the execution of these tests.
-   **`memory/`**: Stores project-related documentation, summaries, and todo lists.
</repository_structure>

<dependencies_and_installation>
Dependencies are managed separately for the backend and frontend.

-   **Backend (Python)**:
    *   Dependencies are listed in `backend/requirements.txt`.
    *   To install, navigate to the `backend/` directory and run `pip install -r requirements.txt`.
-   **Frontend (Node.js/React)**:
    *   Dependencies are listed in `frontend/package.json`.
    *   To install, navigate to the `frontend/` directory and run `npm install` (or `yarn install` if using Yarn).
</dependencies_and_installation>

<testing_instructions>
The repository utilizes pytest for running tests. Tests are organized in the `tests/` directory with markers for different test types.

-   **Test Markers**:
    *   `unit` (default): Fast tests with no external dependencies
    *   `integration`: Tests requiring server/resources; skipped by default
    *   `slow`: Long-running tests; skipped by default
    
-   **Running Tests**:
    *   Run unit tests only: `pytest -q` or `pytest tests/`
    *   Run integration tests: `pytest -q -m integration`
    *   Run all tests: `pytest -q -m "integration or slow"`
    *   Run specific test file: `pytest tests/test_direct_patterns.py -v`
    *   Collect tests without running: `pytest --collect-only`

-   **Test Organization** (see tests/README.md for full legend):
    *   Unit tests: test_default_structure.py, test_direct_patterns.py, test_linguistic_service_pytest.py, test_session_utils.py
    *   Integration tests: test_api.py, test_api_structure.py, test_complete_integration.py, test_streaming_*.py
    *   Legacy/archived tests: Located in tests/archived/ folder

-   **Test Frameworks**:
    *   Backend tests (Python) use `pytest` with fixtures defined in `tests/conftest.py`
    *   Frontend tests (React) are not explicitly defined with a testing framework yet

-   **Test Scope**: Tests cover backend API functionality, linguistic analysis, data structure validation, session management, and streaming capabilities.
</testing_instructions>

<pull_request_formatting>
</pull_request_formatting>

