"""Public API router configuration."""

from fastapi import APIRouter

from src.api.public import assessment

# Create main public router
public_router = APIRouter(tags=["public"])

# Include sub-routers
public_router.include_router(assessment.router)

__all__ = ["public_router"]
