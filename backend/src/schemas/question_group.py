"""Pydantic schemas for QuestionGroup."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class QuestionGroupCreate(BaseModel):
    """Schema for creating a question group."""

    type_id: UUID = Field(..., description="Parent questionnaire type ID")
    name: str = Field(..., min_length=1, max_length=200, description="Group name (Mongolian)")
    display_order: int = Field(
        default=0,
        ge=0,
        description="Display order within the type",
    )
    weight: Decimal = Field(
        default=Decimal("1.0"),
        gt=0,
        le=Decimal("100.0"),
        description="Weight for type score calculation",
    )


class QuestionGroupUpdate(BaseModel):
    """Schema for updating a question group."""

    name: str | None = Field(None, min_length=1, max_length=200)
    display_order: int | None = Field(None, ge=0)
    weight: Decimal | None = Field(None, gt=0, le=Decimal("100.0"))
    is_active: bool | None = None


class QuestionGroupResponse(BaseModel):
    """Schema for question group response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type_id: UUID
    name: str
    display_order: int
    weight: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class QuestionGroupList(BaseModel):
    """Schema for listing question groups (minimal fields)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type_id: UUID
    name: str
    display_order: int
    is_active: bool


class QuestionGroupWithQuestionCount(QuestionGroupResponse):
    """Schema for question group with question count."""

    question_count: int = Field(default=0, description="Number of questions in this group")
