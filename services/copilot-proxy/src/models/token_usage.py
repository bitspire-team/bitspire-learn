from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from src.core.db import Base


class TokenUsage(Base):
    """Stores token usage analytics for AI interactions."""

    __tablename__ = "token_usages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_log_id = Column(String, ForeignKey("request_logs.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=True, index=True)
    interaction_id = Column(String, index=True)
    model = Column(String, index=True)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    created_on = Column(DateTime(timezone=True))
