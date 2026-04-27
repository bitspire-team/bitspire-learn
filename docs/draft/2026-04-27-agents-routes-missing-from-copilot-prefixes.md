# Draft: Agents Routes Missing from Copilot Prefixes

**Date:** 2026-04-27

## Problem
Requests to `/agents/*` paths (e.g. `/agents/sessions`, `/agents/swe/custom-agents/...`, `/agents/swe/models`) returned 404 Not Found because they were being forwarded to the GitHub API instead of the Copilot API.

## Cause
The `COPILOT_PREFIXES` tuple in `src/api/routes/proxy.py` did not include the `/agents` prefix. The catch-all route falls through to the GitHub API base URL for any path not matching a known Copilot prefix, and `api.github.com` does not serve these agent endpoints.

## Decision
Added `"/agents"` to the `COPILOT_PREFIXES` tuple so that all `/agents/*` requests are forwarded to `api.githubcopilot.com`. This follows the existing pattern used for other Copilot-specific path prefixes.
