"""Request models for the API."""
from pydantic import BaseModel
from typing import Literal


class DatasourceConfig(BaseModel):
    """Configuration for a datasource connection."""

    type: Literal["postgres", "mysql", "mongodb"]
    datasource_id: str  # Maps to env var like DB_URL_{datasource_id}


class QueryRequest(BaseModel):
    """Request to execute a natural language query."""

    message: str
    datasource: DatasourceConfig
    session_id: str
