# Testing Guide

This document provides comprehensive information about the testing infrastructure for the AI Lie Detector project.

## Table of Contents

1. [Overview](#overview)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [Test Coverage](#test-coverage)
5. [CI/CD Integration](#cicd-integration)
6. [Running Tests](#running-tests)
7. [Writing Tests](#writing-tests)

## Overview

The project uses a comprehensive testing setup with:
- **Backend**: Python pytest with coverage reporting
- **Frontend**: Vitest with React Testing Library
- **CI/CD**: GitHub Actions for automated testing
- **Coverage**: Automated coverage reporting with pytest-cov and Vitest coverage

## Backend Testing

### Test Structure

Backend tests are located in the `tests/` directory:

```
tests/
├── test_session_utils.py              # Session utility unit tests
├── test_linguistic_service_unit.py    # Linguistic service unit tests (23 tests)
├── test_manipulation_service_unit.py  # Manipulation service unit tests (14 tests)
├── test_psychological_service_unit.py # Psychological service unit tests (16 tests)
├── test_direct_patterns.py            # Linguistic pattern detection tests (7 tests)
├── test_default_structure.py          # Data structure validation tests (4 tests)
└── archived/                          # Archived test files (not run by default)
```

### Test Categories

Tests are marked with pytest markers:
- `@pytest.mark.unit` - Fast unit tests with no external dependencies (default)
- `@pytest.mark.integration` - Integration tests requiring server/resources
- `@pytest.mark.slow` - Slow-running tests

### Running Backend Tests

```bash
# Run all unit tests (default)
pytest

# Run specific test file
pytest tests/test_linguistic_service_unit.py

# Run with coverage
pytest --cov=backend --cov-report=term-missing

# Run integration tests
pytest -m integration

# Run all tests including integration and slow tests
pytest -m ""
```

### Backend Test Configuration

Configuration is in `pytest.ini`:
- Test discovery in `tests/` directory
- Excludes `archived/`, `generated_files/`, `test_extras/`
- Coverage enabled by default with HTML and XML reports
- Logs enabled at INFO level

Coverage configuration is in `.coveragerc`:
- Measures coverage for `backend/` directory
- Excludes test files, archived files, and some entry points
- Generates HTML report in `htmlcov/`
- Generates XML report for CI/CD

## Frontend Testing

### Test Structure

Frontend tests are co-located with components:

```
frontend/
├── src/
│   ├── components/
│   │   └── ui/
│   │       ├── badge.jsx
│   │       └── badge.test.jsx        # Badge component tests (8 tests)
│   └── test/
│       └── setup.js                  # Test setup and configuration
└── vitest.config.js                  # Vitest configuration
```

### Running Frontend Tests

```bash
cd frontend

# Run tests in watch mode
npm test

# Run tests once
npm test -- --run

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### Frontend Test Configuration

Configuration is in `vitest.config.js`:
- Uses jsdom environment for React component testing
- Includes React Testing Library setup
- Coverage reporting with v8 provider
- Generates text, JSON, and HTML coverage reports

## Test Coverage

### Current Coverage

Backend coverage (as of last run):
- **Overall**: 24.73%
- **Linguistic Service**: 69.94%
- **Models**: 100%
- **Other Services**: 7-30%

### Viewing Coverage Reports

**Backend:**
```bash
# Generate and view HTML report
pytest --cov=backend --cov-report=html
# Open htmlcov/index.html in browser
```

**Frontend:**
```bash
cd frontend
npm run test:coverage
# Open coverage/index.html in browser
```

### Coverage Goals

- Unit tests should achieve >80% coverage
- Critical services should achieve >90% coverage
- Integration tests supplement unit test coverage

## CI/CD Integration

### GitHub Actions Workflow

The `.github/workflows/tests.yml` file defines automated testing:

**Backend Tests Job:**
- Runs on Python 3.12
- Installs dependencies: pytest, pytest-cov, pydantic, httpx, fastapi, etc.
- Runs all unit tests with coverage
- Uploads coverage to Codecov

**Frontend Tests Job:**
- Runs on Node.js 20
- Installs dependencies with npm ci
- Runs tests with coverage
- Uploads coverage to Codecov

### Triggering CI/CD

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

## Running Tests

### Local Development

**Quick Test Run:**
```bash
# Backend unit tests only (fast)
pytest

# Frontend tests
cd frontend && npm test -- --run
```

**Full Test Suite:**
```bash
# Run all backend tests with coverage
pytest -m "" --cov=backend

# Run all frontend tests with coverage
cd frontend && npm run test:coverage
```

### Before Committing

```bash
# Run backend tests
pytest tests/test_session_utils.py tests/test_linguistic_service_unit.py tests/test_manipulation_service_unit.py tests/test_psychological_service_unit.py -v

# Run frontend tests
cd frontend && npm test -- --run
```

## Writing Tests

### Backend Unit Tests

**Example Structure:**
```python
import pytest
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.your_service import your_function


@pytest.mark.unit
def test_your_function():
    """Test description."""
    result = your_function("input")
    
    assert result is not None
    assert isinstance(result, dict)
    assert "expected_key" in result
```

**Best Practices:**
- Mark with `@pytest.mark.unit` for fast tests
- Use descriptive test names starting with `test_`
- Test edge cases (empty input, None, special characters)
- Test both success and failure scenarios
- Keep tests independent and isolated

### Frontend Component Tests

**Example Structure:**
```javascript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { YourComponent } from './YourComponent'

describe('YourComponent', () => {
  it('renders correctly', () => {
    render(<YourComponent />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })

  it('handles user interaction', () => {
    render(<YourComponent />)
    // Add interaction tests
  })
})
```

**Best Practices:**
- Group related tests in `describe` blocks
- Use descriptive test names
- Test component rendering
- Test user interactions
- Test props and state changes
- Keep tests focused and simple

## Test Organization

### Archived Tests

Old or superseded tests are in `tests/archived/`:
- These tests are excluded from normal test runs
- Kept for reference and historical purposes
- 32 archived test files moved from root tests/ directory

### Test Extras

Test assets and generated files in `tests/test_extras/`:
- Audio samples (.wav, .mp3)
- Video files
- Generated JSON responses
- HTML artifacts

## Troubleshooting

### Common Issues

**Missing Dependencies:**
```bash
# Backend
pip install pytest pytest-cov pydantic httpx fastapi google-genai python-dotenv

# Frontend
cd frontend && npm install
```

**Import Errors:**
```python
# Add this to test files
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
```

**Coverage Not Working:**
```bash
# Ensure pytest-cov is installed
pip install pytest-cov

# Check .coveragerc configuration
# Check pytest.ini has --cov options
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

## Contributing

When adding new features:
1. Write unit tests first (TDD approach recommended)
2. Ensure tests pass locally before committing
3. Maintain or improve code coverage
4. Update this guide if adding new test patterns
