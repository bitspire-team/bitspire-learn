import logging

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.models.token_usage import TokenUsage
from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class TokenUsageRepository(BaseRepository[TokenUsage]):
    def __init__(self, session: AsyncSession = Depends(get_db)):
        super().__init__(TokenUsage, session)

