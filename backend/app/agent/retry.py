import logging

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


async def execute_with_retry(
    connector, query: str, datasource_type: str
) -> tuple[list[dict] | None, str | None]:
    """
    Execute a query. Transient errors could be retried here, but
    logical errors (syntax, division by zero) should be returned
    to the LLM immediately.
    
    Args:
        connector: The datasource connector
        query: The query to execute
        datasource_type: Type of datasource (postgres, mysql, mongodb)
    
    Returns:
        Tuple of (results, error_message) - one will be None
    """
    try:
        results = await connector.execute(query)
        return results, None
    except Exception as e:
        error_str = str(e)
        logger.error(f"Query execution failed: {error_str}")
        return None, error_str


def format_error_for_llm(error: str, query: str, datasource_type: str) -> str:
    """
    Format an execution error in a way the LLM can learn from.
    
    Args:
        error: The error message
        query: The query that failed
        datasource_type: Type of datasource
    
    Returns:
        Formatted error message for the LLM
    """
    return f"""The {datasource_type} query failed with this error:

{error}

Failed query:
{query}

Please analyze the error and try a corrected version of the query."""
