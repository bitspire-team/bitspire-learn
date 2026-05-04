import logging

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.models.attachment import Attachment
from src.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class AttachmentRepository(BaseRepository[Attachment]):
    def __init__(self, session: AsyncSession = Depends(get_db)):
        super().__init__(Attachment, session)

    async def get_by_hash(self, hash: str) -> Attachment | None:
        result = await self.session.execute(select(Attachment).where(Attachment.hash == hash))
        return result.scalars().first()
