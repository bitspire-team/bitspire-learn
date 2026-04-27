import hashlib

from sqlalchemy import Column, DateTime, Integer, String, Text

from src.core.db import Base


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hash = Column(String(64), unique=True, index=True)
    role = Column(String)
    content = Column(Text)
    created_on = Column(DateTime)

    @staticmethod
    def compute_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
