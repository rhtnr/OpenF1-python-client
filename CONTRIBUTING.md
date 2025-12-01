# Contributing to OpenF1 Python Client

First off, thank you for considering contributing to the OpenF1 Python Client! 🏎️

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:

   ```bash
   git clone https://github.com/YOUR_USERNAME/openf1-python.git
   cd openf1-python
   ```

3. Add the upstream repository as a remote:

   ```bash
   git remote add upstream https://github.com/openf1-client/openf1-python.git
   ```

## Development Setup

1. Ensure you have Python 3.10 or higher installed:

   ```bash
   python --version
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode with all dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

4. Verify the installation:

   ```bash
   pytest --version
   mypy --version
   black --version
   ruff --version
   ```

## Making Changes

1. Create a new branch for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. Make your changes following the [Code Style](#code-style) guidelines

3. Add or update tests as needed

4. Run the test suite to ensure everything passes:

   ```bash
   pytest
   ```

5. Commit your changes with a clear, descriptive message:

   ```bash
   git commit -m "Add feature: description of what you added"
   # or
   git commit -m "Fix: description of what you fixed"
   ```

## Code Style

This project follows strict code style guidelines:

### Formatting

- **Black** for code formatting (line length: 88)
- **Ruff** for linting

Run formatters before committing:

```bash
black src tests
ruff check src tests --fix
```

### Type Hints

- All public functions and methods must have type hints
- Use `from __future__ import annotations` for modern annotation syntax
- Run type checking with:

  ```bash
  mypy src/openf1_client
  ```

### Docstrings

- Use Google-style docstrings
- All public classes, methods, and functions must have docstrings
- Example:

  ```python
  def get_laps(self, session_key: int, driver_number: int) -> list[Lap]:
      """
      Fetch lap data for a specific driver.

      Args:
          session_key: The session identifier.
          driver_number: The driver's car number.

      Returns:
          A list of Lap objects for the specified driver.

      Raises:
          OpenF1APIError: If the API returns an error response.
      """
  ```

### Naming Conventions

- Classes: `PascalCase`
- Functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private attributes: `_leading_underscore`

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=openf1_client --cov-report=term-missing

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::TestClientInitialization::test_default_initialization

# Run with verbose output
pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use `pytest` fixtures for setup/teardown
- Mock external HTTP calls using the `responses` library

Example test:

```python
import pytest
import responses

from openf1_client import OpenF1Client


@responses.activate
def test_fetch_drivers():
    """Test fetching driver data."""
    responses.add(
        responses.GET,
        "https://api.openf1.org/v1/drivers",
        json=[{"driver_number": 1, "full_name": "Max Verstappen"}],
        status=200,
    )

    with OpenF1Client() as client:
        drivers = client.drivers.list(session_key=9158)

    assert len(drivers) == 1
    assert drivers[0].full_name == "Max Verstappen"
```

## Submitting Changes

1. Push your branch to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a Pull Request on GitHub

3. In your PR description, include:
   - A clear description of the changes
   - The motivation for the changes
   - Any breaking changes
   - Screenshots or examples if applicable

4. Wait for review and address any feedback

### PR Checklist

Before submitting, ensure:

- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`black src tests`)
- [ ] Linting passes (`ruff check src tests`)
- [ ] Type checking passes (`mypy src/openf1_client`)
- [ ] New features have tests
- [ ] Documentation is updated if needed

## Reporting Bugs

When reporting bugs, please include:

1. **Python version**: Output of `python --version`
2. **Package version**: Output of `pip show openf1-client`
3. **Operating system**: e.g., macOS 14.0, Ubuntu 22.04, Windows 11
4. **Steps to reproduce**: Minimal code example that demonstrates the issue
5. **Expected behavior**: What you expected to happen
6. **Actual behavior**: What actually happened
7. **Error messages**: Full traceback if applicable

Use this template:

```markdown
**Environment:**
- Python: 3.12.0
- openf1-client: 1.0.0
- OS: macOS 14.0

**Steps to reproduce:**
```python
from openf1_client import OpenF1Client
# Your code here
```

**Expected behavior:**
Description of what should happen.

**Actual behavior:**
Description of what actually happened.

**Error message:**
```
Traceback (most recent call last):
  ...
```
```

## Suggesting Features

Feature suggestions are welcome! When suggesting a feature:

1. Check existing issues to avoid duplicates
2. Clearly describe the use case
3. Explain how the feature would benefit users
4. If possible, suggest an API design

---

Thank you for contributing! 🏁
