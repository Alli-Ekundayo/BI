"""Base connector abstract class."""
from abc import ABC, abstractmethod
from typing import Any


class DataConnector(ABC):
    """Abstract base class for all datasource connectors."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish the connection to the datasource."""
        pass

    @abstractmethod
    async def get_schema(self) -> dict[str, Any]:
        """
        Return the datasource schema as a dictionary.
        
        Returns:
            Dictionary mapping table/collection names to their fields
            Format: {
                "table_name": [
                    {"column": "col_name", "type": "data_type"},
                    ...
                ]
            }
        """
        pass

    @abstractmethod
    async def execute(self, query: str) -> list[dict[str, Any]]:
        """
        Execute a query against the datasource.
        
        Args:
            query: The query string (SQL, MongoDB aggregation, etc.)
        
        Returns:
            List of result rows as dictionaries
        
        Raises:
            Exception: If query execution fails
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the connection to the datasource."""
        pass

    async def __aenter__(self) -> "DataConnector":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
