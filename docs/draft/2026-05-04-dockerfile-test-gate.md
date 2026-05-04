# Dockerfile Test Gate — Multi-Stage Build

## Problem
Dokploy self-hosts the proxy service with no CI pipeline. Bad code can reach production if tests are not enforced at build time.

## Decision
Use a multi-stage Dockerfile where the first stage runs all pytest tests. If any test fails, the Docker build fails and Dokploy never receives the image.

## Implementation
- **Stage 1 (`test`)**: Installs runtime + `[test]` dependencies, copies `src/` and `tests/`, runs `pytest tests/ -v`.
- **Stage 2 (`production`)**: Clean image with only runtime dependencies and `src/`. No test artifacts in the final image.

## Why This Approach
- No CI server needed — the build itself is the gate.
- Tests run in the same environment (same Python version, same dependency resolver) that production uses.
- Final image stays lean — tests are not included in the production layer.
- Dokploy just runs `docker build` as usual; failure = no deploy.

## Key Considerations
- All tests must be environment-agnostic (use in-memory SQLite, mocks, etc.). The `conftest.py` already uses `sqlite+aiosqlite:///:memory:` which is correct.
- Tests marked `@pytest.mark.integration` still run — there's no separate "unit only" gate. If integration tests need a real DB, they should be skipped in the Docker build via `-m "not integration"` or by mocking the DB layer.
- Future: If tests grow slow, consider caching pip/uv layers or splitting unit vs integration stages.
