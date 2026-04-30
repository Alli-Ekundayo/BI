from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from pydantic import BaseModel, Field

class NotificationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    SUCCESS = "SUCCESS"

class NotificationState(str, Enum):
    UNREAD = "UNREAD"
    READ = "READ"
    DISMISSED = "DISMISSED"
    ACKNOWLEDGED = "ACKNOWLEDGED"

class NotificationBase(BaseModel):
    title: str
    message: str
    severity: NotificationSeverity = NotificationSeverity.INFO
    category: str = "general"
    metadata: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    state: NotificationState = NotificationState.UNREAD
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
