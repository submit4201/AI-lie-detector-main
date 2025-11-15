# GitHub Copilot Instructions for AI Lie Detector

## Project Overview

The AI Lie Detector is a sophisticated voice analysis application combining advanced AI models, speech recognition, and linguistic analysis to detect deception patterns in human speech. The system provides comprehensive real-time analysis with structured outputs, session management, and detailed reporting capabilities.

## Repository Structure

This is a full-stack application with two main components:

### Backend (`backend/`)
- **Framework**: FastAPI with Pydantic for data validation
- **Language**: Python 3.12+
- **AI Integration**: Google Gemini AI for deception analysis
- **Speech Processing**: SpeechRecognition library with Google Speech-to-Text
- **Audio Processing**: PyDub for audio quality assessment
- **Session Management**: In-memory conversation tracking
- **Port**: `http://localhost:8000`

Key subdirectories:
- `api/`: Route definitions and API endpoints
- `services/`: Business logic (e.g., `gemini_service.py`, `audio_analysis_service.py`, `linguistic_service.py`, `manipulation_service.py`, `psychological_service.py`)
- `models.py`: Pydantic data models
- `config.py`: Configuration settings

### Frontend (`frontend/`)
- **Framework**: React 18 with Vite build system
- **Language**: JavaScript/JSX
- **UI Library**: Tailwind CSS with shadcn/ui components
- **State Management**: Custom React hooks
- **Audio Handling**: Browser MediaRecorder API
- **Port**: `http://localhost:5175`

### Tests (`tests/`)
- Unit tests, integration tests, and end-to-end tests
- See `TESTING.md` for comprehensive testing documentation

### Documentation (`memory/`)
- Project documentation, summaries, and notes
- Refer to `AGENTS.md` for additional repository guidelines

## Code Style and Standards

### General Rules
1. When creating new functions or modules, **always search first** in `backend/` or `frontend/` subdirectories to check if similar functionality exists
2. Place new code in existing or new files that logically group related functionality
3. Follow existing code patterns and conventions in the repository

### Frontend
- Adhere to ESLint rules defined in `frontend/eslint.config.js`
- Run linter: `cd frontend && npm run lint`
- Use functional components with hooks
- Follow React best practices
- Maintain responsive design principles

### Backend
- Follow PEP 8 style guidelines for Python code
- Use type hints for function parameters and return values
- Use Pydantic models for data validation
- Keep services modular and focused on single responsibilities
- Handle errors gracefully with meaningful error messages

## Dependencies and Installation

### Backend (Python)
- Dependencies: `backend/requirements.txt` (production) and `backend/requirements-dev.txt` (development)
- Install: `cd backend && pip install -r requirements.txt`
- Key dependencies: fastapi, pydantic, google-genai, speechrecognition, pydub, python-dotenv

### Frontend (Node.js/React)
- Dependencies: `frontend/package.json`
- Install: `cd frontend && npm install`
- Key dependencies: react, vite, tailwindcss, @radix-ui, lucide-react

## Testing

The project uses pytest (backend) and Vitest (frontend). Tests are organized with markers:

### Test Markers (Backend)
- `@pytest.mark.unit` - Fast tests with no external dependencies (default)
- `@pytest.mark.integration` - Tests requiring server/resources; skipped by default
- `@pytest.mark.slow` - Long-running tests; skipped by default

### Running Tests

**Backend:**
```bash
# Run unit tests only (default)
pytest

# Run with coverage
pytest --cov=backend --cov-report=term-missing

# Run integration tests
pytest -m integration

# Run all tests
pytest -m ""

# Run specific test file
pytest tests/test_linguistic_service_unit.py -v
```

**Frontend:**
```bash
cd frontend

# Run tests in watch mode
npm test

# Run tests once
npm test -- --run

# Run with coverage
npm run test:coverage
```

### Test Organization
- Unit tests: `test_session_utils.py`, `test_linguistic_service_unit.py`, `test_manipulation_service_unit.py`, `test_psychological_service_unit.py`, `test_direct_patterns.py`, `test_default_structure.py`
- Integration tests: `test_api.py`, `test_streaming_*.py`, `test_complete_integration.py`
- Frontend tests: Co-located with components (e.g., `badge.test.jsx`)
- Archived tests: Located in `tests/archived/` (not run by default)

### Writing Tests
- **Always** write tests for new functionality
- Follow TDD approach when possible
- Maintain or improve code coverage
- Test edge cases (empty input, None, special characters)
- Keep tests independent and isolated
- See `TESTING.md` for comprehensive testing guide

## Building and Running

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Important Files and Documentation

- `AGENTS.md` - Repository structure, dependencies, testing instructions, and general rules
- `TESTING.md` - Comprehensive testing guide with examples
- `AI_LIE_DETECTOR_PROJECT_OVERVIEW.md` - Complete system architecture and feature documentation
- `SECURITY.md` - Security guidelines and vulnerability reporting
- `pytest.ini` - Backend test configuration
- `.coveragerc` - Backend coverage configuration
- `vitest.config.js` - Frontend test configuration
- `eslint.config.js` - Frontend linting rules

## API Structure

### Main Endpoints
- `POST /analyze` - Main analysis endpoint
- `POST /session/new` - Create new conversation session
- `GET /session/{id}/history` - Retrieve session history
- `GET /` - API health check and information
- `GET /docs` - FastAPI auto-generated documentation

## Key Features and Capabilities

1. **Multi-layered Analysis**: Quantitative metrics, linguistic patterns, emotion detection, AI insights
2. **Session Management**: UUID-based sessions with conversation history tracking
3. **Real-time Analysis**: Live audio recording and streaming analysis
4. **Structured Outputs**: Comprehensive JSON responses with fallback data structures
5. **Error Handling**: Graceful error handling with user-friendly messages
6. **Validation**: Pydantic models ensure data consistency

## Development Workflow

1. **Check existing code** before creating new functions
2. **Run tests early and often** to catch issues
3. **Follow existing patterns** in the codebase
4. **Document complex logic** with comments when necessary
5. **Validate with linters** before committing
6. **Test both success and failure scenarios**
7. **Maintain backward compatibility** unless explicitly changing behavior

## Common Patterns

### Backend Services
- Services are modular (e.g., `gemini_service.py`, `audio_analysis_service.py`)
- Each service has a focused responsibility
- Services use Pydantic models for input/output validation
- Error handling returns structured error responses

### Frontend Components
- Components are located in `src/components/`
- UI components from shadcn/ui are in `src/components/ui/`
- Use custom hooks for state management
- Follow responsive design patterns
- Handle loading and error states

## Notes for Code Generation

- **Search first**: Before creating new code, search for similar functionality
- **Follow conventions**: Match the style and patterns of existing code
- **Test thoroughly**: Include unit tests for new functionality
- **Document when needed**: Add comments for complex logic
- **Validate inputs**: Use Pydantic models (backend) or prop validation (frontend)
- **Handle errors**: Always include error handling for external calls
- **Use type hints**: Especially in Python backend code
- **Keep it modular**: Functions should have single, clear responsibilities

## Additional Resources

- Backend API documentation: `http://localhost:8000/docs` (when running)
- Test runner script: `tests/master_test_runner.py`
- Memory folder: Contains project notes and implementation summaries
