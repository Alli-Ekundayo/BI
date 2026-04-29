"""FastAPI application entry point."""
from fastapi import FastAPI
from app.api import router, add_middleware
from app.config import settings

# Create the FastAPI app
app = FastAPI(
    title="BI Bot API",
    description="AI-powered business intelligence bot for natural language database queries",
    version="0.1.0",
)

# Add middleware (CORS, rate limiting, etc.)
add_middleware(app)

# Include API routes
app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
    )
