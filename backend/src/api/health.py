"""Health check endpoints for the application."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session

router = APIRouter(tags=["root"])


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Check timestamp")
    database: str = Field(..., description="Database connection status")
    version: str = Field(default="1.0.0", description="API version")


class ReadinessResponse(BaseModel):
    """Readiness check response schema."""

    ready: bool = Field(..., description="Whether service is ready")
    checks: dict[str, bool] = Field(..., description="Individual check results")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Basic health check endpoint for load balancers and monitoring.",
)
async def health_check(
    session: AsyncSession = Depends(get_session),
) -> HealthResponse:
    """Check application health including database connectivity."""
    # Check database connection
    db_status = "healthy"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return HealthResponse(
        status="ok" if db_status == "healthy" else "degraded",
        timestamp=datetime.now(timezone.utc),
        database=db_status,
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness check",
    description="Kubernetes-style readiness probe to check if service can accept traffic.",
)
async def readiness_check(
    session: AsyncSession = Depends(get_session),
) -> ReadinessResponse:
    """Check if the application is ready to serve requests."""
    checks: dict[str, bool] = {}

    # Check database
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        checks["database"] = False

    # All checks must pass for readiness
    ready = all(checks.values())

    return ReadinessResponse(ready=ready, checks=checks)


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    description="Kubernetes-style liveness probe to check if service is running.",
)
async def liveness_check() -> dict[str, str]:
    """Simple liveness check - returns 200 if application is running."""
    return {"status": "alive"}
