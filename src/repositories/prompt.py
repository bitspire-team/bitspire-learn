import logging

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.models.prompt import Prompt
from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PromptRepository(BaseRepository[Prompt]):
    def __init__(self, session: AsyncSession = Depends(get_db)):
        super().__init__(Prompt, session)

    async def get_by_hash(self, hash: str) -> Prompt | None:
        result = await self.session.execute(select(Prompt).where(Prompt.hash == hash))
        return result.scalars().first()
