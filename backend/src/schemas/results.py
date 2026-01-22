"""Pydantic schemas for assessment results."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import OptionType, RiskRating


class TypeScore(BaseModel):
    """Schema for per-type score result."""

    type_id: UUID = Field(..., description="Questionnaire type ID")
    type_name: str = Field(..., description="Questionnaire type name")
    raw_score: int = Field(..., ge=0, description="Total points awarded")
    max_score: int = Field(..., ge=0, description="Maximum possible points")
    percentage: float = Field(..., ge=0, le=100, description="Score percentage")
    risk_rating: RiskRating = Field(..., description="Risk rating based on thresholds")


class OverallScore(BaseModel):
    """Schema for overall assessment score."""

    raw_score: int = Field(..., ge=0, description="Total points awarded")
    max_score: int = Field(..., ge=0, description="Maximum possible points")
    percentage: float = Field(..., ge=0, le=100, description="Score percentage")
    risk_rating: RiskRating = Field(..., description="Overall risk rating")


class AnswerBreakdown(BaseModel):
    """Schema for individual answer in breakdown."""

    question_id: UUID = Field(..., description="Question ID from snapshot")
    question_text: str = Field(..., description="Question text from snapshot")
    type_id: UUID = Field(..., description="Questionnaire type ID")
    type_name: str = Field(..., description="Questionnaire type name")
    selected_option: OptionType = Field(..., description="YES or NO")
    comment: str | None = Field(None, description="Optional comment")
    score_awarded: int = Field(..., ge=0, description="Points received")
    max_score: int = Field(..., ge=0, description="Maximum possible for this question")
    attachment_count: int = Field(default=0, ge=0, description="Number of attachments")


class AssessmentResultsResponse(BaseModel):
    """Schema for complete assessment results."""

    model_config = ConfigDict(from_attributes=True)

    assessment_id: UUID = Field(..., description="Assessment ID")
    respondent_id: UUID = Field(..., description="Respondent ID")
    respondent_name: str = Field(..., description="Respondent name")
    status: str = Field(..., description="Assessment status")
    completed_at: datetime | None = Field(None, description="Completion timestamp")

    # Scores
    type_scores: list[TypeScore] = Field(
        ...,
        description="Per-type score results",
    )
    overall_score: OverallScore = Field(
        ...,
        description="Overall assessment score",
    )

    # Optional breakdown
    answer_breakdown: list[AnswerBreakdown] | None = Field(
        None,
        description="Individual answer details (only included if breakdown=true)",
    )
