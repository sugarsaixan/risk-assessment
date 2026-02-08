"""Pydantic schemas for public API endpoints."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from src.models.enums import OptionType, RiskRating
from src.schemas.answer import AnswerInput
from src.schemas.draft import DraftResponse
from src.schemas.submission_contact import SubmissionContactInput


class AssessmentFormResponse(BaseModel):
    """Schema for public assessment form data.

    Returns hierarchical structure: Type → Group → Question
    """

    id: str = Field(..., description="Assessment ID")
    respondent_name: str = Field(..., description="Respondent's name")
    expires_at: str = Field(..., description="Expiration timestamp")
    types: list[dict[str, Any]] = Field(
        ...,
        description="Questionnaire types with groups and questions from snapshot",
    )
    draft: Optional[DraftResponse] = Field(
        None,
        description="Saved draft answers if any exist",
    )


class SubmitRequest(BaseModel):
    """Schema for assessment submission request."""

    contact: SubmissionContactInput = Field(
        ...,
        description="Contact information of the person submitting the assessment",
    )
    answers: list[AnswerInput] = Field(
        ...,
        min_length=1,
        description="List of answers for all questions",
    )


class GroupResult(BaseModel):
    """Schema for per-group score result within a type."""

    group_id: str = Field(..., description="Question group ID")
    group_name: str = Field(..., description="Question group name")
    raw_score: int = Field(..., ge=0, description="Total points awarded in group")
    max_score: int = Field(..., ge=0, description="Maximum possible points in group")
    percentage: float = Field(..., ge=0, le=100, description="Group score percentage")
    risk_rating: RiskRating = Field(..., description="Group risk rating")


class TypeResult(BaseModel):
    """Schema for per-type score result."""

    type_id: str = Field(..., description="Questionnaire type ID")
    type_name: str = Field(..., description="Questionnaire type name")
    raw_score: int = Field(..., ge=0, description="Total points awarded")
    max_score: int = Field(..., ge=0, description="Maximum possible points")
    percentage: float = Field(..., ge=0, le=100, description="Score percentage")
    risk_rating: RiskRating = Field(..., description="Risk rating")
    groups: list[GroupResult] = Field(
        default=[],
        description="Per-group score results within this type",
    )


class OverallResult(BaseModel):
    """Schema for overall assessment result."""

    raw_score: int = Field(..., ge=0, description="Total points awarded")
    max_score: int = Field(..., ge=0, description="Maximum possible points")
    percentage: float = Field(..., ge=0, le=100, description="Score percentage")
    risk_rating: RiskRating = Field(..., description="Overall risk rating")


class AnswerBreakdownItem(BaseModel):
    """Schema for individual answer in breakdown."""

    question_id: str = Field(..., description="Question ID")
    question_text: str = Field(..., description="Question text")
    type_id: str = Field(..., description="Questionnaire type ID")
    type_name: str = Field(..., description="Questionnaire type name")
    selected_option: OptionType = Field(..., description="YES or NO")
    comment: str | None = Field(None, description="Optional comment")
    score_awarded: int = Field(..., ge=0, description="Points received")
    max_score: int = Field(..., ge=0, description="Maximum possible points")
    attachment_count: int = Field(default=0, ge=0, description="Number of attachments")


class SubmitResponse(BaseModel):
    """Schema for assessment submission response."""

    assessment_id: str = Field(..., description="Assessment ID")
    type_results: list[TypeResult] = Field(
        ...,
        description="Per-type score results with nested group results",
    )
    overall_result: OverallResult = Field(..., description="Overall assessment result")
    answer_breakdown: list[AnswerBreakdownItem] | None = Field(
        None,
        description="Individual answer details (only included when breakdown=true)",
    )


class AssessmentErrorResponse(BaseModel):
    """Schema for assessment access error."""

    error: str = Field(
        ...,
        description="Error code: not_found, expired, already_completed",
    )
    message: str = Field(..., description="Human-readable error message in Mongolian")
