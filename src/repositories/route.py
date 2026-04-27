import logging

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.models.route import Route
from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class RouteRepository(BaseRepository[Route]):
    def __init__(self, session: AsyncSession = Depends(get_db)):
        super().__init__(Route, session)

    async def get_by_method_and_path(self, method: str, path: str) -> Route | None:
        result = await self.session.execute(
            select(Route).where(Route.method == method, Route.path == path)
        )
        return result.scalars().first()
