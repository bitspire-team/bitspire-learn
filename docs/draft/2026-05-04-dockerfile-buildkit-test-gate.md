# Draft: Dockerfile BuildKit Test Gate

**Date:** 2026-05-04

## Problem
The tests in the Dockerfile `test` stage were completely skipped by BuildKit during a standard `docker build`, meaning no test gate was actually being enforced for Dokploy. Additionally, missing files in `.dockerignore` caused tests/migrations to fail if they *were* run.

## Cause
- BuildKit skips stages that are not depended upon by the final target stage (`production`).
- The `.dockerignore` explicitly excluded `tests/`, `alembic/`, `alembic.ini`.
- `pydantic_settings` raised a missing `DATABASE_URL` issue when importing the `conftest.py` missing environment variables in the Docker build.

## Decision
- Added a `base` stage to deduplicate `uv` installation code.
- Added `RUN python -m pytest tests/ -v && touch /tests-passed` in the `test` stage to run tests and create a marker file.
- Added `COPY --from=test /tests-passed /tests-passed` to the `production` stage to force BuildKit to depend on the `test` stage.
- Updated `.dockerignore` to explicitly include `!tests/*`, `!alembic/*`, and `!alembic.ini`.
- Added a dummy `ENV DATABASE_URL="sqlite+aiosqlite:///:memory:"` for the `test` stage so settings initialization parses successfully without relying on an external `.env` file during image build.