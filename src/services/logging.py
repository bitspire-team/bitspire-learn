import json
import logging
import uuid
from datetime import datetime

from fastapi import Depends, Request, Response

from src.models import RequestLog, ResponseLog
from src.repositories import RequestLogRepository, ResponseLogRepository

logger = logging.getLogger(__name__)


class LoggingService:
    def __init__(
        self,
        request_repo: RequestLogRepository = Depends(),
        response_repo: ResponseLogRepository = Depends(),
    ):
        self.request_repo = request_repo
        self.response_repo = response_repo

    @staticmethod
    def parse_as_json(body_bytes: bytes):
        if not body_bytes:
            return None
        decoded = body_bytes.decode("utf-8", errors="replace")
        try:
            return json.loads(decoded)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse the payload as JSON: %s", e)
            return decoded

    @staticmethod
    def parse_as_sse(body_bytes: bytes):
        if not body_bytes:
            return None
        decoded = body_bytes.decode("utf-8", errors="replace")
        events = []

        for line in decoded.splitlines():
            if line.startswith("data: "):
                data = line[6:].strip()
                if data and data != "[DONE]":
                    try:
                        events.append(json.loads(data))
                    except json.JSONDecodeError as e:
                        logger.warning(
                            "Failed to parse an SSE event's JSON data: %s", e
                        )

        if events:
            return {"sse_events": events}

        logger.warning(
            "Failed to parse the payload as Server-Sent Events: no valid events found."
        )
        return decoded

    @staticmethod
    async def read_request_body(request: Request):
        body = await request.body()

        # Reassign so downstream code can read the consumed body again.
        async def receive():
            return {"type": "http.request", "body": body}

        request._receive = receive

        if not body:
            return None
        content_type = request.headers.get("content-type", "")
        if "json" in content_type.lower():
            return LoggingService.parse_as_json(body)
        return body.decode("utf-8", errors="replace")

    @staticmethod
    async def read_response_body(response: Response):
        if not hasattr(response, "body_iterator"):
            body = getattr(response, "body", b"")
        else:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            # Reassign so Starlette can still send the consumed body to the client.
            async def body_iterator():
                yield body

            response.body_iterator = body_iterator()

        if not body:
            return None
        content_type = response.headers.get("content-type", "")
        if "text/event-stream" in content_type or b"data: " in body:
            return LoggingService.parse_as_sse(body)
        if "json" in content_type.lower():
            return LoggingService.parse_as_json(body)
        return body.decode("utf-8", errors="replace")

    async def log_request(self, request: Request) -> RequestLog:
        req_uuid = str(uuid.uuid4())
        # Stored on request.state so log_response can link the response to this request.
        request.state.req_uuid = req_uuid

        body = await self.read_request_body(request)

        request_log = await self.request_repo.create(
            id=req_uuid,
            timestamp=datetime.now(),
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            query=str(request.url.query) if request.url.query else None,
            headers=dict(request.headers),
            body=body,
        )
        logger.info(
            "Logged request %s %s to the database.",
            request.method,
            request.url.path,
        )
        return request_log

    async def log_response(self, request: Request, response: Response) -> ResponseLog:
        req_uuid = getattr(request.state, "req_uuid", str(uuid.uuid4()))

        response_body = await self.read_response_body(response)

        response_log = await self.response_repo.create(
            id=str(uuid.uuid4()),
            request_id=req_uuid,
            timestamp=datetime.now(),
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response_body,
        )
        logger.info(
            "Logged response with status %d for request %s to the database.",
            response.status_code,
            req_uuid,
        )
        return response_log
