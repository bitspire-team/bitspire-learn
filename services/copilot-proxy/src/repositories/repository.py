import logging

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.models.repository import Repository
from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class RepositoryRepository(BaseRepository[Repository]):
    def __init__(self, session: AsyncSession = Depends(get_db)):
        super().__init__(Repository, session)

    async def get_by_nwo(self, nwo: str) -> Repository | None:
        result = await self.session.execute(select(Repository).where(Repository.nwo == nwo))
        return result.scalars().first()
