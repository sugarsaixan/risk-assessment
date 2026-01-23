"""Pydantic schemas for assessment results."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import OptionType, RiskRating


class GroupScore(BaseModel):
    """Schema for per-group score result within a type."""

    group_id: UUID = Field(..., description="Question group ID")
    group_name: str = Field(..., description="Question group name")
    raw_score: int = Field(..., ge=0, description="Total points awarded")
    max_score: int = Field(..., ge=0, description="Maximum possible points")
    percentage: float = Field(..., ge=0, le=100, description="Score percentage")
    risk_rating: RiskRating = Field(..., description="Risk rating based on thresholds")


class TypeScore(BaseModel):
    """Schema for per-type score result."""

    type_id: UUID = Field(..., description="Questionnaire type ID")
    type_name: str = Field(..., description="Questionnaire type name")
    raw_score: int = Field(..., ge=0, description="Total points awarded")
    max_score: int = Field(..., ge=0, description="Maximum possible points")
    percentage: float = Field(..., ge=0, le=100, description="Score percentage")
    risk_rating: RiskRating = Field(..., description="Risk rating based on thresholds")
    groups: list[GroupScore] = Field(
        default_factory=list,
        description="Per-group score breakdown within this type",
    )


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


class SubmissionContactInfo(BaseModel):
    """Schema for submission contact info in results."""

    model_config = ConfigDict(from_attributes=True)

    last_name: str = Field(..., description="Овог (Family name)")
    first_name: str = Field(..., description="Нэр (Given name)")
    email: str = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    position: str = Field(..., description="Албан тушаал (Job position)")


class AssessmentResultsResponse(BaseModel):
    """Schema for complete assessment results."""

    model_config = ConfigDict(from_attributes=True)

    assessment_id: UUID = Field(..., description="Assessment ID")
    respondent_id: UUID = Field(..., description="Respondent ID")
    respondent_name: str = Field(..., description="Respondent name")
    status: str = Field(..., description="Assessment status")
    completed_at: datetime | None = Field(None, description="Completion timestamp")

    # Submission contact (who filled the form)
    contact: SubmissionContactInfo | None = Field(
        None,
        description="Contact info of person who filled the assessment (Хариулагч)",
    )

    # Scores
    type_scores: list[TypeScore] = Field(
        ...,
        description="Per-type score results with group breakdown",
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
