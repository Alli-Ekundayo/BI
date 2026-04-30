import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.analytics.base import BaseAnalysis
from app.notifications.models import Notification
from app.notifications.stream import broadcaster

class MockAnalysis(BaseAnalysis):
    """A mock implementation of BaseAnalysis for testing."""
    async def fetch_data(self):
        return {"value": 100}
        
    async def calculate_metric(self, data):
        return data["value"] * 1.5
        
    async def get_benchmark(self):
        return 120
        
    async def update_benchmark(self, new_metric):
        pass
        
    async def analyze(self):
        data = await self.fetch_data()
        metric = await self.calculate_metric(data)
        benchmark = await self.get_benchmark()
        
        if metric > benchmark:
            await self._dispatch_alert(
                template_key="tx_volume_spike",
                template_args={
                    "channel": "API",
                    "percentage": int(((metric/benchmark) - 1) * 100),
                    "timeframe": "last hour"
                }
            )

@pytest.mark.asyncio
async def test_base_analysis_execution():
    """Test that a concrete analysis job correctly triggers alerts and broadcasts."""
    mock_db = AsyncMock()
    mock_notif_store = AsyncMock()
    
    # Mock the return value of notif_store.create
    saved_notif = Notification(
        id="test-id",
        title="Transaction Volume Spike",
        message="Transaction volume for API has increased by 25% in the last last hour.",
        severity="WARNING",
        category="transaction"
    )
    mock_notif_store.create.return_value = saved_notif
    
    # Subscribe to the broadcaster to catch the event
    subscription = broadcaster.subscribe()
    await anext(subscription) # skip ping
    
    analysis = MockAnalysis(mock_db, mock_notif_store)
    
    # Execute the analysis
    await analysis.execute()
    
    # Verify notif_store.create was called
    assert mock_notif_store.create.called
    
    # Verify the message was broadcasted
    msg = await anext(subscription)
    assert "event: notification" in msg
    assert "Transaction Volume Spike" in msg
    assert "25%" in msg
