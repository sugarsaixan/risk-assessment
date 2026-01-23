"""AssessmentScore model for calculated scores per group, type, and overall."""

import uuid
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel
from src.models.enums import RiskRating


class AssessmentScore(BaseModel):
    """Calculated score for an assessment.

    Hierarchy of scores:
    - group_id != NULL, type_id != NULL: Group-level score within a type
    - group_id == NULL, type_id != NULL: Type-level score (aggregate of groups)
    - group_id == NULL, type_id == NULL: Overall score (aggregate of types)

    Attributes:
        assessment_id: Reference to parent Assessment.
        type_id: QuestionnaireType ID, or NULL for overall score.
        group_id: QuestionGroup ID, or NULL for type/overall score.
        raw_score: Sum of awarded scores.
        max_score: Maximum possible score.
        percentage: (raw_score / max_score) * 100.
        risk_rating: LOW, MEDIUM, or HIGH based on thresholds.
    """

    __tablename__ = "assessment_scores"
    __table_args__ = (
        UniqueConstraint(
            "assessment_id", "type_id", "group_id",
            name="uq_assessment_score_type_group"
        ),
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
    group_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="Group ID or NULL for type/overall",
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
        SAEnum(RiskRating, name="risk_rating"),
        nullable=False,
        comment="LOW/MEDIUM/HIGH",
    )

    def __repr__(self) -> str:
        type_str = str(self.type_id) if self.type_id else "OVERALL"
        group_str = str(self.group_id) if self.group_id else "TYPE/OVERALL"
        return f"<AssessmentScore(assessment_id={self.assessment_id}, type={type_str}, group={group_str}, rating={self.risk_rating})>"
