# Proxy Service

## Overview
A transparent HTTP proxy built with FastAPI and HTTPX that forwards all traffic to `https://api.githubcopilot.com/` while capturing full request/response payloads for inspection.

## Architecture

### Forwarding (`forward_http_request`)
- Accepts all HTTP methods (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`) on any path. FastAPI does not support wildcard method routing, so they are listed explicitly.
- Rewrites the URL via string replacement: `str(request.url).replace(str(request.base_url), TARGET_BASE_URL)`. This avoids scheme-duplication bugs that occur when using `URL.replace(netloc=...)` with a target that already contains `https://`.
- Strips hop-by-hop and connection-specific headers (`host`, `connection`, `transfer-encoding`, `accept-encoding`, etc.) from both the outbound request and the upstream response.
- Passes the request body directly as `content=body`. HTTPX accepts `b""` for empty bodies, so no ternary conditional is needed.
- Catches all upstream exceptions and returns a `502 Bad Gateway` response containing the error message.

### Middleware (`logging_and_dumping_middleware`)
- Intercepts every non-health-check request before and after the route handler.
- Reads the request body, then restores it by overriding `request._receive` so the route handler can read it again. Without this, Starlette's stream is consumed and `call_next` hangs.
- Collects the response body by iterating `response.body_iterator`, then rebuilds a new `Response` to return to the client.
- Writes a single JSON file per request to `requests/`, containing `id`, `timestamp`, full request details, and full response details in one artifact.

### Payload Parsing
- **JSON**: Attempts `json.loads()` first. Falls back to the decoded UTF-8 string on failure.
- **SSE**: Detects `text/event-stream` content-type or `data: ` byte prefix. Parses individual SSE events via `sseclient-py`, extracting JSON from each `data:` line and skipping `[DONE]` terminators. Returns `{"sse_events": [...]}` on success, or the raw string on failure.

### Health and Liveness
- `/live` returns `{"status": "alive"}`.
- `/health` counts files in `requests/` and returns `{"status": "healthy", "requests_count": N}`.

## Design Principles
- The forwarding route does only forwarding. Logging and payload dumping live exclusively in middleware, keeping `forward_http_request` minimal and obviously correct.
- Readability of the forwarding path matters more than brevity. The control flow stays flat and explicit.
- Abstractions are avoided when they are larger than the code they replace.
