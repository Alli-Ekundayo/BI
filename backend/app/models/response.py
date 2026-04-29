"""Response models for the API."""
from pydantic import BaseModel
from typing import Any, Literal, Optional


class QueryResponse(BaseModel):
    """Response from a query execution."""

    answer: str
    query_generated: str
    results: list[dict[str, Any]]
    viz_type: Literal["table", "bar", "line", "pie"]
    session_id: str
    error: Optional[str] = None


class SchemaResponse(BaseModel):
    """Schema definition for a datasource."""

    tables: dict[str, list[dict[str, Any]]]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
