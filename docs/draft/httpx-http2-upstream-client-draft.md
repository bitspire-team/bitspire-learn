# HTTPX HTTP/2 for Upstream Client

## Problem
The proxy uses `httpx.AsyncClient` with default settings (HTTP/1.1 only) to forward requests to the GitHub Copilot API. We evaluated whether a different HTTP client library or protocol upgrade would improve performance.

## Intention
Determine the best HTTP client library for a FastAPI-based reverse proxy and whether enabling HTTP/2 on the upstream client is worthwhile.

## Requirements
- Must support async natively (to avoid blocking the FastAPI event loop).
- Must integrate cleanly with FastAPI's async request lifecycle.
- Backward compatibility: must not break if the upstream server only supports HTTP/1.1.
- Minimal additional dependencies.

## Decision
- **httpx remains the best choice** for async HTTP in FastAPI. It is built by the same team (Encode), has native async support, streaming, and HTTP/2 capability. Alternatives like `aiohttp` (older, more verbose) and `requests`/`urllib3` (sync-only, would block the event loop) are inferior for this use case.
- **HTTP/2 should be enabled** on the upstream client (`http2=True`) for the following reasons:
  - **Multiplexing**: Multiple concurrent requests share a single TCP connection without head-of-line blocking.
  - **Header compression** (HPACK): Reduces overhead on repeated requests with similar auth/API headers.
  - **Lower latency**: Fewer round trips for connection setup during request bursts.
- The GitHub Copilot API supports HTTP/2, so the benefits are real and immediate.

## Criticality
- HTTP/2 negotiation is automatic via ALPN during TLS. If the server doesn't support it, httpx falls back to HTTP/1.1 transparently — there is zero backward compatibility risk.
- This setting only affects the **outbound** connection (proxy → GitHub API). The inbound side (clients → proxy via uvicorn) is completely unaffected.
- The only additional dependency is the `h2` Python package.

## Why
httpx is the de facto standard pairing with FastAPI. Enabling HTTP/2 is a low-risk, high-reward change: it improves throughput for concurrent proxy requests with automatic fallback and requires only one extra dependency.

## Evolution
1. Started by evaluating alternative HTTP client libraries (aiohttp, requests, urllib3) — concluded httpx is the correct choice.
2. Identified HTTP/2 as the meaningful upgrade opportunity on the existing client.
3. Confirmed HTTP/2 defaults to off (`http2=False`) and must be explicitly enabled.
4. Verified backward compatibility is not a concern due to automatic ALPN negotiation and transparent fallback.
