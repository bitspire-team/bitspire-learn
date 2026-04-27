import logging

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.models.user import User
from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession = Depends(get_db)):
        super().__init__(User, session)

    async def get_by_github_id(self, github_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.github_id == github_id)
        )
        return result.scalars().first()

    async def get_by_machine_id(self, machine_id: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.machine_id == machine_id)
        )
        return result.scalars().first()

    async def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.session.commit()
        return user
