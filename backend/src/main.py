"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.admin import admin_router
from src.api.health import router as health_router
from src.api.public import public_router
from src.core.config import settings
from src.core.database import close_db, init_db
from src.core.logging import RequestLoggingMiddleware, setup_logging
from src.core.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    setup_logging()
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## Risk Assessment Survey API

API for managing risk assessment questionnaires, respondents, and survey submissions.

### Features

- **Admin API**: Manage questionnaire types, questions, options, respondents, and assessments
- **Public API**: Respondent-facing endpoints for completing assessments

### Authentication

Admin endpoints require API key authentication via the `X-API-Key` header.
Public endpoints are rate-limited and accessed via one-time tokens.
    """,
    debug=settings.debug,
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "root",
            "description": "Root and health check endpoints",
        },
        {
            "name": "types",
            "description": "Questionnaire type management (Admin)",
        },
        {
            "name": "questions",
            "description": "Question and option management (Admin)",
        },
        {
            "name": "respondents",
            "description": "Respondent management (Admin)",
        },
        {
            "name": "assessments",
            "description": "Assessment link creation and results (Admin)",
        },
        {
            "name": "public",
            "description": "Public assessment submission endpoints",
        },
    ],
    license_info={
        "name": "Proprietary",
    },
    contact={
        "name": "Risk Assessment Support",
    },
)

# Request logging middleware (must be added first to wrap all other middleware)
app.add_middleware(RequestLoggingMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.public_url,
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    if settings.debug:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc), "type": type(exc).__name__},
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Configure rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register routers
app.include_router(health_router)
app.include_router(admin_router)
app.include_router(public_router)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint returning API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "ok",
    }
