from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from src.core.db import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    request_log_id = Column(String, ForeignKey("request_logs.id"))
    role = Column(String)
    content = Column(JSON)
    created_on = Column(DateTime(timezone=True))
