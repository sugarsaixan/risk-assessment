"""Admin API endpoints for questions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import CurrentApiKey
from src.core.database import get_session
from src.repositories.question import QuestionRepository
from src.repositories.question_group import QuestionGroupRepository
from src.repositories.question_option import QuestionOptionRepository
from src.schemas.common import PaginatedResponse
from src.schemas.question import (
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
    QuestionWithOptionsResponse,
)
from src.schemas.question_option import QuestionOptionResponse, QuestionOptionsSet

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create question",
)
async def create_question(
    data: QuestionCreate,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QuestionResponse:
    """Create a new question for a question group."""
    # Verify group exists
    group_repo = QuestionGroupRepository(session)
    group = await group_repo.get_by_id(data.group_id)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question group not found",
        )

    # Auto-assign display_order if not provided or 0
    question_repo = QuestionRepository(session)
    if data.display_order == 0:
        data.display_order = await question_repo.get_next_display_order(data.group_id)

    question = await question_repo.create(data)
    return QuestionResponse.model_validate(question)


@router.get(
    "",
    response_model=PaginatedResponse[QuestionResponse],
    summary="List questions",
)
async def list_questions(
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
    group_id: UUID = Query(..., description="Filter by question group ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: bool | None = Query(None, description="Filter by active status"),
) -> PaginatedResponse[QuestionResponse]:
    """List questions for a question group."""
    repo = QuestionRepository(session)
    offset = (page - 1) * page_size

    questions = await repo.get_by_group(
        group_id, is_active=is_active, offset=offset, limit=page_size
    )
    total = await repo.count_by_group(group_id, is_active=is_active)

    return PaginatedResponse.create(
        items=[QuestionResponse.model_validate(q) for q in questions],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{question_id}",
    response_model=QuestionWithOptionsResponse,
    summary="Get question with options",
)
async def get_question(
    question_id: UUID,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QuestionWithOptionsResponse:
    """Get a question by ID including its options."""
    repo = QuestionRepository(session)
    question = await repo.get_by_id_with_options(question_id)

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    return QuestionWithOptionsResponse(
        id=question.id,
        group_id=question.group_id,
        text=question.text,
        display_order=question.display_order,
        weight=question.weight,
        is_critical=question.is_critical,
        is_active=question.is_active,
        options=[QuestionOptionResponse.model_validate(o) for o in question.options],
    )


@router.patch(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="Update question",
)
async def update_question(
    question_id: UUID,
    data: QuestionUpdate,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QuestionResponse:
    """Update a question."""
    repo = QuestionRepository(session)
    question = await repo.get_by_id(question_id)

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    updated = await repo.update(question, data)
    return QuestionResponse.model_validate(updated)


@router.put(
    "/{question_id}/options",
    response_model=list[QuestionOptionResponse],
    summary="Set question options",
)
async def set_question_options(
    question_id: UUID,
    options: QuestionOptionsSet,
    _api_key: CurrentApiKey,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[QuestionOptionResponse]:
    """Set YES and NO options for a question.

    This replaces any existing options.
    """
    # Verify question exists
    question_repo = QuestionRepository(session)
    question = await question_repo.get_by_id(question_id)

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    # Set options
    option_repo = QuestionOptionRepository(session)
    created_options = await option_repo.set_options(question_id, options)

    return [QuestionOptionResponse.model_validate(o) for o in created_options]
