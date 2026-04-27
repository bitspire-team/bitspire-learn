import logging
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import Base

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.commit()
        return obj
