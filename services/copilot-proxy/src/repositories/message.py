from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.models import Message
from src.repositories.base import BaseRepository

class MessageRepository(BaseRepository[Message]):
    def __init__(self, session: AsyncSession = Depends(get_db)):
        super().__init__(Message, session)
