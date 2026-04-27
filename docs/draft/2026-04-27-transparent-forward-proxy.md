# Draft: Transparent forward proxy replaces route whitelist

**Date:** 2026-04-27

## Problem
The proxy maintained an explicit `ROUTE_MAP` whitelist of every upstream path. Each time the Copilot client introduced a new endpoint, the proxy returned 501 until the route was manually added. This amounted to reverse engineering incoming requests.

## Cause
The original design treated the proxy as a route-level gateway: only explicitly registered paths were forwarded, everything else was blocked. This is the wrong model for a pass-through proxy that should transparently relay traffic.

## Decision
Replaced the `ROUTE_MAP` whitelist and honeypot (501 catch-all) with a single transparent catch-all route that forwards all requests to `COPILOT_API_BASE_URL` by default. The `make_route_handler` factory and `ROUTE_MAP` list were removed entirely. New upstream endpoints now work automatically without proxy changes. Explicit routes can still be added later if a path needs a different upstream or custom logic.
