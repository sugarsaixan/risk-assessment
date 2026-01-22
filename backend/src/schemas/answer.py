"""Pydantic schemas for Answer."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import OptionType


class AnswerInput(BaseModel):
    """Schema for submitting an answer."""

    question_id: UUID = Field(..., description="Question ID from the form")
    selected_option: OptionType = Field(..., description="YES or NO")
    comment: str | None = Field(None, max_length=2000, description="Optional comment")
    attachment_ids: list[UUID] = Field(
        default_factory=list,
        description="IDs of uploaded attachments",
    )


class AnswerResponse(BaseModel):
    """Schema for answer response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    assessment_id: UUID
    question_id: UUID
    selected_option: OptionType
    comment: str | None
    score_awarded: int
    created_at: datetime
