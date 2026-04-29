"""API routes for query, schema, and session management."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.models.request import QueryRequest, DatasourceConfig
from app.models.response import QueryResponse, SchemaResponse, HealthResponse
from app.api.middleware import limiter
from app.connectors.registry import get_connector
from app.services.schema_service import get_schema_service
from app.services.query_service import get_query_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@router.post("/query", response_model=QueryResponse, tags=["query"])
@limiter.limit("20/minute")
async def query(request: Request, req: QueryRequest):
    """
    Execute a natural language query against a datasource.
    
    Returns the generated query, results, and suggested visualization type.
    """
    try:
        # Get the connector for this datasource and use context manager to ensure closure
        async with await get_connector(req.datasource) as connector:
            # Get the query service
            query_service = await get_query_service()
            
            # Execute the query
            result = await query_service.execute_query(
                natural_language_query=req.message,
                connector=connector,
                session_id=req.session_id
            )
            
            return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute query: {str(e)}"
        )


@router.get("/schema", response_model=SchemaResponse, tags=["schema"])
async def get_schema(datasource_type: str, datasource_id: str):
    """
    Fetch the schema for a given datasource.
    
    Results are cached for 10 minutes to avoid expensive introspection.
    """
    try:
        # Create a config object for the connector
        config = DatasourceConfig(type=datasource_type, datasource_id=datasource_id)
        
        # Get the connector and use context manager to ensure closure
        async with await get_connector(config) as connector:
            # Get the schema service
            schema_service = await get_schema_service()
            
            # Get the schema
            schema = await schema_service.get_schema(datasource_id, connector)
            
            return {"tables": schema}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching schema: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch schema: {str(e)}"
        )


@router.post("/session", tags=["session"])
async def create_session(datasource: DatasourceConfig):
    """Create a new session for a datasource."""
    # TODO: Implement session creation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Session endpoint not yet implemented",
    )


@router.get("/session/{session_id}", tags=["session"])
async def get_session(session_id: str):
    """Retrieve session history and metadata."""
    # TODO: Implement session retrieval
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Session endpoint not yet implemented",
    )
