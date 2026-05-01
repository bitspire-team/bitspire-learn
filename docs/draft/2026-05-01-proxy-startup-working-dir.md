# Proxy Startup Working Directory

**Date:** 2026-05-01
**Topic:** proxy-startup-working-dir

## Problem
The `Run Proxy` task in `.vscode/tasks.json` was failing with `ModuleNotFoundError: No module named 'src.core.db'` because it was being run with a `cwd` of `services/copilot-proxy/src` while the import paths in the application code expect `services/copilot-proxy` to be the working directory (i.e. they use `from src....`).

## Cause
The VS Code task `cwd` property was set to `${workspaceFolder}/services/copilot-proxy/src` instead of `${workspaceFolder}/services/copilot-proxy`.

## Decision/Action Taken
Updated `.vscode/tasks.json` to change the `cwd` for the `Run Proxy` task to `${workspaceFolder}/services/copilot-proxy` and the command to `uv run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload`. This aligns the execution context with the expected import paths.