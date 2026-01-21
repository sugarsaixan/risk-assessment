"""Pydantic schemas for Assessment."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import AssessmentStatus


class AssessmentCreate(BaseModel):
    """Schema for creating an assessment."""

    respondent_id: UUID = Field(..., description="Respondent being assessed")
    selected_type_ids: list[UUID] = Field(
        ...,
        min_length=1,
        description="QuestionnaireType IDs to include",
    )
    expires_in_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Days until link expires",
    )


class AssessmentCreated(BaseModel):
    """Schema for assessment creation response."""

    id: UUID
    url: str = Field(..., description="Public assessment URL with token")
    expires_at: datetime


class AssessmentResponse(BaseModel):
    """Schema for assessment response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    respondent_id: UUID
    selected_type_ids: list[UUID]
    expires_at: datetime
    status: AssessmentStatus
    completed_at: datetime | None
    created_at: datetime


class AssessmentList(BaseModel):
    """Schema for listing assessments (minimal fields)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    respondent_id: UUID
    status: AssessmentStatus
    expires_at: datetime
    created_at: datetime


class AssessmentWithRespondent(BaseModel):
    """Schema for assessment with respondent details."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    respondent_id: UUID
    respondent_name: str
    selected_type_ids: list[UUID]
    expires_at: datetime
    status: AssessmentStatus
    completed_at: datetime | None
    created_at: datetime
