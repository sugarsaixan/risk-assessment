"""Pydantic schemas for Assessment."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import AssessmentStatus
from src.schemas.respondent import RespondentInline


class AssessmentCreate(BaseModel):
    """Schema for creating an assessment with inline respondent data from Odoo."""

    respondent: RespondentInline = Field(..., description="Inline respondent data from Odoo")
    employee_id: str | None = Field(
        None,
        max_length=100,
        description="Odoo employee ID who is creating this assessment",
    )
    employee_name: str | None = Field(
        None,
        max_length=300,
        description="Display name of the Odoo employee",
    )
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
    respondent_id: UUID = Field(..., description="Internal respondent UUID (created or matched)")
    url: str = Field(..., description="Public assessment URL with token")
    expires_at: datetime


class AssessmentResponse(BaseModel):
    """Schema for assessment response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    respondent_id: UUID
    respondent_odoo_id: str | None = None
    employee_id: str | None = None
    employee_name: str | None = None
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
    respondent_odoo_id: str | None = None
    employee_id: str | None = None
    employee_name: str | None = None
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
