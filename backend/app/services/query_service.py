"""Query service - orchestrates agent calls and query execution."""
import logging
from typing import Any, Optional

from app.models.response import QueryResponse
from app.agent.orchestrator import run_agent
from app.services.session_service import get_session_service

logger = logging.getLogger(__name__)


class QueryService:
    """Service for query execution and LLM orchestration."""

    async def execute_query(
        self, natural_language_query: str, connector: Any, session_id: Optional[str] = None
    ) -> QueryResponse:
        """
        Execute a natural language query end-to-end.
        
        Args:
            natural_language_query: The user's question
            connector: The initialized DataConnector instance
            session_id: Optional session ID for conversation history
        
        Returns:
            QueryResponse with generated query, results, and visualization type
        """
        try:
            # 1. Get the schema for the datasource
            schema = await connector.get_schema()
            
            # 2. Get conversation history if session_id is provided
            session_messages = []
            if session_id:
                session_service = await get_session_service()
                session_messages = await session_service.get_messages(session_id)
            
            # 3. Run the agent (LLM with tool calling)
            # The agent will handle query generation and execution via tool calling
            final_answer, results, generated_query, viz_type = await run_agent(
                message=natural_language_query,
                schema=schema,
                connector=connector,
                datasource_type=connector.datasource_type if hasattr(connector, 'datasource_type') else "postgres",
                session_messages=session_messages,
            )
            
            # 4. Save the interaction to the session if it exists
            if session_id:
                session_service = await get_session_service()
                await session_service.add_message(session_id, "user", natural_language_query)
                await session_service.add_message(session_id, "assistant", final_answer)
            
            # 5. Return the response
            return QueryResponse(
                answer=final_answer,
                query_generated=generated_query,
                results=results,
                viz_type=viz_type,
                session_id=session_id,
            )
        
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}", exc_info=True)
            return QueryResponse(
                answer=f"Error executing query: {str(e)}",
                query_generated="",
                results=[],
                viz_type="table",
                session_id=session_id,
                error=str(e),
            )


# Global query service instance
_query_service: QueryService | None = None


async def get_query_service() -> QueryService:
    """Get or create the global query service."""
    global _query_service
    if _query_service is None:
        _query_service = QueryService()
    return _query_service
