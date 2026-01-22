"""Pydantic schemas for Question."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class QuestionCreate(BaseModel):
    """Schema for creating a question."""

    type_id: UUID = Field(..., description="Parent questionnaire type ID")
    text: str = Field(..., min_length=1, max_length=2000, description="Question text (Mongolian)")
    display_order: int = Field(default=0, ge=0, description="Order within type for display")
    weight: Decimal = Field(
        default=Decimal("1.0"),
        gt=0,
        le=Decimal("100.0"),
        description="Question weight (future use)",
    )
    is_critical: bool = Field(default=False, description="Critical flag (future use)")


class QuestionUpdate(BaseModel):
    """Schema for updating a question."""

    text: str | None = Field(None, min_length=1, max_length=2000)
    display_order: int | None = Field(None, ge=0)
    weight: Decimal | None = Field(None, gt=0, le=Decimal("100.0"))
    is_critical: bool | None = None
    is_active: bool | None = None


class QuestionResponse(BaseModel):
    """Schema for question response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type_id: UUID
    text: str
    display_order: int
    weight: Decimal
    is_critical: bool
    is_active: bool


class QuestionWithOptionsResponse(BaseModel):
    """Schema for question response including options."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type_id: UUID
    text: str
    display_order: int
    weight: Decimal
    is_critical: bool
    is_active: bool
    options: list["QuestionOptionResponse"] = []


# Import at end to avoid circular imports
from src.schemas.question_option import QuestionOptionResponse  # noqa: E402

QuestionWithOptionsResponse.model_rebuild()
