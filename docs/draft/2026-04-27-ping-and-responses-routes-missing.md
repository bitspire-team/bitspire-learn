# Draft: Missing /_ping and /responses routes

**Date:** 2026-04-27

## Problem
Copilot client requests to `/_ping` and `/responses` were returning 501 "No routing is configured for this path" because the proxy had no routes defined for these endpoints.

## Cause
The proxy's `ROUTE_MAP` did not include entries for `/_ping` (a health-check ping used by the Copilot client) or `/responses` (the newer OpenAI Responses API endpoint). Both are legitimate upstream paths that the Copilot extension calls.

## Decision
Added `/_ping` and `/responses` to the `ROUTE_MAP` in `src/api/routes/proxy.py`, both forwarding to `COPILOT_API_BASE_URL`. After restart, `/_ping` returns 200 and `/responses` returns 400 (expected for an empty GET — the upstream accepts the route). The `/v1/engines/gpt-41-copilot/completions` route was already configured but returns 404 from upstream, which is an upstream issue, not a proxy routing problem.
