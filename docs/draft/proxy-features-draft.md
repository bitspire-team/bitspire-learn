# Proxy Service Features Draft

## Problem
The project requires visibility into the requests and responses exchanged with the GitHub Copilot API (`api.githubcopilot.com`) to monitor, analyze, and document the payload structure, without breaking the normal flow of the client application.

## Intention
To document the current capabilities and feature set of the `proxy.py` service so that future development and architectural decisions can build upon this baseline. 

## Requirements
*   **Protocol Support:** Must accept all HTTP methods (GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD) on any path.
*   **Traffic Forwarding:** Must seamlessly forward requests to the target `https://api.githubcopilot.com`, including query parameters.
*   **Header Filtering:** Must strip restrictive hop-by-hop and connection-specific headers (e.g., `host`, `connection`, `transfer-encoding`, `accept-encoding`) to prevent upstream rejection or parsing errors.
*   **Payload Capture:** Must parse and save the JSON request and response bodies (or fallback to strings) into `requests/` and `responses/` folders with unique UUIDs and timestamps.
*   **Robust Logging:** Must use Python's `logging` module to output natural English statements to both the console and timestamped files in `logs/` without using shorthands or bracketed prefixes.
*   **Resilience:** Must gracefully shut down the asynchronous connection pool (`httpx.AsyncClient`) and handle upstream communication errors by returning `502 Bad Gateway` while properly recording the fault.

## Criticality
The most critical part of this service is the accurate, non-destructive forwarding of traffic while capturing the exact payloads. Stripping the correct headers (like `host` and `transfer-encoding`) is crucial to ensure the target API does not block or misinterpret the proxied request.

## Why
This approach was chosen because a transparent HTTP proxy using FastAPI and HTTPX allows for highly concurrent request handling, easy manipulation of headers, and seamless asynchronous file I/O for logging. It provides a reliable interception layer that satisfies both the need for deep payload inspection and the requirement to maintain Copilot's functional integrity.

## Evolution of Decisions
*   **Method Support:** Initially questioned if we could just use a wildcard for HTTP methods (e.g., `*`) to simplify the code. However, it was decided to explicitly define `["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]` because FastAPI and Starlette do not support wildcard routing for methods. If omitted, the default is `GET` only. Explicitly defining them ensures proper all-request forwarding.
*   **Decoupling Logic:** The `forward_http_request` function was becoming too bloated with non-routing concerns like logging and file-writing. Initially, a custom `HookManager` was introduced. However, this was replaced with a native FastAPI `@app.middleware("http")` function to intercept requests before and after the route handler. Now, `forward_http_request` is pure, only knowing about forwarding the traffic, and the middleware handles the logging, tracking, and dumping.
*   **Payload Parsing:** Initially tried aggressively extracting individual JSON objects out of standard Server-Sent Event (SSE) and JSON Lines (JSONL) blobs. Decided to revert back to basic `json.loads(decoded)` parsing for simplicity. The code falls back to returning the decoded UTF-8 string on failure. We've left a structured codebase note acknowledging that this fallback causes streaming response payloads (like Copilot chat completion) to log as unformatted raw strings rather than nested objects.
*   **Route Simplification:** The active forwarding route is already close to minimal. The preferred simplification is to keep the route focused on URL construction, header filtering, body forwarding, and error handling, while avoiding extra intermediate variables or duplicated response-mapping code. Small simplifications such as building the target URL in one expression and passing the request body directly are acceptable when they do not hide the proxy behavior.