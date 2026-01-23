"""Admin API endpoints for question groups."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import CurrentApiKey
from src.core.database import get_session
from src.repositories.question_group import QuestionGroupRepository
from src.repositories.questionnaire_type import QuestionnaireTypeRepository
from src.schemas.common import PaginatedResponse
from src.schemas.question_group import (
    QuestionGroupCreate,
    QuestionGroupResponse,
    QuestionGroupUpdate,
)

router = APIRouter(prefix="/groups", tags=["question-groups"])


@router.post(
    "",
    response_model=QuestionGroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create question group",
)
async def create_group(
    data: QuestionGroupCreate,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QuestionGroupResponse:
    """Create a new question group within a questionnaire type."""
    # Verify type exists
    type_repo = QuestionnaireTypeRepository(session)
    qtype = await type_repo.get_by_id(data.type_id)
    if qtype is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire type not found",
        )

    group_repo = QuestionGroupRepository(session)
    group = await group_repo.create(data)
    return QuestionGroupResponse.model_validate(group)


@router.get(
    "",
    response_model=PaginatedResponse[QuestionGroupResponse],
    summary="List question groups",
)
async def list_groups(
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
    type_id: UUID = Query(..., description="Filter by questionnaire type ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: bool | None = Query(None, description="Filter by active status"),
) -> PaginatedResponse[QuestionGroupResponse]:
    """List question groups for a questionnaire type."""
    repo = QuestionGroupRepository(session)
    offset = (page - 1) * page_size

    groups = await repo.get_by_type_id(
        type_id, is_active=is_active, offset=offset, limit=page_size
    )
    total = await repo.count(type_id=type_id, is_active=is_active)

    return PaginatedResponse.create(
        items=[QuestionGroupResponse.model_validate(g) for g in groups],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{group_id}",
    response_model=QuestionGroupResponse,
    summary="Get question group",
)
async def get_group(
    group_id: UUID,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QuestionGroupResponse:
    """Get a question group by ID."""
    repo = QuestionGroupRepository(session)
    group = await repo.get_by_id(group_id)

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question group not found",
        )

    return QuestionGroupResponse.model_validate(group)


@router.patch(
    "/{group_id}",
    response_model=QuestionGroupResponse,
    summary="Update question group",
)
async def update_group(
    group_id: UUID,
    data: QuestionGroupUpdate,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QuestionGroupResponse:
    """Update a question group."""
    repo = QuestionGroupRepository(session)
    group = await repo.get_by_id(group_id)

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question group not found",
        )

    updated = await repo.update(group, data)
    return QuestionGroupResponse.model_validate(updated)


@router.delete(
    "/{group_id}",
    response_model=QuestionGroupResponse,
    summary="Deactivate question group",
)
async def deactivate_group(
    group_id: UUID,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QuestionGroupResponse:
    """Deactivate a question group (soft delete).

    Deactivated groups are excluded from new assessment snapshots
    but remain in existing assessments.
    """
    repo = QuestionGroupRepository(session)
    group = await repo.get_by_id(group_id)

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question group not found",
        )

    # Soft delete by setting is_active to False
    updated = await repo.update(group, QuestionGroupUpdate(is_active=False))
    return QuestionGroupResponse.model_validate(updated)
