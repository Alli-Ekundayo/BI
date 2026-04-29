# System Architecture

BI Bot is a full-stack application that transforms natural language into database queries.

## High-Level Flow

```
User Query (Natural Language)
    ↓
Frontend UI (React/TypeScript)
    ↓
API Gateway (FastAPI + Nginx)
    ↓
Query Service
    ↓
Agent Orchestrator (Gemini LLM)
    ├─→ Schema Introspection (via Connector)
    ├─→ Query Generation (LLM with tools)
    ├─→ Query Execution (with retry/self-correction)
    └─→ Visualization Recommendation
    ↓
Results + Generated Query + Chart Type
    ↓
Results Cache (In-Process Memory)
    ↓
Frontend Renders Results
```

## Backend Architecture

### API Layer
- **FastAPI**: High-performance Python web framework
- **Middleware**: CORS, rate limiting, error handling
- **Routes**: `/api/v1/query`, `/api/v1/schema`, `/api/v1/session`

### Agent Layer
The agent implements a tool-calling loop with the Google Gemini LLM:

1. **Orchestrator** (`orchestrator.py`): 
   - Manages the LLM conversation loop
   - Dispatches tool calls
   - Implements error recovery

2. **Tools** (`tools.py`):
   - `introspect_schema`: Fetch database/collection schema
   - `generate_query`: Generate SQL/aggregation pipeline
   - `execute_query`: Run the query against the datasource
   - `suggest_visualization`: Recommend chart type based on results

3. **Prompt** (`prompt.py`):
   - Systems prompt with schema injection
   - Query language-specific instructions
   - Error recovery guidance

4. **Retry Logic** (`retry.py`):
   - Max 3 retries per query
   - Error message feedback to LLM
   - Automatic query correction

5. **Memory** (`memory.py`):
   - Session history management
   - Context window truncation to stay within token limits
   - Message history preservation

### Connector Layer
Unified interface for all datasources:

```
DataConnector (abstract)
├── PostgreSQLConnector (psycopg2 + connection pooling)
├── SQLGenericConnector (SQLAlchemy - MySQL, MariaDB)
└── MongoConnector (pymongo - MongoDB, MongoDB Atlas)
```

Each connector implements:
- `connect()`: Establish connection
- `get_schema()`: Introspect schema using native tools
- `execute(query)`: Run query and return results
- `close()`: Clean up connection (return to pool)

### Service Layer
- **QueryService**: Orchestrates the end-to-end query flow
- **SchemaService**: Caches schema introspection results (in-process memory)
- **SessionService**: Stores user sessions and query history (in-process memory)
- **AuthService**: JWT token creation and validation
- **Security**:
  - `sanitizer.py`: SQL/MongoDB validation
  - `rbac.py`: Role-based access control

## Data Flow for a Query

1. **Frontend submits QueryRequest**
   ```json
   {
     "message": "How many active users by country?",
     "datasource": {"type": "postgres", "datasource_id": "prod_db"},
     "session_id": "abc-123"
   }
   ```

2. **Backend retrieves schema**
   - Check in-process cache first (10-minute TTL)
   - Cache miss: introspect the datasource
   - Store in process memory for next query

3. **Agent loop begins**
   ```
   LLM sees schema + user message
   → LLM calls "generate_query" tool
   → Validate query (sanitizer)
   → Execute query with retry logic
   → If error: feed back to LLM, try again (max 3x)
   → Call "suggest_visualization" tool
   → Return final answer + results
   ```

4. **Results returned to frontend**
   ```json
   {
     "answer": "There are 15,234 active users...",
     "query_generated": "SELECT country, COUNT(*) FROM users ...",
     "results": [{"country": "US", "count": 8234}, ...],
     "viz_type": "bar",
     "session_id": "abc-123"
   }
   ```

5. **Frontend renders**
   - Table view by default
   - Chart view with Recharts (bar, line, pie)
   - Raw JSON inspector

## Connection Pooling

**Why**: Hosted databases (Supabase, Neon, PlanetScale, etc.) cap simultaneous connections (usually 20-100).

**Implementation**:
- PostgreSQL: `psycopg2.pool.ThreadedConnectionPool` (min=1, max=5)
- MySQL: SQLAlchemy `QueuePool` (pool_size=5, max_overflow=10)
- MongoDB: Module-level `MongoClient` (reused across requests)

**Pattern**: Connections are returned to the pool after each request (never closed in production), not created fresh.

## Caching Strategy

| What | Where | TTL | Invalidation |
|---|---|---|---|
| Schema | In-process memory | 10 min | Manual (`invalidate_schema` endpoint) |
| Sessions | In-process memory | 24 hrs | Automatic TTL |
| Results | In-memory (frontend) | Session | Page refresh |

## Security Model

1. **Connection strings are server-side only**
   - Frontend sends `datasource_id` (e.g., "prod_db")
   - Backend resolves to full connection string from `DB_URL_{id}` env var
   - Connection string never leaves the server

2. **Query Validation**
   - All LLM-generated SQL/pipelines validated by sanitizer
   - Only SELECT allowed; blocks INSERT, UPDATE, DELETE, DROP, etc.
   - MongoDB aggregations validated; blocks $out, $merge, etc.

3. **Authentication**
   - JWT tokens issued by auth service (24-hour expiration)
   - Tokens required for all protected endpoints
   - Refresh token capability

4. **Authorization**
   - Role-based: Admin, Analyst, Viewer
   - Datasource-level ACLs
   - Rate limiting: 20 queries/minute per user

## Error Handling

| Case | Handling |
|---|---|
| Query syntax error | Caught by execute_query tool, fed back to LLM, retry |
| Table/column not found | Same as above (LLM learns from schema) |
| Connection timeout | Wrapped in QueryResponse with error field |
| LLM generation fails | Max 10 tool calls to prevent infinite loop |
| Invalid token | 401 Unauthorized via FastAPI dependency |

## Performance Considerations

1. **Schema caching**: Expensive introspection (100+ tables) cached for 10 min
2. **Connection pooling**: Reuse connections, avoid connection exhaustion
3. **Batch results**: Large result sets (10k+ rows) paginated on frontend
4. **Nginx compression**: Gzip enabled for API responses
5. **Context window**: Session messages truncated to last 20 to stay within token budget

## Deployment

- **Docker Compose**: Orchestrates backend, frontend, and Nginx
- **Health checks**: All services report health status
- **Environment variables**: All secrets loaded from `.env` file (never hardcoded)
- **SSL/TLS**: Nginx can be configured with certificates for production; DB connections use SSL/`mongodb+srv://`
