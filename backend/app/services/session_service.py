"""Session service - manages user sessions and query history."""
import logging
from typing import Any, Optional
from datetime import datetime, timedelta
import uuid
from asyncio import Lock
from app.models.session import Session, Message

logger = logging.getLogger(__name__)

# Session TTL in seconds (24 hours)
SESSION_TTL = 86400


class SessionService:
    """Service for session management with in-process memory."""

    def __init__(self):
        self._sessions: dict[str, Session] = {}
        self._lock = Lock()

    async def connect(self) -> None:
        """Initialize in-memory store (no external dependency)."""
        logger.info("Session service using in-process memory")

    async def disconnect(self) -> None:
        """Clear in-memory sessions."""
        async with self._lock:
            self._sessions.clear()

    def _is_expired(self, session: Session) -> bool:
        """Return True if session has expired."""
        return bool(session.expires_at and session.expires_at <= datetime.utcnow())

    async def _purge_expired(self) -> None:
        """Remove expired sessions from in-memory store."""
        expired_ids = [
            sid for sid, sess in self._sessions.items() if self._is_expired(sess)
        ]
        for sid in expired_ids:
            del self._sessions[sid]

    async def create_session(self, datasource_id: str, user_id: Optional[str] = None) -> Session:
        """
        Create a new session.
        
        Args:
            datasource_id: The datasource this session is for
            user_id: Optional user ID
        
        Returns:
            New Session object
        """
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        session = Session(
            session_id=session_id,
            datasource_id=datasource_id,
            messages=[],
            created_at=now,
            updated_at=now,
            expires_at=now + timedelta(seconds=SESSION_TTL),
        )
        
        async with self._lock:
            await self._purge_expired()
            self._sessions[session_id] = session
        logger.info(f"Created in-memory session: {session_id}")
        
        return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve a session.
        
        Args:
            session_id: The session ID
        
        Returns:
            Session object or None if not found
        """
        async with self._lock:
            await self._purge_expired()
            session = self._sessions.get(session_id)
            if not session:
                logger.info(f"Session not found: {session_id}")
                return None
            return session

    async def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to a session. Creates session if it doesn't exist.
        
        Args:
            session_id: The session ID
            role: Message role (user or assistant)
            content: Message content
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                logger.info(f"Session {session_id} not found, creating new one.")
                now = datetime.utcnow()
                session = Session(
                    session_id=session_id,
                    datasource_id="unknown",  # We don't know the datasource here, but we can update it later
                    messages=[],
                    created_at=now,
                    updated_at=now,
                    expires_at=now + timedelta(seconds=SESSION_TTL),
                )
                self._sessions[session_id] = session
            
            # Add message
            message = Message(role=role, content=content, timestamp=datetime.utcnow())
            session.messages.append(message)
            session.updated_at = datetime.utcnow()
            session.expires_at = datetime.utcnow() + timedelta(seconds=SESSION_TTL)
            
        logger.info(f"Added message to session: {session_id}")

    async def get_messages(self, session_id: str) -> list[dict[str, Any]]:
        """
        Get all messages in a session.
        
        Args:
            session_id: The session ID
        
        Returns:
            List of message dictionaries with role and content
        """
        session = await self.get_session(session_id)
        if not session:
            return []
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in session.messages
        ]

    async def delete_session(self, session_id: str) -> None:
        """
        Delete a session.
        
        Args:
            session_id: The session ID
        """
        async with self._lock:
            self._sessions.pop(session_id, None)
        logger.info(f"Deleted session: {session_id}")


# Global session service instance
_session_service: SessionService | None = None


async def get_session_service() -> SessionService:
    """Get or create the global session service."""
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
        await _session_service.connect()
    return _session_service
