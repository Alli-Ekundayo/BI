"""PostgreSQL connector using psycopg2."""
import logging
from typing import Any
import psycopg2
import psycopg2.extras
from psycopg2 import pool as pg_pool

from app.connectors.base import DataConnector

logger = logging.getLogger(__name__)

# Module-level pool - shared across requests
_pools: dict[str, pg_pool.ThreadedConnectionPool] = {}


def _get_pool(connection_string: str) -> pg_pool.ThreadedConnectionPool:
    """Get or create a connection pool for the given connection string."""
    if connection_string not in _pools:
        _pools[connection_string] = pg_pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,  # Increased from 5 to better handle concurrent requests
            dsn=connection_string,
        )
    return _pools[connection_string]


class PostgreSQLConnector(DataConnector):
    """PostgreSQL connector using psycopg2 with connection pooling."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.conn = None
        self._pool = None

    async def connect(self) -> None:
        """Get a connection from the pool."""
        self._pool = _get_pool(self.connection_string)
        self.conn = self._pool.getconn()
        logger.info("PostgreSQL connection acquired from pool")

    async def get_schema(self) -> dict[str, Any]:
        """
        Introspect the PostgreSQL schema.
        
        Returns:
            Dictionary of tables with their columns and types
        """
        if not self.conn:
            raise RuntimeError("Connection not established")
        
        cursor = self.conn.cursor()
        try:
            query = """
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            
            schema = {}
            for table_name, column_name, data_type, is_nullable in rows:
                if table_name not in schema:
                    schema[table_name] = []
                schema[table_name].append({
                    "column": column_name,
                    "type": data_type,
                    "nullable": is_nullable == "YES",
                })
            
            logger.info(f"Retrieved schema for {len(schema)} tables")
            return schema
        
        except Exception as e:
            logger.error(f"Failed to get schema: {e}")
            raise

    async def execute(self, query: str) -> list[dict[str, Any]]:
        """
        Execute a query and return results as list of dicts.
        
        Args:
            query: SQL query string
        
        Returns:
            List of result rows as dictionaries
        """
        if not self.conn:
            raise RuntimeError("Connection not established")
        
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            logger.info(f"Executing query: {query[:100]}...")
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            self.conn.commit()
            cursor.close()
            logger.info(f"Query returned {len(results)} rows")
            return results
        
        except Exception as e:
            self.conn.rollback()
            cursor.close()
            logger.error(f"Query execution failed: {e}")
            raise

    async def close(self) -> None:
        """Return the connection to the pool."""
        if self._pool and self.conn:
            self._pool.putconn(self.conn)
            self.conn = None
            logger.info("PostgreSQL connection returned to pool")
