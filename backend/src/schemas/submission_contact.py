"""Pydantic schemas for SubmissionContact."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SubmissionContactInput(BaseModel):
    """Schema for submission contact input (embedded in submit request)."""

    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Овог (Family name)",
    )
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Нэр (Given name)",
    )
    email: EmailStr = Field(
        ...,
        description="Email address",
    )
    phone: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Phone number",
    )
    position: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Албан тушаал (Job position)",
    )


class SubmissionContactResponse(BaseModel):
    """Schema for submission contact response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    assessment_id: UUID
    last_name: str
    first_name: str
    email: str
    phone: str
    position: str
    created_at: datetime
    updated_at: datetime
