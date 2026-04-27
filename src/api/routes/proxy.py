import logging

import httpx
from fastapi import APIRouter, Request, Response

from src.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

RESTRICTED_HEADERS = {
    "connection",
    "content-length",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "accept-encoding",
    "host",
}

upstream_client = httpx.AsyncClient(timeout=30.0, http2=True)

PROXY_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]

COPILOT_PREFIXES = (
    "/_ping",
    "/v1/",
    "/chat/",
    "/responses",
    "/models",
    "/agents",
)


async def forward_request(request: Request, upstream_base_url: str) -> Response:
    target_url = str(request.url).replace(str(request.base_url), upstream_base_url)

    outbound_headers = {
        k: v for k, v in request.headers.items() if k.lower() not in RESTRICTED_HEADERS
    }

    body = await request.body()

    try:
        logger.info("Forwarding the request to %s.", target_url)
        upstream_response = await upstream_client.request(
            method=request.method,
            url=target_url,
            headers=outbound_headers,
            content=body,
        )
        logger.info("Completed forwarding the request to %s.", target_url)
    except Exception as e:
        # Return 502 so the client knows the upstream failed, not the proxy itself.
        logger.exception("Failed to forward request to %s.", target_url)
        return Response(status_code=502, content=f"Proxy error: {e}")

    response_headers = {
        k: v
        for k, v in upstream_response.headers.items()
        if k.lower() not in RESTRICTED_HEADERS
    }
    return Response(
        status_code=upstream_response.status_code,
        content=upstream_response.content,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )


@router.api_route("/{path:path}", methods=PROXY_METHODS)
async def catch_all(path: str, request: Request) -> Response:
    if request.url.path.startswith(COPILOT_PREFIXES):
        logger.info(
            "Forwarding %s request for %s to the Copilot API.",
            request.method,
            request.url.path,
        )
        return await forward_request(request, settings.COPILOT_API_BASE_URL)

    logger.info(
        "Forwarding %s request for %s to the GitHub API.",
        request.method,
        request.url.path,
    )
    return await forward_request(request, settings.GITHUB_API_BASE_URL)
