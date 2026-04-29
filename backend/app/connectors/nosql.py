"""MongoDB connector using pymongo."""
import logging
import json
from typing import Any

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

from app.connectors.base import DataConnector

logger = logging.getLogger(__name__)

# Module-level clients - one per connection string
_clients: dict[str, MongoClient] = {}


def _get_client(connection_string: str) -> MongoClient:
    """Get or create a MongoDB client for the given connection string."""
    if connection_string not in _clients:
        _clients[connection_string] = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
    return _clients[connection_string]


class MongoConnector(DataConnector):
    """MongoDB connector using pymongo."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.client = None
        self.db = None

    async def connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            self.client = _get_client(self.connection_string)
            # Test the connection
            self.client.admin.command("ping")
            
            # Get the default database from connection string
            # Format: mongodb+srv://user:pass@host/dbname
            # If no dbname specified, use "admin"
            url_parts = self.connection_string.split("/")
            if len(url_parts) > 3 and url_parts[-1]:
                dbname = url_parts[-1].split("?")[0]
                self.db = self.client[dbname]
            else:
                # Fallback to admin database
                self.db = self.client["admin"]
            
            logger.info(f"MongoDB connection established to {self.db.name}")
        
        except ServerSelectionTimeoutError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def get_schema(self) -> dict[str, Any]:
        """
        Introspect the MongoDB schema by sampling documents.
        
        Returns:
            Dictionary of collections with their fields
        """
        if not self.db:
            raise RuntimeError("Connection not established")
        
        try:
            schema = {}
            
            for collection_name in self.db.list_collection_names():
                collection = self.db[collection_name]
                
                # Sample up to 10 documents to infer schema
                sample_docs = list(collection.find().limit(10))
                
                # Collect all field names and types from samples
                fields = set()
                field_types = {}
                
                for doc in sample_docs:
                    for key, value in doc.items():
                        fields.add(key)
                        if key not in field_types:
                            field_types[key] = type(value).__name__
                
                # Build schema for this collection
                schema[collection_name] = [
                    {"column": field, "type": field_types.get(field, "unknown")}
                    for field in sorted(fields)
                ]
            
            logger.info(f"Retrieved schema for {len(schema)} collections")
            return schema
        
        except Exception as e:
            logger.error(f"Failed to get schema: {e}")
            raise

    async def execute(self, query: str) -> list[dict[str, Any]]:
        """
        Execute a MongoDB aggregation pipeline.
        
        Args:
            query: JSON string representing MongoDB aggregation pipeline
                   (e.g., '[{"$match": {...}}, {"$group": {...}}]')
        
        Returns:
            List of result documents
        """
        if not self.db:
            raise RuntimeError("Connection not established")
        
        try:
            # Parse the query as a MongoDB aggregation pipeline
            try:
                pipeline = json.loads(query)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON aggregation pipeline: {query}")
            
            if not isinstance(pipeline, list):
                raise ValueError("MongoDB pipeline must be a JSON array")
            
            # Extract collection name from first stage if possible
            # For now, assume we're working with a specific collection
            # This would need to be improved for multi-collection queries
            collection_name = None
            for stage in pipeline:
                if "$collection" in stage:
                    collection_name = stage["$collection"]
                    break
            
            if not collection_name:
                # Fallback: use first collection in database
                collections = self.db.list_collection_names()
                if not collections:
                    raise ValueError("No collections found in database")
                collection_name = collections[0]
                logger.warning(f"No collection specified, using first: {collection_name}")
            
            collection = self.db[collection_name]
            
            # Execute the aggregation pipeline
            logger.info(f"Executing aggregation on {collection_name}")
            results = list(collection.aggregate(pipeline))
            
            # Convert ObjectId to strings for JSON serialization
            for result in results:
                if "_id" in result:
                    result["_id"] = str(result["_id"])
            
            logger.info(f"Aggregation returned {len(results)} documents")
            return results
        
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    async def close(self) -> None:
        """Close the MongoDB connection."""
        if self.client:
            # Don't close - keep in pool for reuse
            logger.info("MongoDB connection returned to pool")
