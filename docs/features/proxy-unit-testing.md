# Proxy Unit Testing

## Overview
Unit tests for the `forward_http_request` function in `tests/test_proxy.py`, covering the four core forwarding scenarios. Tests run without network access or authentication tokens.

## Test Cases

| Test | Verifies |
|------|----------|
| `test_forwarding_get_requests` | URL rewriting, header filtering, status/body/media-type mapping |
| `test_forwarding_post_requests_with_payload` | Body bytes forwarded untouched to upstream |
| `test_forwarding_post_requests_with_streaming_response` | SSE content-type and raw bytes pass through correctly |
| `test_exception_handling` | Upstream failures produce 502 with error message |

## Conventions
- Class-based: `TestForwardHttpRequest` mirrors the function under test.
- File placement: `tests/test_proxy.py` mirrors `proxy.py`.
- Dependencies: `pytest` and `pytest-asyncio` in `[project.optional-dependencies] test`, installed via `pip install -e .[test]`.

## Mocking Strategy
- **Real `fastapi.Request`**: Constructed from an inline ASGI scope dict and an `AsyncMock` receive callable. `Request` is stateless (just wraps a dict), so no side effects. A `SCOPE_BASE` constant holds the two keys that never change (`type`, `server`).
- **Real `httpx.Response`**: Used instead of `MagicMock` for upstream responses. Equally stateless, removes a layer of faking.
- **Patched `upstream_client.request`**: The only mock — this is the sole component that makes real network calls.

## Key Decisions
- **Real objects over mocks when safe.** `Request` and `httpx.Response` carry no side effects, so real instances test actual data flow rather than assumptions about mock attributes. `MagicMock(spec=Request)` was abandoned because it broke on `request.url.path` (plain strings lack `.path`).
- **No helper functions.** The ASGI scope dict is small (5 keys) and self-explanatory. Inline construction keeps each test self-contained. An intermediate `build_test_request()` helper was removed for this reason.
- **Mock only what has side effects.** `upstream_client.request` is patched; everything else is real.
