# Contributing

Thanks for your interest in contributing!

## Development Setup

1. Fork and clone the repository.
2. Create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt -r requirements-test.txt
   ```

4. Install pre-commit hooks:

   ```powershell
   pre-commit install
   ```

## Running Tests

```powershell
python -m pytest -q
```

## Code Style

- **Formatter/linter:** [ruff](https://docs.astral.sh/ruff/) (line length 100)
- **Type hints:** All functions must have type annotations (enforced by `mypy`)
- **Imports:** Sorted by `ruff isort` rules

Run linting locally:

```powershell
ruff check .
mypy api/
```

## Pull Requests

1. Create a feature branch from `main`.
2. Make your changes with clear commit messages.
3. Ensure all tests pass and linting is clean.
4. Open a PR with a description of the change and its motivation.

## Reporting Bugs

Open an issue with:
- A minimal reproduction
- Expected vs actual behavior
- Your OS and Python version
