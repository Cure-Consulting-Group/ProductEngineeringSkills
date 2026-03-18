---
globs: "**/*.py"
---

# Python Standards — Cure Consulting Group

When editing Python files, follow these standards:

## Code Style
- Python 3.11+ minimum — use modern syntax (match/case, type unions `X | Y`, `tomllib`)
- Type hints on all function signatures — use `from __future__ import annotations` for forward refs
- Use `dataclasses` or `pydantic.BaseModel` for data structures — no raw dicts for structured data
- Prefer `pathlib.Path` over `os.path` for file operations
- Use `asyncio` for I/O-bound operations — `async def` with `await`, not threading

## Architecture
- Follow Clean Architecture: domain (models, use cases) → data (repos, APIs) → presentation (CLI, API handlers)
- Dependencies point inward — domain has zero external imports
- Use dependency injection via constructor parameters or `inject` library
- Configuration via environment variables with `pydantic-settings` or `python-dotenv`

## Error Handling
- Custom exception hierarchy inheriting from `Exception` — never bare `except:`
- Use `raise ... from e` for exception chaining
- Validate at boundaries (API inputs, file reads, external calls) — trust internal code
- Return `None` or raise — never return error codes

## Testing
- pytest with fixtures — no unittest.TestCase
- Test file mirrors source: `src/users/service.py` → `tests/users/test_service.py`
- Fixtures in `conftest.py` — shared fixtures at package level
- Use `pytest-asyncio` for async tests
- Minimum 80% coverage on new code

## Dependencies
- Pin exact versions in `requirements.txt` or `poetry.lock`
- Group in `pyproject.toml`: `[project.dependencies]` (runtime), `[project.optional-dependencies.dev]` (dev)
- No vendored dependencies — use virtual environments
