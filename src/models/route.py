from sqlalchemy import Column, DateTime, Integer, String

from src.core.db import Base


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    method = Column(String, index=True)
    path = Column(String, index=True)
    created_on = Column(DateTime)
