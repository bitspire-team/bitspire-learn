# Draft: Register pytest marks to eliminate warnings

**Date:** 2026-05-04

## Problem
Running pytest produced 4 `PytestUnknownMarkWarning` warnings about unknown `pytest.mark.integration`, cluttering test output and potentially masking future issues.

## Cause
`@pytest.mark.integration` was used on test functions but never registered in pytest configuration. pytest 9.x warns about unregistered marks by default.

## Decision
Registered the `integration` mark under `[tool.pytest.ini_options]` in `services/copilot-proxy/pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "integration: marks tests as integration tests",
]
```

This is the standard pytest pattern — all custom marks should be declared upfront so pytest can validate usage and generate proper help output via `pytest --markers`.
