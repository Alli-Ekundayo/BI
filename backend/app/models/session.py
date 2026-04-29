"""Session and message models."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Message(BaseModel):
    """A single message in a session."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime


class Session(BaseModel):
    """A user session with query history."""

    session_id: str
    datasource_id: str
    messages: list[Message] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
