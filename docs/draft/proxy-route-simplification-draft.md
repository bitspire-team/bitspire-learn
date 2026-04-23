# Proxy Route Simplification Draft

## Problem
The `logging_and_dumping_middleware` in `proxy.py` was bloated with redundant target URL construction logic, verbose try/except blocks, and unnecessary logger statements just to dump request and response payloads. The forwarding handler looked verbose despite already being limited to core proxy work.

## Intention
Strip down the middleware to purely intercept the payload (request body + response body) and perform lightweight dumps to the filesystem. Identify simplifications that reduce visual noise without changing proxy behavior.

## Requirements
*   Must dump request and response to a file.
*   Must maintain the payload integrity for the downstream route handler and the return response (otherwise, Starlette routing breaks). Target forwarder must not be altered.
*   Keep request forwarding semantics unchanged.
*   Preserve header filtering and upstream error handling.
*   Avoid adding abstractions that are larger than the code they replace.

## Criticality
Overriding the `request._receive` inner function and passing a manually rebuilt `Response` are critical components of letting Starlette/FastAPI consume iterators continuously while still permitting middleware to look at the body bytes in memory. Without doing this, `call_next` fails or hangs. The route must remain obviously correct. In a proxy, readability of the forwarding path matters more than shaving off a few lines.

## Why
Cleaner, maintainable code. The route handlers (`forward_http_request`) can do the heavy lifting of proxying. The middleware now acts exclusively as an un-invasive traffic tap to `requests/` and `responses/`. The cleanest simplification here is not a larger refactor. It is to collapse a few small conditionals and helper variables while leaving the control flow flat and explicit.