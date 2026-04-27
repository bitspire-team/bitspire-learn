from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON

from src.core.db import Base


class ResponseLog(Base):
    __tablename__ = "response_logs"

    id = Column(String, primary_key=True, index=True)
    request_id = Column(String, ForeignKey("request_logs.id"))
    timestamp = Column(DateTime)
    status_code = Column(Integer)
    headers = Column(JSON)
    body = Column(JSON, nullable=True)
