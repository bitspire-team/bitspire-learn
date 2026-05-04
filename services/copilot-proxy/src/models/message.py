from sqlalchemy import JSON, Column, DateTime, ForeignKey, String

from src.core.db import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    request_log_id = Column(String, ForeignKey("request_logs.id"))
    role = Column(String)
    content = Column(JSON)
    text = Column(String)
    meta_data = Column(JSON)
    model = Column(String)
    created_on = Column(DateTime(timezone=True))
