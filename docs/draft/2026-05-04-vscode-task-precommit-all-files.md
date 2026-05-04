# Draft: VS Code Task for Pre-commit All Files

**Date:** 2026-05-04

## Problem
Developers needed a one-click workspace task to run pre-commit against the entire repository, not only on staged files during commits.

## Cause
The existing task list did not include a command for full-repository pre-commit execution.

## Decision
Added a dedicated VS Code task in `.vscode/tasks.json` with label `Run Pre-commit (All Files)` and command `uv run pre-commit run --all-files` so repository-wide checks can be run on demand.
