"""Pydantic schemas for QuestionnaireType."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import ScoringMethod


class QuestionnaireTypeCreate(BaseModel):
    """Schema for creating a questionnaire type."""

    name: str = Field(..., min_length=1, max_length=200, description="Type name (Mongolian)")
    scoring_method: ScoringMethod = Field(
        default=ScoringMethod.SUM,
        description="Score calculation method",
    )
    threshold_high: int = Field(
        default=80,
        ge=0,
        le=100,
        description="Percentage threshold for LOW risk (>= this = low)",
    )
    threshold_medium: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Percentage threshold for MEDIUM risk (>= this = medium)",
    )
    weight: Decimal = Field(
        default=Decimal("1.0"),
        gt=0,
        le=Decimal("100.0"),
        description="Weight for overall score calculation",
    )


class QuestionnaireTypeUpdate(BaseModel):
    """Schema for updating a questionnaire type."""

    name: str | None = Field(None, min_length=1, max_length=200)
    scoring_method: ScoringMethod | None = None
    threshold_high: int | None = Field(None, ge=0, le=100)
    threshold_medium: int | None = Field(None, ge=0, le=100)
    weight: Decimal | None = Field(None, gt=0, le=Decimal("100.0"))
    is_active: bool | None = None


class QuestionnaireTypeResponse(BaseModel):
    """Schema for questionnaire type response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    scoring_method: ScoringMethod
    threshold_high: int
    threshold_medium: int
    weight: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


class QuestionnaireTypeList(BaseModel):
    """Schema for listing questionnaire types (minimal fields)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    is_active: bool
