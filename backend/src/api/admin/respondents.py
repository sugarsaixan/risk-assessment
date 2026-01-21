"""Admin API endpoints for respondents."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import CurrentApiKey
from src.core.database import get_session
from src.models.enums import RespondentKind
from src.repositories.respondent import RespondentRepository
from src.schemas.common import PaginatedResponse
from src.schemas.respondent import (
    RespondentCreate,
    RespondentResponse,
    RespondentUpdate,
)

router = APIRouter(prefix="/respondents", tags=["respondents"])


@router.post(
    "",
    response_model=RespondentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create respondent",
)
async def create_respondent(
    data: RespondentCreate,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RespondentResponse:
    """Create a new respondent (organization or person)."""
    repo = RespondentRepository(session)
    respondent = await repo.create(data)
    return RespondentResponse.model_validate(respondent)


@router.get(
    "",
    response_model=PaginatedResponse[RespondentResponse],
    summary="List respondents",
)
async def list_respondents(
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    kind: RespondentKind | None = Query(None, description="Filter by respondent type"),
    search: str | None = Query(None, description="Search by name"),
) -> PaginatedResponse[RespondentResponse]:
    """List all respondents with pagination and filtering."""
    repo = RespondentRepository(session)
    offset = (page - 1) * page_size

    respondents = await repo.get_all(
        kind=kind, name_search=search, offset=offset, limit=page_size
    )
    total = await repo.count(kind=kind, name_search=search)

    return PaginatedResponse.create(
        items=[RespondentResponse.model_validate(r) for r in respondents],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{respondent_id}",
    response_model=RespondentResponse,
    summary="Get respondent",
)
async def get_respondent(
    respondent_id: UUID,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RespondentResponse:
    """Get a respondent by ID."""
    repo = RespondentRepository(session)
    respondent = await repo.get_by_id(respondent_id)

    if respondent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Respondent not found",
        )

    return RespondentResponse.model_validate(respondent)


@router.patch(
    "/{respondent_id}",
    response_model=RespondentResponse,
    summary="Update respondent",
)
async def update_respondent(
    respondent_id: UUID,
    data: RespondentUpdate,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RespondentResponse:
    """Update a respondent."""
    repo = RespondentRepository(session)
    respondent = await repo.get_by_id(respondent_id)

    if respondent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Respondent not found",
        )

    updated = await repo.update(respondent, data)
    return RespondentResponse.model_validate(updated)
