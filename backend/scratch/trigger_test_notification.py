import asyncio
import logging
from app.notifications.stream import broadcaster
from app.notifications.models import NotificationSeverity

logging.basicConfig(level=logging.INFO)

async def trigger():
    print("Broadcasting test notification in 2 seconds...")
    await asyncio.sleep(2)
    
    test_notif = {
        "id": "manual-test-id",
        "title": "Manual Test Notification",
        "message": "This is a manually triggered notification for testing the SSE stream.",
        "severity": NotificationSeverity.SUCCESS,
        "category": "system",
        "created_at": "2026-04-30T10:00:00Z"
    }
    
    print(f"Broadcasting: {test_notif['title']}")
    await broadcaster.broadcast(test_notif, event_type="notification")
    print("Done. If you have the frontend open and connected to /api/notifications/stream, you should see it.")

if __name__ == "__main__":
    asyncio.run(trigger())
