# BI Bot — AI-Powered Business Intelligence Platform

A full-stack application that transforms natural language into database queries across PostgreSQL, MySQL, MongoDB, and more — with a PartyRock-style no-code UI.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Google Generative AI API key

### Setup

1. **Clone and configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Google API key and database URLs
   ```

2. **Backend setup:**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Frontend setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **With Docker Compose (recommended for production):**
   ```bash
   docker-compose up --build
   ```

The API will be available at `http://localhost:8000` and the frontend at `http://localhost`.

## Architecture

### Backend (Python/FastAPI)
- **Agent**: LLM orchestration with function calling and self-correction retry loops
- **Connectors**: Unified interface for PostgreSQL, MySQL, MongoDB, and more
- **Services**: Business logic for queries, schemas, sessions, and authentication
- **Security**: SQL sanitization, JWT auth, RBAC, and rate limiting

### Frontend (React/TypeScript)
- **Components**: Query input, schema explorer, results renderer (table/chart)
- **Hooks**: Reusable logic for queries, schemas, and session management
- **Stores**: Zustand state management for queries, sessions, and datasources
- **API Client**: Axios HTTP client with interceptors

## Project Structure

```
backend/
  app/
    agent/          # LLM orchestration
    api/            # FastAPI routes & middleware
    connectors/     # Datasource adapters
    models/         # Pydantic request/response schemas
    services/       # Business logic
    security/       # Auth, RBAC, sanitization
    config.py       # Settings via pydantic-settings
    main.py         # FastAPI app entry point

frontend/
  src/
    components/     # React UI components
    hooks/          # Custom React hooks
    store/          # Zustand state stores
    api/            # HTTP client & API methods
    types/          # TypeScript interfaces

docker/
  nginx.conf        # Reverse proxy config

docs/
  architecture.md   # System design
  connector-guide.md # Adding new datasources
  api-reference.md  # API documentation
```

## Implementation Status

- [x] **Phase 1**: Backend Foundation (config, models, routes, middleware)
- [ ] **Phase 2**: Agent & Tools (LLM orchestration, tool definitions, retry logic)
- [ ] **Phase 3**: Connectors (PostgreSQL, MySQL, MongoDB implementations)
- [ ] **Phase 4**: Frontend (React components, hooks, stores)
- [ ] **Phase 5**: Security & Hardening (SQL sanitization, auth, rate limiting)
- [ ] **Phase 6**: DevOps & Deployment (Docker, Docker Compose, CI/CD)

## Key Features (Roadmap)

- ✨ Natural language to SQL/aggregation pipeline translation
- 🔄 Self-correcting agent with up to 3 retry attempts on query failures
- 📊 Automatic visualization recommendation (table, bar, line, pie charts)
- 🔐 JWT authentication and role-based access control
- 💾 In-process session management with history
- 🛡️ SQL injection protection and query sanitization
- 📈 Schema introspection caching for performance
- 🚀 Connection pooling for hosted databases
- 🐳 Full Docker containerization for easy deployment

## Environment Variables

See `.env.example` for all required variables:
- `GOOGLE_API_KEY`: Your Google Generative AI API key
- `SECRET_KEY`: Random secret for JWT signing
- `DB_URL_*`: Datasource connection strings (mapped by datasource_id)

## Security

- Connection strings are server-side only — frontend never sees raw credentials
- All SQL queries validated through an allowlist-based sanitizer
- SSL/TLS enforced for all hosted database connections
- Rate limiting on query endpoints (20 requests/minute per user)
- JWT tokens with 24-hour expiration

## Contributing

1. Create a feature branch
2. Make changes following the phase roadmap
3. Write tests in `backend/tests/`
4. Submit a pull request

## License

MIT
