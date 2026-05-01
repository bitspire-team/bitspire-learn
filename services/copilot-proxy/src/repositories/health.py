import logging

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db

logger = logging.getLogger(__name__)


class HealthRepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def check(self) -> None:
        await self.session.execute(text("SELECT 1"))
