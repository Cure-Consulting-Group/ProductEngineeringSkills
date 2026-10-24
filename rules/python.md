---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
---

# Python Standards — Cure Consulting Group

When editing Python files, follow these standards:

## Code Style
- Python 3.12+ floor; new projects target the newest release their dependencies support (3.14 or 3.15). 3.10 is end-of-life
- Modern syntax: `match`, `X | Y` unions, `type` aliases, `tomllib`
- Type hints on every function signature; `pyright` or `mypy` (strict on new code) in CI
- `ruff check` and `ruff format` — replaces black, isort and flake8
- `dataclasses` or `pydantic.BaseModel` for structured data — no raw dicts
- `pathlib.Path` over `os.path`
- `asyncio` for I/O-bound work — `async def` with `await`, not threading

## Architecture
- Clean Architecture: domain (models, use cases) → data (repos, APIs) → presentation (CLI, API handlers)
- Dependencies point inward — the domain has zero external imports
- Dependency injection via constructor parameters
- Configuration from environment variables via `pydantic-settings`

## Error Handling
- Custom exception hierarchy inheriting from `Exception` — never bare `except:`
- `raise ... from e` for exception chaining
- Validate at boundaries (API inputs, file reads, external calls) — trust internal code
- Return `None` or raise — never return error codes

## Testing
- pytest with fixtures — no `unittest.TestCase` in new code
- Test file mirrors source: `src/users/service.py` → `tests/users/test_service.py`
- Shared fixtures in `conftest.py`; `pytest-asyncio` for async tests
- 80% diff coverage on new code (gate defined by `testing-strategy`)

## Dependencies (uv)
- `uv` manages the interpreter, venv and lockfile: `uv add`, `uv add --dev`, `uv run`; commit `uv.lock`; CI runs `uv sync --locked`
- Runtime deps in `[project.dependencies]`; dev tooling in `[dependency-groups]` (PEP 735) — not `[project.optional-dependencies]` (user-facing extras only) or legacy `tool.uv.dev-dependencies`
- No vendored dependencies, no global `pip install`

Verified 2026-10-24: 3.15 released 2026-10-09, 3.10 EOL 2026-10 (python.org/downloads); `[dependency-groups]` per docs.astral.sh/uv/concepts/projects/dependencies.
