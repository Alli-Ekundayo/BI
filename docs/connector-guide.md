# Connector Guide — Adding New Datasources

BI Bot uses a unified connector interface, making it easy to add support for new datasources.

## Architecture

All connectors inherit from `DataConnector` and implement four methods:

```python
class DataConnector(ABC):
    async def connect(self) -> None: ...
    async def get_schema(self) -> dict: ...
    async def execute(self, query: str) -> list[dict]: ...
    async def close(self) -> None: ...
```

## Step 1: Create the Connector Class

Create a new file in `backend/app/connectors/` (e.g., `bigquery.py`):

```python
# backend/app/connectors/bigquery.py
import logging
from google.cloud import bigquery
from app.connectors.base import DataConnector

logger = logging.getLogger(__name__)

class BigQueryConnector(DataConnector):
    def __init__(self, connection_string: str):
        # connection_string contains credentials JSON path or GCP project ID
        self.connection_string = connection_string
        self.client = None

    async def connect(self) -> None:
        from google.cloud import bigquery
        self.client = bigquery.Client(project=self.connection_string)
        logger.info(f"Connected to BigQuery project: {self.connection_string}")

    async def get_schema(self) -> dict[str, Any]:
        schema = {}
        for dataset in self.client.list_datasets():
            dataset_ref = self.client.get_dataset(dataset)
            dataset_tables = self.client.list_tables(dataset_ref)
            for table in dataset_tables:
                table_ref = self.client.get_table(table.reference)
                schema[f"{dataset.dataset_id}.{table.table_id}"] = [
                    {"column": field.name, "type": str(field.field_type)}
                    for field in table_ref.schema
                ]
        return schema

    async def execute(self, query: str) -> list[dict[str, Any]]:
        query_job = self.client.query(query)
        results = query_job.result()
        return [dict(row) for row in results]

    async def close(self) -> None:
        if self.client:
            self.client.close()
```

## Step 2: Register the Connector

Add it to the registry in `backend/app/connectors/registry.py`:

```python
from app.connectors.bigquery import BigQueryConnector

CONNECTOR_MAP = {
    "postgres": PostgreSQLConnector,
    "mysql": SQLGenericConnector,
    "mongodb": MongoConnector,
    "bigquery": BigQueryConnector,  # Add here
}
```

## Step 3: Add Connection String to Environment

In `.env`:

```env
DB_URL_BIGQUERY_PROD=my-project-id
```

## Step 4: Test

Create `backend/tests/test_bigquery_connector.py`:

```python
import pytest
from app.connectors.bigquery import BigQueryConnector

@pytest.mark.asyncio
async def test_bigquery_connection():
    connector = BigQueryConnector("my-project-id")
    await connector.connect()
    schema = await connector.get_schema()
    assert isinstance(schema, dict)
    await connector.close()
```

## Step 5: Update Frontend

The frontend will automatically work with the new connector. Just ensure the datasource type matches:

```typescript
// Frontend can now use:
const datasource: DatasourceConfig = {
  type: 'bigquery',
  datasource_id: 'bigquery_prod'
};
```

## Query Language Considerations

The LLM needs to know what query language your datasource expects. Update `app/agent/prompt.py`:

```python
query_language = {
    "postgres": "PostgreSQL SQL",
    "mysql": "MySQL SQL",
    "mongodb": "MongoDB aggregation pipeline",
    "bigquery": "BigQuery Standard SQL",  # Add here
}.get(datasource_type, "SQL")
```

## Connection String Resolution

Connection strings are resolved from environment variables at runtime:

```python
# User specifies datasource_id: "bigquery_prod"
# System looks for DB_URL_BIGQUERY_PROD in environment
# This ensures credentials never touch the frontend
```

## Common Patterns

### Connection Pooling (SQL-like)
```python
from sqlalchemy.pool import QueuePool

# Module-level pool
_engines = {}

def _get_engine(connection_string):
    if connection_string not in _engines:
        _engines[connection_string] = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
    return _engines[connection_string]
```

### Query Validation
```python
# In execute(), validate queries before running:
from app.security.sanitizer import validate_sql

async def execute(self, query: str) -> list[dict[str, Any]]:
    # Validate
    query = validate_sql(query, datasource_type="bigquery")
    
    # Execute
    ...
```

### Result Serialization
```python
# Some datasources return non-JSON-serializable types
# Convert them to standard types:

results = []
for row in raw_results:
    result_dict = dict(row)
    # Convert special types
    for key, value in result_dict.items():
        if isinstance(value, datetime):
            result_dict[key] = value.isoformat()
        elif isinstance(value, UUID):
            result_dict[key] = str(value)
    results.append(result_dict)
return results
```

## Testing Checklist

- [ ] Connector connects successfully
- [ ] `get_schema()` returns dict of tables/columns
- [ ] `execute()` runs a SELECT and returns results as list of dicts
- [ ] `close()` cleans up resources (connection pool, client, etc.)
- [ ] Connection string resolution works
- [ ] Query validation works
- [ ] Results are JSON-serializable

## Examples

### Snowflake

```python
class SnowflakeConnector(DataConnector):
    def __init__(self, connection_string: str):
        # connection_string: "user:password@account.region"
        self.connection_string = connection_string
        self.conn = None

    async def connect(self):
        import snowflake.connector
        user, password, account = self._parse_connection_string()
        self.conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
        )

    async def get_schema(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS")
        schema = {}
        for table, column in cursor.fetchall():
            schema.setdefault(table, []).append({"column": column})
        return schema

    async def execute(self, query: str):
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    async def close(self):
        if self.conn:
            self.conn.close()
```

### Apache Spark / Databricks

```python
class SparkConnector(DataConnector):
    def __init__(self, connection_string: str):
        # Databricks workspace URL + personal access token
        self.workspace_url, self.token = connection_string.split("|")
        self.client = None

    async def connect(self):
        from databricks import sql
        self.client = sql.connect(
            host=self.workspace_url,
            http_path="/sql/1.0/warehouses/...",
            auth_type="pat",
            token=self.token,
        )

    async def get_schema(self):
        # Query system tables for schema
        ...

    async def execute(self, query: str):
        cursor = self.client.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    async def close(self):
        if self.client:
            self.client.close()
```

## Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Common issues:

- **Connection refused**: Check connection string, credentials, network access
- **Table not found**: Ensure schema introspection returns actual table names
- **Results not serializable**: Convert timestamps, UUIDs, etc. to strings
- **Slow queries**: Use connection pooling and index on frequently queried columns
