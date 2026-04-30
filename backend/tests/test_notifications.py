import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.notifications.templates import TemplateEngine
from app.notifications.models import NotificationSeverity, NotificationState, NotificationCreate
from app.notifications.stream import SSEBroadcaster
from app.notifications.store import NotificationStore

@pytest.mark.asyncio
async def test_template_engine_format():
    """Test that templates are correctly formatted with arguments."""
    template_key = "tx_volume_spike"
    args = {
        "channel": "POS",
        "percentage": 25,
        "timeframe": "1 hour"
    }
    
    formatted = TemplateEngine.format_alert(template_key, **args)
    
    assert formatted["title"] == "Transaction Volume Spike"
    assert "POS" in formatted["message"]
    assert "25%" in formatted["message"]
    assert "1 hour" in formatted["message"]
    assert formatted["severity"] == NotificationSeverity.WARNING
    assert formatted["category"] == "transaction"
    assert formatted["metadata"] == args

@pytest.mark.asyncio
async def test_sse_broadcaster():
    """Test that SSE broadcaster correctly pushes messages to subscribers."""
    broadcaster = SSEBroadcaster()
    
    # Create a subscriber
    subscription = broadcaster.subscribe()
    
    # Get the initial ping message
    first_msg = await anext(subscription)
    assert "event: ping" in first_msg
    assert "connected" in first_msg
    
    # Broadcast a message
    test_data = {"id": "123", "title": "Test Alert"}
    
    # Run broadcast in background
    asyncio.create_task(broadcaster.broadcast(test_data, event_type="notification"))
    
    # Wait for the message in the stream
    second_msg = await anext(subscription)
    assert "event: notification" in second_msg
    assert "Test Alert" in second_msg

@pytest.mark.asyncio
async def test_notification_store_create():
    """Test that NotificationStore correctly formats the SQL for creation."""
    mock_db = AsyncMock()
    store = NotificationStore(mock_db)
    
    notif_in = NotificationCreate(
        title="Test Notification",
        message="This is a test message",
        severity=NotificationSeverity.INFO,
        category="system"
    )
    
    await store.create(notif_in)
    
    # Verify that execute was called with an INSERT statement
    args, _ = mock_db.execute.call_args
    query = args[0]
    assert "INSERT INTO notifications" in query
    assert "Test Notification" in query
    assert "This is a test message" in query
    assert "INFO" in query
