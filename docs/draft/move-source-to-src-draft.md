# Draft: Move Python Source Files to src/ Directory

## Problem
Python source files (`proxy.py`, `ui.py`) were located at the project root, mixing application code with configuration and metadata files.

## Intention
Organize the project by moving application Python files into a `src/` package directory, following standard Python project layout conventions.

## Requirements
- All Python source files must reside under `src/`.
- `src/` must be a proper Python package (with `__init__.py`).
- All references must be updated: test imports, `@patch` targets, `pyproject.toml`, Dockerfile, and VS Code tasks.
- Tests must continue to pass after the move.

## Criticality
The most critical part is ensuring all import paths and patch targets in tests are updated from `proxy.*` to `src.proxy.*`. Missing even one patch target silently breaks test mocking.

## Why
Standard Python project layout separates source code from project metadata, tests, and configuration. This makes the project easier to navigate, package, and maintain.

## Changes Made
- Created `src/` directory with `__init__.py`.
- Moved `proxy.py` → `src/proxy.py`, `ui.py` → `src/ui.py`.
- Updated `pyproject.toml`: changed `py-modules = ["proxy", "ui"]` to `packages = ["src"]`.
- Updated `Dockerfile`: `CMD ["python", "src/proxy.py"]`.
- Updated `.vscode/tasks.json`: Run Proxy and Run UI commands now reference `src/proxy.py` and `src/ui.py`.
- Updated `tests/test_proxy.py`: import changed to `from src.proxy import ...`, all `@patch("proxy.` → `@patch("src.proxy.`.
