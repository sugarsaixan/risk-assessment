"""Admin API endpoints for questionnaire types."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import CurrentApiKey
from src.core.database import get_session
from src.repositories.questionnaire_type import QuestionnaireTypeRepository
from src.schemas.common import PaginatedResponse
from src.schemas.questionnaire_type import (
    QuestionnaireTypeCreate,
    QuestionnaireTypeResponse,
    QuestionnaireTypeUpdate,
)

router = APIRouter(prefix="/types", tags=["questionnaire-types"])


@router.post(
    "",
    response_model=QuestionnaireTypeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create questionnaire type",
)
async def create_type(
    data: QuestionnaireTypeCreate,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QuestionnaireTypeResponse:
    """Create a new questionnaire type."""
    # Validate threshold order
    if data.threshold_high <= data.threshold_medium:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="threshold_high must be greater than threshold_medium",
        )

    repo = QuestionnaireTypeRepository(session)
    qtype = await repo.create(data)
    return QuestionnaireTypeResponse.model_validate(qtype)


@router.get(
    "",
    response_model=PaginatedResponse[QuestionnaireTypeResponse],
    summary="List questionnaire types",
)
async def list_types(
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: bool | None = Query(None, description="Filter by active status"),
) -> PaginatedResponse[QuestionnaireTypeResponse]:
    """List all questionnaire types with pagination."""
    repo = QuestionnaireTypeRepository(session)
    offset = (page - 1) * page_size

    types = await repo.get_all(is_active=is_active, offset=offset, limit=page_size)
    total = await repo.count(is_active=is_active)

    return PaginatedResponse.create(
        items=[QuestionnaireTypeResponse.model_validate(t) for t in types],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{type_id}",
    response_model=QuestionnaireTypeResponse,
    summary="Get questionnaire type",
)
async def get_type(
    type_id: UUID,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QuestionnaireTypeResponse:
    """Get a questionnaire type by ID."""
    repo = QuestionnaireTypeRepository(session)
    qtype = await repo.get_by_id(type_id)

    if qtype is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire type not found",
        )

    return QuestionnaireTypeResponse.model_validate(qtype)


@router.patch(
    "/{type_id}",
    response_model=QuestionnaireTypeResponse,
    summary="Update questionnaire type",
)
async def update_type(
    type_id: UUID,
    data: QuestionnaireTypeUpdate,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QuestionnaireTypeResponse:
    """Update a questionnaire type."""
    repo = QuestionnaireTypeRepository(session)
    qtype = await repo.get_by_id(type_id)

    if qtype is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire type not found",
        )

    # Validate threshold order if both are being updated
    new_high = data.threshold_high if data.threshold_high is not None else qtype.threshold_high
    new_medium = (
        data.threshold_medium if data.threshold_medium is not None else qtype.threshold_medium
    )
    if new_high <= new_medium:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="threshold_high must be greater than threshold_medium",
        )

    updated = await repo.update(qtype, data)
    return QuestionnaireTypeResponse.model_validate(updated)
