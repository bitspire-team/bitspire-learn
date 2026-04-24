import json
import logging
import os
import uuid
import io
import sseclient
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import Response

os.makedirs("logs", exist_ok=True)
os.makedirs("requests", exist_ok=True)

log_file_path = os.path.join(
    "logs", f"proxy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file_path, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

TARGET_BASE_URL = "https://api.githubcopilot.com/"
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8080

RESTRICTED_HEADERS = {
    "connection",
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await upstream_client.aclose()
    logger.info("The proxy server is shutting down gracefully.")


app = FastAPI(lifespan=lifespan)


def parse_as_json(body_bytes: bytes) -> Any:
    logger.info("Starting to parse the payload as JSON.")
    if not body_bytes:
        return None
    decoded = body_bytes.decode("utf-8", errors="replace")
    try:
        return json.loads(decoded)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse the payload as JSON: {e}")
        return decoded


def parse_as_sse(body_bytes: bytes) -> Any:
    logger.info("Starting to parse the payload as Server-Sent Events.")
    if not body_bytes:
        return None
    decoded = body_bytes.decode("utf-8", errors="replace")
    try:
        stream = io.BytesIO(body_bytes)
        client = sseclient.SSEClient(stream)
        events = []
        for event in client.events():
            if event.data and event.data != "[DONE]":
                try:
                    events.append(json.loads(event.data))
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse an SSE event's JSON data: {e}")
        if events:
            return {"sse_events": events}
        raise ValueError("No SSE events were found in the stream.")
    except Exception as e:
        logger.warning(f"Failed to parse the payload as Server-Sent Events: {e}")
        return decoded


@app.middleware("http")
async def logging_and_dumping_middleware(request: Request, call_next):
    # Skip logging and payload dumping for liveness and health checks.
    if request.url.path in ["/live", "/health"]:
        return await call_next(request)

    req_uuid = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    payload_file_path = os.path.join("requests", f"{timestamp}_{req_uuid}.json")

    # FastAPI middleware reads the body using `request.body()`.
    # However, `request.body()` can only be awaited once if we don't handle it carefully.
    # Reading it here consumes the stream.
    body = await request.body()

    req_body_parsed = parse_as_json(body)

    # Store it back so the route handler can read it
    async def receive():
        return {"type": "http.request", "body": body}

    request._receive = receive

    dump_data = {
        "id": req_uuid,
        "timestamp": timestamp,
        "request": {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "body": req_body_parsed,
        },
        "response": None,
    }

    response = await call_next(request)

    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    res_body_parsed = None
    if response_body:
        content_type = response.headers.get("content-type", "")
        if "text/event-stream" in content_type or b"data: " in response_body:
            res_body_parsed = parse_as_sse(response_body)
        else:
            res_body_parsed = parse_as_json(response_body)

    dump_data["response"] = {
        "status": response.status_code,
        "headers": dict(response.headers),
        "body": res_body_parsed,
    }

    with open(payload_file_path, "w", encoding="utf-8") as f:
        json.dump(dump_data, f, indent=2)

    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )


@app.get("/live")
async def is_alive() -> dict:
    logger.info("Received a liveness probe request.")
    return {"status": "alive"}


@app.get("/health")
async def is_healthy() -> dict:
    logger.info("Received a health check request.")
    try:
        requests_count = len(os.listdir("requests"))
        logger.info(f"Counted {requests_count} items in the requests directory.")
        return {"status": "healthy", "requests_count": requests_count}
    except Exception as error:
        logger.error(
            f"Failed to count items in the requests directory during health check: {error}"
        )
        return {"status": "unhealthy", "error": str(error)}


@app.api_route("/{path:path}", methods=["GET", "POST"])
async def forward_http_request(path: str, request: Request) -> Response:
    logger.info(f"Received a request for {request.method} {path}")

    target_url = str(request.url).replace(str(request.base_url), TARGET_BASE_URL)

    outbound_headers = {
        k: v for k, v in request.headers.items() if k.lower() not in RESTRICTED_HEADERS
    }

    body = await request.body()

    try:
        logger.info(f"Forward a request to {target_url}")
        upstream_response = await upstream_client.request(
            method=request.method,
            url=target_url,
            headers=outbound_headers,
            content=body,
        )
        logger.info(f"Completed a request for {request.method} {request.url.path}")

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
    except Exception as error:
        logger.error(f"Failed to forward the request to {target_url}: {error}")
        return Response(status_code=502, content=f"Proxy error: {error}")


if __name__ == "__main__":
    logger.info(
        f"The proxy server has started successfully and is now listening on {LISTEN_HOST}:{LISTEN_PORT}."
    )
    logger.info(f"The proxy server is writing logs to {log_file_path}.")
    uvicorn.run(app, host=LISTEN_HOST, port=LISTEN_PORT, log_level="warning")
