import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.connectors.base import DataConnector
from app.notifications.templates import TemplateEngine
from app.notifications.store import NotificationStore
from app.notifications.models import NotificationCreate
from app.notifications.stream import broadcaster

logger = logging.getLogger(__name__)

class BaseAnalysis(ABC):
    """
    Abstract base class for all analytics jobs.
    Defines the workflow: calculate metric -> check threshold -> alert -> save benchmark.
    """
    def __init__(self, db: DataConnector, notif_store: NotificationStore):
        self.db = db
        self.notif_store = notif_store

    @abstractmethod
    async def fetch_data(self) -> Any:
        """Fetch raw data from the database required for this analysis."""
        pass

    @abstractmethod
    async def calculate_metric(self, data: Any) -> Any:
        """Process the raw data to calculate the core metric."""
        pass

    @abstractmethod
    async def get_benchmark(self) -> Any:
        """Fetch the current benchmark/rolling average from the benchmark store."""
        pass

    @abstractmethod
    async def update_benchmark(self, new_metric: Any) -> None:
        """Update the benchmark store with the newly calculated metric."""
        pass

    async def _dispatch_alert(self, template_key: str, template_args: Dict[str, Any]) -> None:
        """
        Formats the alert using TemplateEngine, persists it in Postgres,
        and pushes it to active SSE clients.
        """
        try:
            # 1. Format Alert
            formatted_data = TemplateEngine.format_alert(template_key, **template_args)
            
            # 2. Persist State in Postgres
            notif_in = NotificationCreate(**formatted_data)
            saved_notif = await self.notif_store.create(notif_in)
            
            # 3. Push Event via SSE Broadcaster
            # We serialize the full notification object including its generated ID and timestamps
            await broadcaster.broadcast(
                event_data=saved_notif.model_dump(mode="json"),
                event_type="notification"
            )
            logger.info(f"Dispatched alert [{template_key}] successfully. ID: {saved_notif.id}")
        except Exception as e:
            logger.error(f"Failed to dispatch alert {template_key}: {e}")

    async def execute(self) -> None:
        """
        Main execution loop for an analytics job.
        Subclasses should typically implement `analyze` to house specific logic 
        and call `_dispatch_alert` when thresholds are breached.
        """
        try:
            await self.analyze()
        except Exception as e:
            logger.error(f"Analysis job {self.__class__.__name__} failed: {e}")
            await self._dispatch_alert(
                template_key="sys_job_failure",
                template_args={"job_name": self.__class__.__name__, "error": str(e)}
            )

    @abstractmethod
    async def analyze(self) -> None:
        """
        The core logic tying fetch, calculate, compare, and alert together.
        Must be implemented by subclasses.
        """
        pass
