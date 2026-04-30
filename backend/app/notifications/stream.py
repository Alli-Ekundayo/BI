import asyncio
import json
import logging
from typing import AsyncGenerator, Set, Dict, Any

logger = logging.getLogger(__name__)

class SSEBroadcaster:
    """
    Server-Sent Events (SSE) broadcaster.
    Manages active subscriptions and pushes events to clients.
    """
    def __init__(self):
        # Set of active async queues for connected clients
        self.clients: Set[asyncio.Queue] = set()
        
    async def subscribe(self) -> AsyncGenerator[str, None]:
        """
        Subscribe to the SSE stream. Yields formatted SSE strings.
        Yields an initial connection success message to keep connection alive.
        """
        queue = asyncio.Queue()
        self.clients.add(queue)
        logger.info(f"New SSE client connected. Total clients: {len(self.clients)}")
        
        try:
            # Send initial ping to establish connection
            yield self._format_sse({"type": "ping", "message": "connected"})
            
            while True:
                # Wait for new messages to be broadcast
                message = await queue.get()
                yield self._format_sse(message)
        except asyncio.CancelledError:
            logger.info("SSE client disconnected.")
        finally:
            self.clients.remove(queue)
            logger.info(f"Client removed. Total clients: {len(self.clients)}")

    async def broadcast(self, event_data: Dict[str, Any], event_type: str = "notification") -> None:
        """
        Push an event to all connected clients.
        
        Args:
            event_data: The data payload to send.
            event_type: The type of event (e.g., 'notification', 'metric_update').
        """
        if not self.clients:
            return
            
        message = {
            "type": event_type,
            "data": event_data
        }
        
        # Put message in every client's queue
        for queue in list(self.clients):
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                logger.warning("A client queue is full, skipping message.")

    def _format_sse(self, data: Dict[str, Any]) -> str:
        """Format the data as an SSE payload string."""
        json_data = json.dumps(data)
        # SSE format: 
        # event: event_type
        # data: {"json": "payload"}
        # \n\n
        return f"event: {data.get('type', 'message')}\ndata: {json_data}\n\n"

# Global instance to be used across the app
broadcaster = SSEBroadcaster()
