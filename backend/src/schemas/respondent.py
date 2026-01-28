"""Pydantic schemas for Respondent."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.models.enums import RespondentKind


class RespondentInline(BaseModel):
    """Inline respondent data provided from Odoo during assessment creation."""

    odoo_id: str = Field(..., max_length=100, description="Unique respondent ID from Odoo")
    name: str = Field(..., min_length=1, max_length=300, description="Respondent name")
    kind: RespondentKind = Field(..., description="ORG or PERSON")
    registration_no: str | None = Field(
        None,
        max_length=50,
        description="Required for ORG, optional for PERSON",
    )

    @model_validator(mode="after")
    def validate_registration_no(self) -> "RespondentInline":
        if self.kind == RespondentKind.ORG and not self.registration_no:
            raise ValueError("registration_no is required for ORG respondents")
        return self


class RespondentResponse(BaseModel):
    """Schema for respondent response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kind: RespondentKind
    name: str
    registration_no: str | None
    odoo_id: str | None = None
    created_at: datetime
    updated_at: datetime


class RespondentList(BaseModel):
    """Schema for listing respondents (minimal fields)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kind: RespondentKind
    name: str
