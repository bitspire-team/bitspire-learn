# Draft Note: Parsing Complex Payloads

## Problem
Currently, the `parse_body` function in `proxy.py` relies entirely on a single `json.loads()` pass. While this works well for standard API payloads, it completely fails to decode Server-Sent Events (SSE) and JSON Lines (JSONL), which are heavily used by the Copilot API for streaming completions. When it fails, it dumps the entire stream as an escaped, unreadable string. Additionally, capturing proxy traffic resulted in fragmented, difficult-to-trace logs because requests and responses were split across separate directories (`requests/` and `responses/`), and exceptions generated during the forwarded request were absent from the JSON tracking payload.

## Intention
To upgrade the `parse_body` function to intelligently detect and parse JSONL and SSE streams so that the log files remain perfectly structured and human-readable. Combine the request and response objects into a single cohesive `.json` dump file containing the complete lifecycle of one specific HTTP request.

## Requirements
*   Still parse standard JSON if present.
*   If standard JSON fails, split the string by newlines and try to iteratively parse them.
*   For SSE lines, recognize and strip the `data: ` prefix before parsing.
*   Handle special SSE terminators like `data: [DONE]`.
*   Provide a single JSON schema detailing `"id"`, `"timestamp"`, `"request"` details, `"response"` details, and an optional `"error"` flag to handle failures efficiently. Create a single combined dump when the proxy loop naturally finishes or triggers an overarching error. Update directory artifacts (i.e. `payloads/` instead of `requests/` and `responses/`).

## Criticality
We removed the redundant `try...except...finally` block from the core forwarder `call_next(request)` logic because the underlying `forward_http_request` function gracefully catches exceptions and constructs native 502 responses anyway. Since the forwarder encodes proxy errors into the target `Response` body, we just parse that as a standard `response` object.

## Why
Using a robust parser that can handle multiple lines of sequential JSON or SSE blocks prevents data loss and maintains high-quality logs without interfering with the upstream transit. Developers examining API traces or proxy payloads will have a far easier time reviewing one single JSON artifact, especially to see if an `error` state is tightly coupled to the incoming request payload structure.