import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.db import AsyncSessionLocal
from src.repositories import RequestLogRepository, ResponseLogRepository
from src.repositories.message import MessageRepository
from src.repositories.repository import RepositoryRepository
from src.repositories.user import UserRepository
from src.services import LoggingService
from src.services.request_insight import RequestInsightService

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        async with AsyncSessionLocal() as session:
            # Dependencies are manually resolved because middleware runs outside of the FastAPI dependency injection container.
            service = LoggingService(
                request_repo=RequestLogRepository(session),
                response_repo=ResponseLogRepository(session),
            )
            request_log = await service.log_request(request)
            response = await call_next(request)
            response_log = await service.log_response(request, response)

            # Dependencies are manually resolved because middleware runs outside of the FastAPI dependency injection container.
            insight_service = RequestInsightService(
                user_repo=UserRepository(session),
                repo_repo=RepositoryRepository(session),
                message_repo=MessageRepository(session),
            )
            try:
                await insight_service.extract_and_store(request_log, response_log)
            except Exception as e:
                logger.warning("Request insight extraction failed (non-fatal): %s", e)

            return response
