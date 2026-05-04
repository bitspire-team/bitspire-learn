from unittest.mock import patch

import pytest
from fastapi import FastAPI, Request
from src.middleware.logging import LoggingMiddleware
from starlette.responses import Response


@pytest.mark.asyncio
@pytest.mark.integration
class TestLoggingMiddleware:
    async def test_dispatch_success(self, async_session):
        """Verify middleware intercepts requests and returns the response from call_next."""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)

        async def mock_call_next(request: Request) -> Response:
            return Response(content="OK", status_code=200)

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [],
        }
        request = Request(scope=scope)

        async def mock_receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        request._receive = mock_receive

        # Use the real AsyncSessionLocal from conftest via patching to return our test session
        with patch("src.middleware.logging.AsyncSessionLocal", return_value=async_session):
            middleware = LoggingMiddleware(app)
            response = await middleware.dispatch(request, mock_call_next)

            assert response.status_code == 200
            assert b"OK" in response.body

    async def test_dispatch_does_not_crash_on_insight_failure(self, async_session):
        """Verify that the middleware does not crash the request and still returns the response."""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)

        async def mock_call_next(request: Request) -> Response:
            return Response(content="OK", status_code=200)

        scope = {
            "type": "http",
            "method": "POST",
            "path": "/test",
            "headers": [(b"content-type", b"application/json")],
        }
        request = Request(scope=scope)

        async def mock_receive():
            return {"type": "http.request", "body": b'{"invalid": json', "more_body": False}

        request._receive = mock_receive

        with patch("src.middleware.logging.AsyncSessionLocal", return_value=async_session):
            middleware = LoggingMiddleware(app)
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200
