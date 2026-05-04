import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.db import AsyncSessionLocal
from src.repositories import RequestLogRepository, ResponseLogRepository
from src.repositories.attachment import AttachmentRepository
from src.repositories.message import MessageRepository
from src.repositories.prompt import PromptRepository
from src.repositories.repository import RepositoryRepository
from src.repositories.route import RouteRepository
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
                route_repo=RouteRepository(session),
                user_repo=UserRepository(session),
                prompt_repo=PromptRepository(session),
                repo_repo=RepositoryRepository(session),
                attachment_repo=AttachmentRepository(session),
                message_repo=MessageRepository(session),
            )
            try:
                await insight_service.extract_and_store(request_log, response_log)
            except Exception as e:
                logger.warning(f"Request insight extraction failed (non-fatal): {e}")

            return response
