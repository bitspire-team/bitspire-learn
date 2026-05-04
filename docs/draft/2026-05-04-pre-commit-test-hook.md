# Pre-commit Test Hook

## Problem
Without CI/CD, bad code can be committed and pushed to Dokploy, causing failed builds or runtime errors in production. The Dockerfile test gate catches failures at build time, but that's slow feedback (minutes per build).

## Decision
Add pre-commit hooks using the [pre-commit framework](https://pre-commit.com/) for fast local feedback at commit time.

## Rationale
- **pre-commit framework** over raw git hooks: version-controlled config (`.pre-commit-config.yaml`), portable across developers, declarative, isolated virtualenvs
- **Complements Dockerfile test gate**: pre-commit catches issues before commit, Dockerfile catches issues before deploy — two layers of defense
- **Fast feedback**: tests run in seconds locally vs minutes in Docker build

## Configuration
- File: `.pre-commit-config.yaml` at workspace root
- Hooks:
  1. `pytest-proxy` — runs full test suite in `services/copilot-proxy/` on every commit
  2. `ruff-check` — lint check on staged Python files only (fast, focused)
  3. `ruff-format` — auto-format staged Python files
- Language: `system` (leverages existing uv environment)
- Activation: `pre-commit install` (one-time setup)

## What's Critical
- Pre-commit runs on `git commit`, blocking the commit if tests fail
- Tests run from `services/copilot-proxy/` directory (where `tests/` lives)
- `pass_filenames: false` for pytest — we want full test suite, not just changed files
- Ruff runs on staged files only — fast and focused on what's changing

## Dependencies Added
- `ruff>=0.9.0` — linter + formatter (already configured in root `pyproject.toml`)
- `pre-commit>=4.0.0` — hook framework itself

## Setup
```bash
uv sync                          # install pre-commit + ruff
pre-commit install               # install git hook script
pre-commit run --all-files       # optional: run against all files once
```

## Lessons
- Pre-commit hooks are a force multiplier for quality when there's no CI
- Running full test suite on commit (not just changed files) ensures regressions are caught early
- Combining test + lint + format in one hook gives comprehensive quality gate
