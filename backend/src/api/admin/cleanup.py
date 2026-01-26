"""Admin API endpoints for cleanup operations."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import CurrentApiKey
from src.core.database import get_session
from src.services.cleanup import CleanupService

router = APIRouter(prefix="/cleanup", tags=["cleanup"])


@router.delete(
    "/drafts",
    summary="Cleanup orphaned drafts",
    response_model=None,
)
async def cleanup_drafts(
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
    older_than_days: int = Query(default=30, ge=0, description="Only cleanup drafts for assessments expired more than N days ago"),
    include_images: bool = Query(default=False, description="Also delete orphaned images from storage"),
    dry_run: bool = Query(default=False, description="Preview what would be deleted without actually deleting"),
) -> dict:
    """Delete draft records for expired assessments.

    Optionally also cleans up orphaned image attachments.
    This is an admin-only batch operation.
    """
    service = CleanupService(session)
    result = await service.cleanup_drafts(
        older_than_days=older_than_days,
        include_images=include_images,
        dry_run=dry_run,
    )
    return asdict(result)


@router.delete(
    "/images",
    summary="Cleanup orphaned images",
    response_model=None,
)
async def cleanup_images(
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
    older_than_days: int = Query(default=30, ge=0, description="Only cleanup images uploaded more than N days ago"),
    dry_run: bool = Query(default=False, description="Preview what would be deleted without actually deleting"),
) -> dict:
    """Delete images from storage that are not referenced by any answer.

    This can happen when images are uploaded but assessment is never submitted.
    """
    service = CleanupService(session)
    result = await service.cleanup_images(
        older_than_days=older_than_days,
        dry_run=dry_run,
    )
    return asdict(result)
