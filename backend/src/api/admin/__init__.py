"""Admin API router configuration."""

from fastapi import APIRouter

from src.api.admin import assessments, groups, questions, respondents, types

# Create main admin router
admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Include sub-routers
admin_router.include_router(types.router)
admin_router.include_router(groups.router)
admin_router.include_router(questions.router)
admin_router.include_router(respondents.router)
admin_router.include_router(assessments.router)

__all__ = ["admin_router"]
