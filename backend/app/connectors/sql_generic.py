"""Generic SQL connector using SQLAlchemy (MySQL, MariaDB, etc.)."""
import logging
from typing import Any

from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker

from app.connectors.base import DataConnector

logger = logging.getLogger(__name__)

# Module-level engines - one per connection string
_engines: dict[str, Any] = {}


def _get_engine(connection_string: str, datasource_type: str) -> Any:
    """Get or create a SQLAlchemy engine for the given connection string."""
    if connection_string not in _engines:
        # Add SSL defaults for hosted MySQL
        if datasource_type == "mysql" and "ssl" not in connection_string.lower():
            if "?" in connection_string:
                connection_string += "&ssl_verify_cert=true"
            else:
                connection_string += "?ssl_verify_cert=true"
        
        _engines[connection_string] = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Test connections before using them
        )
    return _engines[connection_string]


class SQLGenericConnector(DataConnector):
    """Generic SQL connector using SQLAlchemy (supports MySQL, MariaDB, etc.)."""

    def __init__(self, connection_string: str, datasource_type: str = "mysql"):
        self.connection_string = connection_string
        self.datasource_type = datasource_type
        self.engine = None
        self.conn = None

    async def connect(self) -> None:
        """Create a connection via SQLAlchemy engine."""
        self.engine = _get_engine(self.connection_string, self.datasource_type)
        self.conn = self.engine.connect()
        logger.info(f"{self.datasource_type} connection established")

    async def get_schema(self) -> dict[str, Any]:
        """
        Introspect the database schema using SQLAlchemy.
        
        Returns:
            Dictionary of tables with their columns and types
        """
        if not self.conn:
            raise RuntimeError("Connection not established")
        
        try:
            inspector = inspect(self.engine)
            schema = {}
            
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                schema[table_name] = [
                    {
                        "column": col["name"],
                        "type": str(col["type"]),
                        "nullable": col["nullable"],
                    }
                    for col in columns
                ]
            
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
        
        try:
            logger.info(f"Executing query: {query[:100]}...")
            result = self.conn.execute(query)
            
            # Convert to list of dicts
            results = [dict(row) for row in result.fetchall()]
            logger.info(f"Query returned {len(results)} rows")
            return results
        
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    async def close(self) -> None:
        """Close the connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info(f"{self.datasource_type} connection closed")
