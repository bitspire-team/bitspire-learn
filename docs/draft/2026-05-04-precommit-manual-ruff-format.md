# Draft: Manual Ruff Formatter Hook

**Date:** 2026-05-04

## Problem
The project needed Ruff formatting available in pre-commit without running automatically on every commit.

## Cause
Only automatic hooks were configured, so formatting could not be triggered through pre-commit as an explicit on-demand action.

## Decision
Added a local pre-commit hook `ruff-format` with `entry: uv run ruff format --force-exclude` and `stages: [manual]` so formatting runs only when explicitly requested.
