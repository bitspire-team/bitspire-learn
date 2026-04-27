import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.db import AsyncSessionLocal
from src.repositories import RequestLogRepository, ResponseLogRepository
from src.services import LoggingService

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        async with AsyncSessionLocal() as session:
            service = LoggingService(
                request_repo=RequestLogRepository(session),
                response_repo=ResponseLogRepository(session),
            )
            await service.log_request(request)

            response = await call_next(request)
            reconstructed = await service.log_response(request, response)

            return reconstructed
