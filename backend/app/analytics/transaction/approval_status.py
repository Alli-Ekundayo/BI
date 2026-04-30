import os
import json
import logging
from typing import Any
from app.analytics.base import BaseAnalysis
from app.connectors.nosql import MongoConnector

logger = logging.getLogger(__name__)

class ApprovalStatusAnalysis(BaseAnalysis):
    async def fetch_data(self) -> Any:
        # Determine target table from env var or infer from schema
        table_name = os.getenv("ANALYTICS_TABLE")
        if not table_name:
            schema = await self.db.get_schema()
            if not schema:
                return []
            table_name = list(schema.keys())[0]

        if isinstance(self.db, MongoConnector):
            pipeline = [
                {"$collection": table_name},
                {"$count": "count"}
            ]
            return await self.db.execute(json.dumps(pipeline))
        else:
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            return await self.db.execute(query)

    async def calculate_metric(self, data: Any) -> Any:
        if data and len(data) > 0:
            return data[0].get('count', 0)
        return 0

    async def get_benchmark(self) -> Any:
        return 0

    async def update_benchmark(self, new_metric: Any) -> None:
        pass

    async def analyze(self) -> None:
        data = await self.fetch_data()
        metric = await self.calculate_metric(data)
        benchmark = await self.get_benchmark()
        
        if metric > benchmark:
            await self._dispatch_alert(
                template_key="tx_approval_drop",
                template_args={'rate': 85.0, 'threshold': 95.0}
            )
            await self.update_benchmark(metric)
