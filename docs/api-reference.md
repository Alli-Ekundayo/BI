# API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/health`) require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Health Check

```http
GET /health
```

Check if the API is running.

**Response:**
```json
{
  "status": "ok"
}
```

**Status Code:** `200 OK`

---

### Execute Query

```http
POST /query
```

Execute a natural language query against a datasource.

**Request:**
```json
{
  "message": "How many active users by country?",
  "datasource": {
    "type": "postgres",
    "datasource_id": "prod_db"
  },
  "session_id": "abc-123-def"
}
```

**Parameters:**
- `message` (string, required): Natural language query
- `datasource.type` (enum, required): `postgres`, `mysql`, or `mongodb`
- `datasource.datasource_id` (string, required): Datasource identifier (resolved from `DB_URL_{id}` env var)
- `session_id` (string, required): Session ID for history tracking

**Response:**
```json
{
  "answer": "There are 15,234 active users across 42 countries...",
  "query_generated": "SELECT country, COUNT(*) as count FROM users WHERE active = true GROUP BY country ORDER BY count DESC",
  "results": [
    {"country": "US", "count": 8234},
    {"country": "GB", "count": 2145},
    {"country": "CA", "count": 1876}
  ],
  "viz_type": "bar",
  "session_id": "abc-123-def",
  "error": null
}
```

**Response Fields:**
- `answer` (string): Natural language summary of the query results
- `query_generated` (string): The generated SQL or aggregation pipeline
- `results` (array): Query results as list of objects
- `viz_type` (string): Recommended visualization: `table`, `bar`, `line`, or `pie`
- `session_id` (string): The session ID (round-trip)
- `error` (string, optional): Error message if query failed

**Status Codes:**
- `200 OK`: Query executed successfully
- `400 Bad Request`: Invalid request format or unsupported datasource type
- `401 Unauthorized`: Missing or invalid authentication token
- `429 Too Many Requests`: Rate limit exceeded (20 requests/minute per user)
- `500 Internal Server Error`: Server-side error or database connection failure

**Rate Limiting:**
- 20 requests per minute per authenticated user
- Returns `429 Too Many Requests` when exceeded

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me top 10 products by revenue",
    "datasource": {"type": "postgres", "datasource_id": "prod_db"},
    "session_id": "session-123"
  }'
```

---

### Get Schema

```http
GET /schema?datasource_type=postgres&datasource_id=prod_db
```

Retrieve the schema for a datasource.

**Query Parameters:**
- `datasource_type` (enum, required): `postgres`, `mysql`, or `mongodb`
- `datasource_id` (string, required): Datasource identifier

**Response:**
```json
{
  "tables": {
    "users": [
      {"column": "id", "type": "integer", "nullable": false},
      {"column": "name", "type": "text", "nullable": false},
      {"column": "email", "type": "text", "nullable": true},
      {"column": "created_at", "type": "timestamp", "nullable": false}
    ],
    "orders": [
      {"column": "id", "type": "integer", "nullable": false},
      {"column": "user_id", "type": "integer", "nullable": false},
      {"column": "total", "type": "numeric", "nullable": false}
    ]
  }
}
```

**Response Fields:**
- `tables` (object): Dictionary of table names → column definitions
  - `column` (string): Column name
  - `type` (string): Data type (e.g., `integer`, `text`, `numeric`, `timestamp`)
  - `nullable` (boolean, optional): Whether column allows NULL values

**Status Codes:**
- `200 OK`: Schema retrieved successfully (may be cached)
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Datasource not found or connection string not configured
- `500 Internal Server Error`: Failed to introspect schema

**Caching:**
- Results cached for 10 minutes in in-process memory
- Cache key: `schema:{datasource_id}`

**Example (cURL):**
```bash
curl -X GET "http://localhost:8000/api/v1/schema?datasource_type=postgres&datasource_id=prod_db" \
  -H "Authorization: Bearer eyJhbGci..."
```

---

### Create Session

```http
POST /session
```

Create a new session for query history tracking.

**Request:**
```json
{
  "type": "postgres",
  "datasource_id": "prod_db"
}
```

**Response:**
```json
{
  "session_id": "abc-123-def-456",
  "datasource_id": "prod_db",
  "created_at": "2024-04-24T10:30:00Z",
  "expires_at": "2024-04-25T10:30:00Z"
}
```

**Status Codes:**
- `201 Created`: Session created successfully
- `400 Bad Request`: Invalid datasource configuration
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Datasource not found

---

### Get Session History

```http
GET /session/{session_id}
```

Retrieve session history and message timeline.

**Path Parameters:**
- `session_id` (string, required): The session ID

**Response:**
```json
{
  "session_id": "abc-123-def-456",
  "datasource_id": "prod_db",
  "messages": [
    {
      "role": "user",
      "content": "How many active users?",
      "timestamp": "2024-04-24T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "There are 42,156 active users as of today.",
      "timestamp": "2024-04-24T10:30:05Z"
    }
  ],
  "created_at": "2024-04-24T10:30:00Z",
  "updated_at": "2024-04-24T10:35:00Z"
}
```

**Status Codes:**
- `200 OK`: Session retrieved successfully
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Session not found or expired

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Descriptive error message"
}
```

### Common Errors

| Status | Error | Cause |
|---|---|---|
| 400 | Invalid datasource type | `type` must be one of: `postgres`, `mysql`, `mongodb` |
| 401 | Invalid token | Token is expired or invalid |
| 404 | No connection string for datasource | Environment variable `DB_URL_{ID}` not set |
| 429 | Rate limit exceeded | More than 20 requests/minute |
| 500 | Failed to connect to database | Network error or invalid credentials |
| 500 | Query execution failed | SQL syntax error or data access issue |

### Retry Behavior

The agent automatically retries queries up to 3 times if they fail. If all retries fail, it returns an error in the response with `results` as an empty array.

---

## Request/Response Examples

### PostgreSQL Query

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Top 5 customers by total spent",
    "datasource": {"type": "postgres", "datasource_id": "prod_db"},
    "session_id": "session-1"
  }'
```

**Response:**
```json
{
  "answer": "The top 5 customers by total spending are...",
  "query_generated": "SELECT customer_id, SUM(amount) as total FROM orders GROUP BY customer_id ORDER BY total DESC LIMIT 5",
  "results": [
    {"customer_id": 1001, "total": 15234.50},
    {"customer_id": 1002, "total": 12456.75}
  ],
  "viz_type": "bar",
  "session_id": "session-1"
}
```

### MongoDB Aggregation

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Average order amount by product category",
    "datasource": {"type": "mongodb", "datasource_id": "analytics_db"},
    "session_id": "session-2"
  }'
```

**Response:**
```json
{
  "answer": "Average order amounts by category...",
  "query_generated": "[{\"$group\": {\"_id\": \"$category\", \"avg_amount\": {\"$avg\": \"$amount\"}}}]",
  "results": [
    {"_id": "Electronics", "avg_amount": 250.75},
    {"_id": "Books", "avg_amount": 45.30}
  ],
  "viz_type": "bar",
  "session_id": "session-2"
}
```

---

## Rate Limiting

The API implements per-user rate limiting:

- **Limit**: 20 requests per minute
- **Header**: `X-RateLimit-Remaining` shows remaining requests
- **Exceeded**: Returns `429 Too Many Requests`

Headers in response:
```
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 15
X-RateLimit-Reset: 1619251234
```

---

## Authentication Flow

1. **Create token** (via admin endpoint - not documented here yet):
   ```
   POST /auth/token
   {"user_id": "user123"}
   ```
   Returns: `{"token": "eyJhbGc..."}`

2. **Use token** in all requests:
   ```
   Authorization: Bearer eyJhbGc...
   ```

3. **Token expires** after 24 hours; use refresh endpoint:
   ```
   POST /auth/refresh
   {"token": "eyJhbGc..."}
   ```

---

## WebSocket Support (Future)

Currently, all endpoints are HTTP. WebSocket support for streaming results is planned for v0.2.0.

```javascript
// Example (not yet implemented):
const ws = new WebSocket('ws://localhost:8000/api/v1/query/stream');
ws.send(JSON.stringify({message, datasource, session_id}));
ws.onmessage = (event) => {
  const {answer, results, viz_type} = JSON.parse(event.data);
  // Stream results as they arrive
};
```
