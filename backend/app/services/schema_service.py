"""Schema service - manages datasource schema introspection and caching."""
import json
import logging
from typing import Any
from datetime import datetime, timedelta
from asyncio import Lock

logger = logging.getLogger(__name__)

# Schema cache TTL in seconds (10 minutes)
SCHEMA_CACHE_TTL = 600


class SchemaService:
    """Service for schema management with in-process caching."""

    def __init__(self):
        self._cache: dict[str, tuple[dict[str, Any], datetime]] = {}
        self._lock = Lock()

    async def connect(self) -> None:
        """Initialize in-memory schema cache."""
        logger.info("Schema service using in-process memory cache")

    async def disconnect(self) -> None:
        """Clear in-memory schema cache."""
        async with self._lock:
            self._cache.clear()

    def _make_cache_key(self, datasource_id: str) -> str:
        """Generate a cache key for a datasource schema."""
        return f"schema:{datasource_id}"

    async def _purge_expired(self) -> None:
        """Remove expired cache entries."""
        now = datetime.utcnow()
        expired_keys = [
            key for key, (_, expires_at) in self._cache.items() if expires_at <= now
        ]
        for key in expired_keys:
            del self._cache[key]

    async def get_schema(self, datasource_id: str, connector: Any) -> dict[str, Any]:
        """
        Get schema for a datasource, using cache if available.
        
        Args:
            datasource_id: The datasource identifier
            connector: The DataConnector instance
        
        Returns:
            Dictionary containing the datasource schema
        """
        cache_key = self._make_cache_key(datasource_id)

        # Try to get from in-memory cache first
        async with self._lock:
            await self._purge_expired()
            cached_entry = self._cache.get(cache_key)
            if cached_entry:
                logger.info(f"Schema cache hit for {datasource_id}")
                cached_schema, _ = cached_entry
                return cached_schema
        
        # Cache miss - introspect the schema
        logger.info(f"Schema cache miss for {datasource_id} - introspecting")
        schema = await connector.get_schema()

        # Store in in-memory cache with TTL
        expires_at = datetime.utcnow() + timedelta(seconds=SCHEMA_CACHE_TTL)
        async with self._lock:
            self._cache[cache_key] = (json.loads(json.dumps(schema, default=str)), expires_at)
        logger.info(f"Cached schema for {datasource_id} ({SCHEMA_CACHE_TTL}s TTL)")
        
        return schema

    async def invalidate_schema(self, datasource_id: str) -> None:
        """
        Invalidate cached schema for a datasource.
        
        Call this after schema changes (e.g., new tables added).
        """
        cache_key = self._make_cache_key(datasource_id)
        async with self._lock:
            self._cache.pop(cache_key, None)
        logger.info(f"Invalidated schema cache for {datasource_id}")

    async def invalidate_all_schemas(self) -> None:
        """Invalidate all cached schemas."""
        async with self._lock:
            self._cache.clear()
        logger.info("Invalidated all schema caches")


# Global schema service instance
_schema_service: SchemaService | None = None


async def get_schema_service() -> SchemaService:
    """Get or create the global schema service."""
    global _schema_service
    if _schema_service is None:
        _schema_service = SchemaService()
        await _schema_service.connect()
    return _schema_service
