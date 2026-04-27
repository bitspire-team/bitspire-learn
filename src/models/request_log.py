from sqlalchemy import Column, String, DateTime, JSON

from src.core.db import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime)
    method = Column(String)
    url = Column(String)
    path = Column(String)
    query = Column(String, nullable=True)
    headers = Column(JSON)
    body = Column(JSON, nullable=True)
