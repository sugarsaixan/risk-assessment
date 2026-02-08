"""Public API endpoints for assessment access and submission."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import JSONResponse, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.rate_limit import PUBLIC_RATE_LIMIT
from src.schemas.attachment import AttachmentUpload
from src.schemas.draft import DraftResponse, DraftSaveRequest, DraftSaveResponse
from src.schemas.public import (
    AssessmentErrorResponse,
    AssessmentFormResponse,
    SubmitRequest,
    SubmitResponse,
)
from src.services.assessment import AssessmentService
from src.services.draft import DraftService
from src.services.results import ResultsService
from src.services.submission import SubmissionService
from src.services.upload import UploadService

router = APIRouter(prefix="/a", tags=["public-assessment"])

# Create limiter for rate limiting
limiter = Limiter(key_func=get_remote_address)

# Mongolian error messages
ERROR_MESSAGES = {
    "not_found": "Үнэлгээ олдсонгүй.",
    "expired": "Линкний хугацаа дууссан байна.",
    "already_completed": "Энэ линк аль хэдийн ашиглагдсан байна.",
}


@router.get(
    "/{token}",
    response_model=AssessmentFormResponse,
    responses={
        404: {"model": AssessmentErrorResponse, "description": "Assessment not found"},
        410: {"model": AssessmentErrorResponse, "description": "Assessment expired or completed"},
    },
    summary="Get assessment form",
)
@limiter.limit(PUBLIC_RATE_LIMIT)
async def get_assessment_form(
    request: Request,
    token: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AssessmentFormResponse | JSONResponse:
    """Get assessment form data for a respondent.

    Returns the questionnaire types with groups and questions from the snapshot.
    The hierarchical structure is: Type → Group → Question
    """
    service = AssessmentService(session)
    assessment, error = await service.get_assessment_status(token)

    if error == "not_found":
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=AssessmentErrorResponse(
                error="not_found",
                message=ERROR_MESSAGES["not_found"],
            ).model_dump(),
        )

    if error == "expired":
        return JSONResponse(
            status_code=status.HTTP_410_GONE,
            content=AssessmentErrorResponse(
                error="expired",
                message=ERROR_MESSAGES["expired"],
            ).model_dump(),
        )

    if error == "already_completed":
        return JSONResponse(
            status_code=status.HTTP_410_GONE,
            content=AssessmentErrorResponse(
                error="already_completed",
                message=ERROR_MESSAGES["already_completed"],
            ).model_dump(),
        )

    # Load respondent in async-safe way before access.
    await session.refresh(assessment, ["respondent"])

    # Load draft if exists
    draft_service = DraftService(session)
    draft = await draft_service.load_draft(assessment.id)

    # Return hierarchical structure: types contain groups contain questions
    return AssessmentFormResponse(
        id=str(assessment.id),
        respondent_name=assessment.respondent.name,
        expires_at=assessment.expires_at.isoformat(),
        types=assessment.questions_snapshot.get("types", []),
        draft=draft,
    )


@router.get(
    "/{token}/draft",
    response_model=DraftResponse,
    responses={
        204: {"description": "No draft exists"},
        404: {"model": AssessmentErrorResponse, "description": "Assessment not found"},
        410: {"model": AssessmentErrorResponse, "description": "Assessment expired or completed"},
    },
    summary="Load saved draft",
)
@limiter.limit(PUBLIC_RATE_LIMIT)
async def get_draft(
    request: Request,
    token: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DraftResponse | Response | JSONResponse:
    """Load saved draft answers for an assessment.

    Returns 204 if no draft exists.
    Only works for PENDING, non-expired assessments.
    """
    service = AssessmentService(session)
    assessment, error = await service.get_assessment_status(token)

    if error == "not_found":
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=AssessmentErrorResponse(
                error="not_found",
                message=ERROR_MESSAGES["not_found"],
            ).model_dump(),
        )

    if error == "expired":
        return JSONResponse(
            status_code=status.HTTP_410_GONE,
            content=AssessmentErrorResponse(
                error="expired",
                message=ERROR_MESSAGES["expired"],
            ).model_dump(),
        )

    if error == "already_completed":
        return JSONResponse(
            status_code=status.HTTP_410_GONE,
            content=AssessmentErrorResponse(
                error="already_completed",
                message=ERROR_MESSAGES["already_completed"],
            ).model_dump(),
        )

    # Load draft
    draft_service = DraftService(session)
    draft = await draft_service.load_draft(assessment.id)

    if draft is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return draft


@router.put(
    "/{token}/draft",
    response_model=DraftSaveResponse,
    responses={
        400: {"model": AssessmentErrorResponse, "description": "Invalid draft data"},
        404: {"model": AssessmentErrorResponse, "description": "Assessment not found"},
        410: {"model": AssessmentErrorResponse, "description": "Assessment expired or completed"},
    },
    summary="Save draft",
)
@limiter.limit(PUBLIC_RATE_LIMIT)
async def save_draft(
    request: Request,
    token: str,
    data: DraftSaveRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DraftSaveResponse | JSONResponse:
    """Save or update draft answers for an assessment.

    Uses upsert pattern - creates new draft or updates existing.
    Only works for PENDING, non-expired assessments.
    """
    service = AssessmentService(session)
    assessment, error = await service.get_assessment_status(token)

    if error == "not_found":
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=AssessmentErrorResponse(
                error="not_found",
                message=ERROR_MESSAGES["not_found"],
            ).model_dump(),
        )

    if error == "expired":
        return JSONResponse(
            status_code=status.HTTP_410_GONE,
            content=AssessmentErrorResponse(
                error="expired",
                message=ERROR_MESSAGES["expired"],
            ).model_dump(),
        )

    if error == "already_completed":
        return JSONResponse(
            status_code=status.HTTP_410_GONE,
            content=AssessmentErrorResponse(
                error="already_completed",
                message=ERROR_MESSAGES["already_completed"],
            ).model_dump(),
        )

    # Save draft
    draft_service = DraftService(session)
    try:
        result = await draft_service.save_draft(assessment.id, data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{token}/upload",
    response_model=AttachmentUpload,
    summary="Upload image attachment",
)
@limiter.limit(PUBLIC_RATE_LIMIT)
async def upload_attachment(
    request: Request,
    token: str,
    question_id: UUID = Form(..., description="Question ID this image is for"),
    file: UploadFile = File(..., description="Image file"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
) -> AttachmentUpload:
    """Upload an image attachment for a question.

    The returned attachment ID should be included in the submission.
    """
    # Validate assessment
    assessment_service = AssessmentService(session)
    assessment, error = await assessment_service.get_assessment_status(token)

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.get(error, "Invalid assessment"),
        )

    # Read file content
    content = await file.read()

    # Upload file
    upload_service = UploadService(session)
    try:
        result = await upload_service.upload_image(
            assessment_id=assessment.id,
            question_id=question_id,
            filename=file.filename or "upload",
            content_type=file.content_type or "application/octet-stream",
            content=content,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{token}/results",
    response_model=SubmitResponse,
    responses={
        404: {"model": AssessmentErrorResponse, "description": "Assessment not found"},
        400: {"model": AssessmentErrorResponse, "description": "Assessment not completed"},
    },
    summary="Get assessment results",
)
@limiter.limit(PUBLIC_RATE_LIMIT)
async def get_public_results(
    request: Request,
    token: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    breakdown: bool = Query(False, description="Include individual answer breakdown"),
) -> SubmitResponse | JSONResponse:
    """Get results for a completed assessment by token.

    Only works for COMPLETED assessments. Returns the same format as the submit response.
    """
    # Get assessment by token
    assessment_service = AssessmentService(session)
    assessment = await assessment_service.get_by_token(token)

    if assessment is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=AssessmentErrorResponse(
                error="not_found",
                message=ERROR_MESSAGES["not_found"],
            ).model_dump(),
        )

    # Only allow access to completed assessments
    if assessment.status.value != "COMPLETED":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=AssessmentErrorResponse(
                error="not_completed",
                message="Үнэлгээ дуусаагүй байна.",
            ).model_dump(),
        )

    # Get results using ResultsService
    results_service = ResultsService(session)
    results = await results_service.get_results(assessment.id, include_breakdown=breakdown)

    if results is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=AssessmentErrorResponse(
                error="not_found",
                message=ERROR_MESSAGES["not_found"],
            ).model_dump(),
        )

    # Convert to SubmitResponse format (matching what submit endpoint returns)
    from src.schemas.public import AnswerBreakdownItem, GroupResult, OverallResult, TypeResult

    type_results = [
        TypeResult(
            type_id=str(ts.type_id),
            type_name=ts.type_name,
            raw_score=ts.raw_score,
            max_score=ts.max_score,
            percentage=ts.percentage,
            risk_rating=ts.risk_rating,
            groups=[
                GroupResult(
                    group_id=str(gs.group_id),
                    group_name=gs.group_name,
                    raw_score=gs.raw_score,
                    max_score=gs.max_score,
                    percentage=gs.percentage,
                    risk_rating=gs.risk_rating,
                )
                for gs in ts.groups
            ],
        )
        for ts in results.type_scores
    ]

    overall_result = OverallResult(
        raw_score=results.overall_score.raw_score,
        max_score=results.overall_score.max_score,
        percentage=results.overall_score.percentage,
        risk_rating=results.overall_score.risk_rating,
    )

    answer_breakdown = None
    if results.answer_breakdown:
        answer_breakdown = [
            AnswerBreakdownItem(
                question_id=str(ab.question_id),
                question_text=ab.question_text,
                type_id=str(ab.type_id),
                type_name=ab.type_name,
                selected_option=ab.selected_option,
                comment=ab.comment,
                score_awarded=ab.score_awarded,
                max_score=ab.max_score,
                attachment_count=ab.attachment_count,
            )
            for ab in results.answer_breakdown
        ]

    return SubmitResponse(
        assessment_id=str(results.assessment_id),
        type_results=type_results,
        overall_result=overall_result,
        answer_breakdown=answer_breakdown,
    )


@router.post(
    "/{token}/submit",
    response_model=SubmitResponse,
    responses={
        400: {"description": "Validation error"},
        404: {"model": AssessmentErrorResponse, "description": "Assessment not found"},
        410: {"model": AssessmentErrorResponse, "description": "Assessment expired or completed"},
    },
    summary="Submit assessment",
)
@limiter.limit(PUBLIC_RATE_LIMIT)
async def submit_assessment(
    request: Request,
    token: str,
    data: SubmitRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SubmitResponse | JSONResponse:
    """Submit assessment answers with contact info and get hierarchical results.

    Requires contact information (Овог, Нэр, email, phone, Албан тушаал).
    Validates all answers, calculates hierarchical scores (Group → Type → Overall),
    and returns results with per-group, per-type, and overall scores.
    """
    # Validate assessment
    assessment_service = AssessmentService(session)
    assessment, error = await assessment_service.get_assessment_status(token)

    if error == "not_found":
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=AssessmentErrorResponse(
                error="not_found",
                message=ERROR_MESSAGES["not_found"],
            ).model_dump(),
        )

    if error in ("expired", "already_completed"):
        return JSONResponse(
            status_code=status.HTTP_410_GONE,
            content=AssessmentErrorResponse(
                error=error,
                message=ERROR_MESSAGES[error],
            ).model_dump(),
        )

    # Validate answers against snapshot
    submission_service = SubmissionService(session)
    validation_errors = submission_service.validate_answers(
        assessment.questions_snapshot,
        data.answers,
    )

    if validation_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": validation_errors},
        )

    # Process submission with contact info and calculate hierarchical scores
    result = await submission_service.process_submission(
        assessment,
        data.contact,
        data.answers,
    )

    # Delete draft after successful submission
    draft_service = DraftService(session)
    await draft_service.delete_draft(assessment.id)

    return result
