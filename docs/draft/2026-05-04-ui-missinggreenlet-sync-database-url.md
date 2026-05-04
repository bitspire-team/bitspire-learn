# Draft: Fix MissingGreenlet in Copilot UI Database Access

**Date:** 2026-05-04

## Problem
The `Run UI` task failed with `sqlalchemy.exc.MissingGreenlet` when the Streamlit dashboard tried to query the database.

## Cause
The UI creates a synchronous SQLAlchemy engine and executes pandas SQL reads, but `DATABASE_URL` could be configured with an async driver URL like `postgresql+asyncpg://` or `sqlite+aiosqlite://`, which requires async greenlet context.

## Decision
Added a `SYNC_DATABASE_URL` setting in `services/copilot-ui/src/core/config.py` that maps async URLs to sync drivers (`postgresql+psycopg2://` and `sqlite://`) and updated `services/copilot-ui/src/ui.py` to build the engine from `settings.SYNC_DATABASE_URL` so Streamlit database reads always use a sync-compatible driver.