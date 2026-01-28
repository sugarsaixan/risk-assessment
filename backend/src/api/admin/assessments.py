"""Admin API endpoints for assessments."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import CurrentApiKey
from src.core.database import get_session
from src.models.enums import AssessmentStatus
from src.repositories.respondent import RespondentRepository
from src.schemas.assessment import (
    AssessmentCreate,
    AssessmentCreated,
    AssessmentResponse,
)
from src.schemas.common import PaginatedResponse
from src.schemas.results import AssessmentResultsResponse
from src.services.assessment import AssessmentService
from src.services.results import ResultsService

router = APIRouter(prefix="/assessments", tags=["assessments"])


def _assessment_to_response(assessment) -> AssessmentResponse:
    """Convert an assessment (with loaded respondent) to response schema."""
    respondent_odoo_id = None
    if assessment.respondent is not None:
        respondent_odoo_id = assessment.respondent.odoo_id

    return AssessmentResponse(
        id=assessment.id,
        respondent_id=assessment.respondent_id,
        respondent_odoo_id=respondent_odoo_id,
        employee_id=assessment.employee_id,
        employee_name=assessment.employee_name,
        selected_type_ids=assessment.selected_type_ids,
        expires_at=assessment.expires_at,
        status=assessment.status,
        completed_at=assessment.completed_at,
        created_at=assessment.created_at,
    )


@router.post(
    "",
    response_model=AssessmentCreated,
    status_code=status.HTTP_201_CREATED,
    summary="Create assessment with inline respondent and optional employee data",
)
async def create_assessment(
    data: AssessmentCreate,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AssessmentCreated:
    """Create a new assessment with inline respondent data from Odoo.

    Accepts respondent data (odoo_id, name, kind, registration_no) and
    optional employee data (employee_id, employee_name). The system
    creates or matches the respondent, stores employee info on the
    assessment, and returns the assessment link.
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
    odoo_id: str | None = Query(None, description="Filter by respondent Odoo ID"),
    employee_id: str | None = Query(None, description="Filter by Odoo employee ID"),
    status_filter: AssessmentStatus | None = Query(
        None, alias="status", description="Filter by status"
    ),
) -> PaginatedResponse[AssessmentResponse]:
    """List all assessments with pagination and filtering."""
    service = AssessmentService(session)

    # Resolve odoo_id to respondent_id
    resolved_respondent_id = respondent_id
    if odoo_id is not None:
        repo = RespondentRepository(session)
        respondent = await repo.get_by_odoo_id(odoo_id)
        if respondent is None:
            # No respondent with this odoo_id — return empty results
            return PaginatedResponse.create(
                items=[],
                total=0,
                page=page,
                page_size=page_size,
            )
        resolved_respondent_id = respondent.id

    assessments, total = await service.list_assessments(
        respondent_id=resolved_respondent_id,
        status=status_filter,
        employee_id=employee_id,
        offset=(page - 1) * page_size,
        limit=page_size,
    )

    return PaginatedResponse.create(
        items=[_assessment_to_response(a) for a in assessments],
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

    return _assessment_to_response(assessment)


@router.get(
    "/{assessment_id}/results",
    response_model=AssessmentResultsResponse,
    summary="Get assessment results",
)
async def get_assessment_results(
    assessment_id: UUID,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
    breakdown: bool = Query(False, description="Include individual answer breakdown"),
) -> AssessmentResultsResponse:
    """Get assessment results with scores and optional answer breakdown.

    Returns per-type scores, overall score, and optionally detailed answer breakdown
    including comments and attachment counts.
    """
    service = ResultsService(session)
    results = await service.get_results(assessment_id, include_breakdown=breakdown)

    if results is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    return results
