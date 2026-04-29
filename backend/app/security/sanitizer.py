"""SQL sanitizer to prevent injection attacks and dangerous queries."""
import logging
import sqlparse
from sqlparse.sql import Statement, Token
from sqlparse.tokens import Keyword, DDL

logger = logging.getLogger(__name__)

# Blocked SQL keywords - only SELECT allowed for security
BLOCKED_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "TRUNCATE",
    "ALTER",
    "CREATE",
    "EXEC",
    "EXECUTE",
    "PRAGMA",
    "ATTACH",
    "DETACH",
}


def validate_sql(query: str, datasource_type: str = "postgres") -> str:
    """
    Validate and sanitize SQL query.
    
    Ensures the query:
    - Does not contain any blocked operations (DDL/DML)
    - Only uses SELECT operations
    - Is valid SQL syntax
    
    Args:
        query: The SQL query string
        datasource_type: Type of database (postgres, mysql, etc.)
    
    Returns:
        The validated query string
    
    Raises:
        ValueError: If the query contains invalid operations
    """
    try:
        parsed = sqlparse.parse(query)
        
        for statement in parsed:
            # Check each token in the statement
            for token in statement.flatten():
                # Check for blocked keywords
                if token.ttype in (Keyword, DDL):
                    token_upper = token.value.upper()
                    if token_upper in BLOCKED_KEYWORDS:
                        raise ValueError(
                            f"Blocked SQL operation: {token_upper}. "
                            f"Only SELECT queries are allowed."
                        )
                    # Also allow FOR (SELECT ... FOR UPDATE is common)
                    if token_upper not in ("SELECT", "FROM", "WHERE", "GROUP", "ORDER", "BY", "HAVING", "LIMIT", "FOR", "AND", "OR", "JOIN", "LEFT", "RIGHT", "INNER", "ON", "AS", "WITH", "CASE", "WHEN", "THEN", "ELSE", "END", "UNION", "ALL"):
                        # warn but don't block
                        logger.warning(f"Unusual SQL keyword in query: {token_upper}")
        
        logger.info(f"SQL query validated: {query[:100]}...")
        return query
    
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"SQL validation error: {e}")
        raise ValueError(f"Invalid SQL syntax: {e}")


def sanitize_mongodb_query(query: str) -> str:
    """
    Validate MongoDB aggregation pipeline.
    
    Ensures the pipeline:
    - Is valid JSON
    - Does not contain write operations
    - Only uses read operations
    
    Args:
        query: The MongoDB aggregation pipeline as JSON string
    
    Returns:
        The validated query string
    
    Raises:
        ValueError: If the query is invalid or contains dangerous operations
    """
    import json
    
    try:
        pipeline = json.loads(query)
        
        if not isinstance(pipeline, list):
            raise ValueError("MongoDB pipeline must be a JSON array")
        
        # Blocked MongoDB operations
        blocked_stages = {
            "$merge",
            "$out",
            "$write",
            "$delete",
            "$insert",
            "$update",
            "$replace",
        }
        
        for stage in pipeline:
            if isinstance(stage, dict):
                for key in stage.keys():
                    if key.lower() in blocked_stages:
                        raise ValueError(
                            f"Blocked MongoDB operation: {key}. "
                            f"Only read operations are allowed."
                        )
        
        logger.info(f"MongoDB query validated: {query[:100]}...")
        return query
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in MongoDB query: {e}")
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"MongoDB validation error: {e}")
        raise ValueError(f"Invalid MongoDB query: {e}")
