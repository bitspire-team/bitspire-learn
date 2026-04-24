import pytest
from unittest.mock import AsyncMock, patch
from fastapi import Request, Response
import httpx

from src.proxy import forward_http_request

SCOPE_BASE = {"type": "http", "server": ("localhost", 8080)}


class TestForwardHttpRequest:
    @pytest.mark.asyncio
    @patch("src.proxy.upstream_client.request", new_callable=AsyncMock)
    async def test_forwarding_get_requests(self, mock_upstream):
        request = Request(
            scope={
                **SCOPE_BASE,
                "method": "GET",
                "path": "/api/models",
                "headers": [
                    (b"accept", b"application/json"),
                    (b"host", b"localhost:8080"),
                ],
            },
            receive=AsyncMock(return_value={"type": "http.request", "body": b""}),
        )
        mock_upstream.return_value = httpx.Response(
            200,
            content=b'{"data": []}',
            headers={"content-type": "application/json", "x-custom": "value"},
        )

        response = await forward_http_request("/api/models", request)

        mock_upstream.assert_called_once_with(
            method="GET",
            url="https://api.githubcopilot.com/api/models",
            headers={"accept": "application/json"},
            content=b"",
        )
        assert response.status_code == 200
        assert response.body == b'{"data": []}'
        assert response.media_type == "application/json"

    @pytest.mark.asyncio
    @patch("src.proxy.upstream_client.request", new_callable=AsyncMock)
    async def test_forwarding_post_requests_with_payload(self, mock_upstream):
        payload = b'{"prompt": "hello world"}'
        request = Request(
            scope={
                **SCOPE_BASE,
                "method": "POST",
                "path": "/v1/completions",
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"host", b"localhost:8080"),
                ],
            },
            receive=AsyncMock(return_value={"type": "http.request", "body": payload}),
        )
        mock_upstream.return_value = httpx.Response(
            201,
            content=b'{"id": "cmpl-123"}',
            headers={"content-type": "application/json"},
        )

        response = await forward_http_request("/v1/completions", request)

        mock_upstream.assert_called_once_with(
            method="POST",
            url="https://api.githubcopilot.com/v1/completions",
            headers={"content-type": "application/json"},
            content=payload,
        )
        assert response.status_code == 201
        assert response.body == b'{"id": "cmpl-123"}'

    @pytest.mark.asyncio
    @patch("src.proxy.upstream_client.request", new_callable=AsyncMock)
    async def test_forwarding_post_requests_with_streaming_response(
        self, mock_upstream
    ):
        payload = b'{"stream": true}'
        request = Request(
            scope={
                **SCOPE_BASE,
                "method": "POST",
                "path": "/v1/chat/completions",
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"host", b"localhost:8080"),
                ],
            },
            receive=AsyncMock(return_value={"type": "http.request", "body": payload}),
        )
        sse_body = (
            b'data: {"choices": [{"delta": {"content": "A"}}]}\n\ndata: [DONE]\n\n'
        )
        mock_upstream.return_value = httpx.Response(
            200, content=sse_body, headers={"content-type": "text/event-stream"}
        )

        response = await forward_http_request("/v1/chat/completions", request)

        mock_upstream.assert_called_once_with(
            method="POST",
            url="https://api.githubcopilot.com/v1/chat/completions",
            headers={"content-type": "application/json"},
            content=payload,
        )
        assert response.status_code == 200
        assert response.body == sse_body
        assert response.media_type == "text/event-stream"

    @pytest.mark.asyncio
    @patch("src.proxy.upstream_client.request", new_callable=AsyncMock)
    async def test_exception_handling(self, mock_upstream):
        request = Request(
            scope={
                **SCOPE_BASE,
                "method": "GET",
                "path": "/api/fail",
                "headers": [(b"host", b"localhost:8080")],
            },
            receive=AsyncMock(return_value={"type": "http.request", "body": b""}),
        )
        mock_upstream.side_effect = Exception("Connection Refused")

        response = await forward_http_request("/api/fail", request)

        assert response.status_code == 502
        assert response.body == b"Proxy error: Connection Refused"
