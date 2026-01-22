"""Public API endpoints for assessment access and submission."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_session
from src.core.rate_limit import PUBLIC_RATE_LIMIT
from src.schemas.attachment import AttachmentUpload
from src.schemas.public import (
    AssessmentErrorResponse,
    AssessmentFormResponse,
    SubmitRequest,
    SubmitResponse,
)
from src.services.assessment import AssessmentService
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

    Returns the questionnaire types and questions from the snapshot.
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

    # Get respondent name
    respondent = assessment.respondent
    await session.refresh(assessment, ["respondent"])

    return AssessmentFormResponse(
        id=str(assessment.id),
        respondent_name=assessment.respondent.name,
        expires_at=assessment.expires_at.isoformat(),
        types=assessment.questions_snapshot.get("types", []),
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
    """Submit assessment answers and get results.

    Validates all answers, calculates scores, and returns results.
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

    # Validate answers
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

    # Process submission
    result = await submission_service.process_submission(assessment, data.answers)
    return result
