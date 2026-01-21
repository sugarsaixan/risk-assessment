"""Pydantic schemas for Respondent."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import RespondentKind


class RespondentCreate(BaseModel):
    """Schema for creating a respondent."""

    kind: RespondentKind = Field(..., description="ORG or PERSON")
    name: str = Field(..., min_length=1, max_length=300, description="Respondent name")
    registration_no: str | None = Field(
        None,
        max_length=50,
        description="Org registration or person ID",
    )


class RespondentUpdate(BaseModel):
    """Schema for updating a respondent."""

    kind: RespondentKind | None = None
    name: str | None = Field(None, min_length=1, max_length=300)
    registration_no: str | None = Field(None, max_length=50)


class RespondentResponse(BaseModel):
    """Schema for respondent response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kind: RespondentKind
    name: str
    registration_no: str | None
    created_at: datetime
    updated_at: datetime


class RespondentList(BaseModel):
    """Schema for listing respondents (minimal fields)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kind: RespondentKind
    name: str
