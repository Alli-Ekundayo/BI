"""Connector registry and factory."""
import os
import logging
from typing import Any

from app.connectors.base import DataConnector
from app.connectors.postgres import PostgreSQLConnector
from app.connectors.sql_generic import SQLGenericConnector
from app.connectors.nosql import MongoConnector
from app.models.request import DatasourceConfig

logger = logging.getLogger(__name__)

# Map datasource types to connector classes
CONNECTOR_MAP: dict[str, type[DataConnector]] = {
    "postgres": PostgreSQLConnector,
    "mysql": SQLGenericConnector,
    "mongodb": MongoConnector,
}


def _resolve_connection_string(datasource_id: str) -> str:
    """
    Resolve a datasource_id to its connection string.
    
    If datasource_id looks like a connection string (contains '://'), it's returned directly.
    Otherwise, it's looked up in environment variables as DB_URL_<DATASOURCE_ID>.
    
    Args:
        datasource_id: Identifier like "prod_db" OR a full connection string.
    
    Returns:
        The connection string
    
    Raises:
        ValueError: If no connection string found for the datasource
    """
    # If it looks like a connection string already, return it
    if "://" in datasource_id:
        return datasource_id

    env_key = f"DB_URL_{datasource_id.upper()}"
    url = os.getenv(env_key)
    if not url:
        raise ValueError(
            f"No connection string found for datasource '{datasource_id}'. "
            f"Set the environment variable {env_key}."
        )
    return url


async def get_connector(config: DatasourceConfig) -> DataConnector:
    """
    Factory function to get a connector for a datasource.
    
    Args:
        config: DatasourceConfig with type and datasource_id
    
    Returns:
        Initialized and connected DataConnector instance
    
    Raises:
        ValueError: If datasource type is unsupported or connection string not found
    """
    # Get the connector class
    connector_class = CONNECTOR_MAP.get(config.type)
    if not connector_class:
        raise ValueError(
            f"Unsupported datasource type: {config.type}. "
            f"Supported types: {list(CONNECTOR_MAP.keys())}"
        )
    
    # Resolve the connection string
    connection_string = _resolve_connection_string(config.datasource_id)
    logger.info(f"Connecting to {config.type} datasource: {config.datasource_id}")
    
    # Create and connect the connector
    if config.type == "mysql":
        connector = connector_class(connection_string, datasource_type="mysql")
    else:
        connector = connector_class(connection_string)
    
    await connector.connect()
    return connector
