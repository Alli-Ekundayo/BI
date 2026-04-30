import logging
import json
from typing import List, Optional
from datetime import datetime
from pydantic import ValidationError

from .models import Notification, NotificationCreate, NotificationState
from app.connectors.postgres import PostgreSQLConnector

logger = logging.getLogger(__name__)

class NotificationStore:
    def __init__(self, db_connector: PostgreSQLConnector):
        self.db = db_connector
        
    async def init_tables(self) -> None:
        """Create the notifications table if it doesn't exist."""
        query = """
        CREATE TABLE IF NOT EXISTS notifications (
            id UUID PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            severity VARCHAR(50) NOT NULL,
            category VARCHAR(100) NOT NULL,
            metadata JSONB,
            state VARCHAR(50) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_notifications_state ON notifications(state);
        CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
        """
        try:
            await self.db.execute(query)
            logger.info("Notifications table initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize notifications table: {e}")
            raise

    async def create(self, notif_in: NotificationCreate) -> Notification:
        """Create and persist a new notification."""
        notif = Notification(**notif_in.model_dump())
        query = """
            INSERT INTO notifications (id, title, message, severity, category, metadata, state, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        # In a real app with the PostgreSQLConnector we might need parameter binding,
        # but the connector current interface takes a single query string for simplicity.
        # We assume the connector is extended to support parameter binding safely.
        # For the blueprint, we format safely (mocking parameter passing):
        metadata_json = json.dumps(notif.metadata) if notif.metadata else None
        
        # NOTE: This uses string formatting for blueprint purposes.
        # In production, use parameterized queries to prevent SQL injection.
        safe_query = f"""
            INSERT INTO notifications (id, title, message, severity, category, metadata, state, created_at, updated_at)
            VALUES ('{notif.id}', '{notif.title.replace("'", "''")}', '{notif.message.replace("'", "''")}', 
                    '{notif.severity}', '{notif.category}', '{metadata_json}', '{notif.state}', 
                    '{notif.created_at.isoformat()}', '{notif.updated_at.isoformat()}');
        """
        await self.db.execute(safe_query)
        return notif

    async def get_all(self, limit: int = 50, offset: int = 0) -> List[Notification]:
        """Fetch notifications, ordered by newest first."""
        query = f"""
            SELECT id, title, message, severity, category, metadata, state, created_at, updated_at
            FROM notifications
            ORDER BY created_at DESC
            LIMIT {limit} OFFSET {offset};
        """
        rows = await self.db.execute(query)
        notifications = []
        for row in rows:
            try:
                notifications.append(Notification(**row))
            except ValidationError as e:
                logger.error(f"Invalid notification record found: {e}")
        return notifications

    async def update_state(self, notif_id: str, new_state: NotificationState) -> Optional[Notification]:
        """Update the state of a specific notification (e.g., READ, DISMISSED)."""
        now = datetime.utcnow().isoformat()
        query = f"""
            UPDATE notifications
            SET state = '{new_state}', updated_at = '{now}'
            WHERE id = '{notif_id}'
            RETURNING id, title, message, severity, category, metadata, state, created_at, updated_at;
        """
        # We assume the `execute` method returns rows for UPDATE ... RETURNING
        rows = await self.db.execute(query)
        if rows:
            return Notification(**rows[0])
        return None

    async def get_unread_count(self) -> int:
        """Get the total number of unread notifications."""
        query = f"SELECT COUNT(*) as count FROM notifications WHERE state = '{NotificationState.UNREAD}';"
        rows = await self.db.execute(query)
        if rows:
            return rows[0].get('count', 0)
        return 0
