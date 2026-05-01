from sqlalchemy import Column, DateTime, Integer, String

from src.core.db import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner = Column(String, index=True)
    name = Column(String, index=True)
    nwo = Column(String, unique=True, index=True)
    created_on = Column(DateTime(timezone=True))
