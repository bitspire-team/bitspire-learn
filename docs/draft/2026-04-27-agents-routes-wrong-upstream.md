# Draft: Agent routes pointed to wrong upstream

**Date:** 2026-04-27

## Problem
All `/agents/*` proxy routes returned HTTP 404 because they were forwarded to the wrong upstream API.

## Cause
The `ROUTE_MAP` in `src/api/routes/proxy.py` mapped all five `/agents/*` prefixes to `GITHUB_API_BASE_URL` (`https://api.github.com/`). These are Copilot-specific agent endpoints that live on `https://api.githubcopilot.com/`, not on the GitHub REST API.

## Decision
Changed all `/agents/*` entries in `ROUTE_MAP` from `settings.GITHUB_API_BASE_URL` to `settings.COPILOT_API_BASE_URL`. The affected routes are `/agents/swe/custom-agents/...`, `/agents/swe/v1/jobs/...`, `/agents/swe/models`, `/agents/sessions`, and `/agents`.
