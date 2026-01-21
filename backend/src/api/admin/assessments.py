"""Admin API endpoints for assessments."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import CurrentApiKey
from src.core.database import get_session
from src.models.enums import AssessmentStatus
from src.schemas.assessment import (
    AssessmentCreate,
    AssessmentCreated,
    AssessmentResponse,
)
from src.schemas.common import PaginatedResponse
from src.services.assessment import AssessmentService

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post(
    "",
    response_model=AssessmentCreated,
    status_code=status.HTTP_201_CREATED,
    summary="Create assessment",
)
async def create_assessment(
    data: AssessmentCreate,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AssessmentCreated:
    """Create a new assessment with a one-time access link.

    This generates a unique token and creates a snapshot of the selected
    questionnaire types and their questions at the time of creation.

    Returns the assessment ID and the public URL to share with the respondent.
    """
    service = AssessmentService(session)

    try:
        result = await service.create_assessment(data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=PaginatedResponse[AssessmentResponse],
    summary="List assessments",
)
async def list_assessments(
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    respondent_id: UUID | None = Query(None, description="Filter by respondent"),
    status_filter: AssessmentStatus | None = Query(
        None, alias="status", description="Filter by status"
    ),
) -> PaginatedResponse[AssessmentResponse]:
    """List all assessments with pagination and filtering."""
    service = AssessmentService(session)

    assessments, total = await service.list_assessments(
        respondent_id=respondent_id,
        status=status_filter,
        offset=(page - 1) * page_size,
        limit=page_size,
    )

    return PaginatedResponse.create(
        items=[AssessmentResponse.model_validate(a) for a in assessments],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse,
    summary="Get assessment",
)
async def get_assessment(
    assessment_id: UUID,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AssessmentResponse:
    """Get an assessment by ID."""
    service = AssessmentService(session)
    assessment = await service.get_by_id(assessment_id)

    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    return AssessmentResponse.model_validate(assessment)
