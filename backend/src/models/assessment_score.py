"""AssessmentScore model for calculated scores per type and overall."""

import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel
from src.models.enums import RiskRating


class AssessmentScore(BaseModel):
    """Calculated score for an assessment.

    One record per questionnaire type, plus one with type_id=NULL for overall score.

    Attributes:
        assessment_id: Reference to parent Assessment.
        type_id: QuestionnaireType ID, or NULL for overall score.
        raw_score: Sum of awarded scores.
        max_score: Maximum possible score.
        percentage: (raw_score / max_score) * 100.
        risk_rating: LOW, MEDIUM, or HIGH based on thresholds.
    """

    __tablename__ = "assessment_scores"
    __table_args__ = (
        UniqueConstraint("assessment_id", "type_id", name="uq_assessment_score_type"),
        CheckConstraint("raw_score >= 0", name="ck_raw_score_positive"),
        CheckConstraint("max_score >= 0", name="ck_max_score_positive"),
        CheckConstraint("raw_score <= max_score", name="ck_raw_score_lte_max"),
        CheckConstraint("percentage >= 0 AND percentage <= 100", name="ck_percentage_range"),
    )

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="Type ID or NULL for overall",
    )
    raw_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Sum of awarded scores",
    )
    max_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Maximum possible score",
    )
    percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Score percentage",
    )
    risk_rating: Mapped[RiskRating] = mapped_column(
        nullable=False,
        comment="LOW/MEDIUM/HIGH",
    )

    def __repr__(self) -> str:
        type_str = str(self.type_id) if self.type_id else "OVERALL"
        return f"<AssessmentScore(assessment_id={self.assessment_id}, type={type_str}, rating={self.risk_rating})>"
