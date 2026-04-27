# Draft: All Proxy Responses Are Plain Response

**Date:** 2026-04-27

## Problem
Response logging had two code paths: one for `body_iterator` (StreamingResponse) and one for `.body` (plain Response), adding complexity that may not be needed.

## Cause
The code was written defensively to handle both response types, but `forward_request()` always returns a plain `Response(content=...)` because httpx reads the full upstream body before returning.

## Decision
Keep both paths in `read_response_body()` as a safety net, but the streaming path is currently dead code. If the proxy ever switches to true streaming (e.g. `StreamingResponse` with httpx `stream()`), the body_iterator path will activate. The plain `.body` path handles all current traffic.
