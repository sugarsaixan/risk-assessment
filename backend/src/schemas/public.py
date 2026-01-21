"""Pydantic schemas for public API endpoints."""

from typing import Any

from pydantic import BaseModel, Field

from src.models.enums import RiskRating
from src.schemas.answer import AnswerInput


class AssessmentFormResponse(BaseModel):
    """Schema for public assessment form data."""

    id: str = Field(..., description="Assessment ID")
    respondent_name: str = Field(..., description="Respondent's name")
    expires_at: str = Field(..., description="Expiration timestamp")
    types: list[dict[str, Any]] = Field(
        ...,
        description="Questionnaire types with questions from snapshot",
    )


class SubmitRequest(BaseModel):
    """Schema for assessment submission request."""

    answers: list[AnswerInput] = Field(
        ...,
        min_length=1,
        description="List of answers for all questions",
    )


class TypeResult(BaseModel):
    """Schema for per-type score result."""

    type_id: str = Field(..., description="Questionnaire type ID")
    type_name: str = Field(..., description="Questionnaire type name")
    raw_score: int = Field(..., ge=0, description="Total points awarded")
    max_score: int = Field(..., ge=0, description="Maximum possible points")
    percentage: float = Field(..., ge=0, le=100, description="Score percentage")
    risk_rating: RiskRating = Field(..., description="Risk rating")


class OverallResult(BaseModel):
    """Schema for overall assessment result."""

    raw_score: int = Field(..., ge=0, description="Total points awarded")
    max_score: int = Field(..., ge=0, description="Maximum possible points")
    percentage: float = Field(..., ge=0, le=100, description="Score percentage")
    risk_rating: RiskRating = Field(..., description="Overall risk rating")


class SubmitResponse(BaseModel):
    """Schema for assessment submission response."""

    assessment_id: str = Field(..., description="Assessment ID")
    type_results: list[TypeResult] = Field(
        ...,
        description="Per-type score results",
    )
    overall_result: OverallResult = Field(..., description="Overall assessment result")


class AssessmentErrorResponse(BaseModel):
    """Schema for assessment access error."""

    error: str = Field(
        ...,
        description="Error code: not_found, expired, already_completed",
    )
    message: str = Field(..., description="Human-readable error message in Mongolian")
