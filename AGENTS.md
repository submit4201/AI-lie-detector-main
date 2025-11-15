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
The repository utilizes a `master_test_runner.py` script located in the `tests/` directory to manage and execute tests.

-   **Running All Tests**: To run the entire test suite, execute `python tests/master_test_runner.py` from the root of the repository.
-   **Running Specific Test Categories**: The `master_test_runner.py` organizes tests into categories (e.g., `backend_validation`, `api_tests`, `service_tests`, `analysis_tests`, `session_tests`, `streaming_tests`). You can run a specific category by providing its name as an argument: `python tests/master_test_runner.py <category_name>`.
-   **Listing Test Categories**: To see a list of available test categories, run `python tests/master_test_runner.py --list`.
-   **Test Frameworks**:
    *   Backend tests (Python) appear to use standard Python testing practices, likely leveraging `unittest` or `pytest` implicitly, as indicated by the structure of the test files.
    *   Frontend tests (React) are not explicitly defined with a specific testing framework in `package.json`, but the `eslint` configuration suggests a focus on code quality.
-   **Test Scope**: Tests cover various aspects, including backend API functionality, individual service logic, data flow, session management, and streaming capabilities.
</testing_instructions>

<pull_request_formatting>
</pull_request_formatting>

