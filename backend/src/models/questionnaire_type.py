"""QuestionnaireType model for categorizing questions."""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Enum as SAEnum, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModelWithTimestamps
from src.models.enums import ScoringMethod

if TYPE_CHECKING:
    from src.models.question import Question
    from src.models.question_group import QuestionGroup


class QuestionnaireType(BaseModelWithTimestamps):
    """Category of questions with scoring configuration.

    Attributes:
        name: Type name (in Mongolian).
        scoring_method: How to calculate scores (SUM only for Phase 1).
        threshold_high: Percentage threshold for LOW risk (>= this = low risk).
        threshold_medium: Percentage threshold for MEDIUM risk (>= this = medium risk).
        weight: Weight for overall score calculation.
        is_active: Whether available for new assessments.
    """

    __tablename__ = "questionnaire_types"
    __table_args__ = (
        CheckConstraint("threshold_high > threshold_medium", name="ck_threshold_order"),
        CheckConstraint("weight > 0", name="ck_positive_weight"),
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Type name (Mongolian)",
    )
    scoring_method: Mapped[ScoringMethod] = mapped_column(
        SAEnum(ScoringMethod, name="scoring_method"),
        nullable=False,
        default=ScoringMethod.SUM,
        comment="Score calculation method",
    )
    threshold_high: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=80,
        comment="Percentage threshold for LOW risk",
    )
    threshold_medium: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=50,
        comment="Percentage threshold for MEDIUM risk",
    )
    weight: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("1.0"),
        comment="Weight for overall score calculation",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Available for new assessments",
    )

    # Relationships
    groups: Mapped[list["QuestionGroup"]] = relationship(
        "QuestionGroup",
        back_populates="questionnaire_type",
        cascade="all, delete-orphan",
        order_by="QuestionGroup.display_order",
    )
    # Legacy: direct questions relationship (for migration compatibility)
    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="questionnaire_type",
        cascade="all, delete-orphan",
        order_by="Question.display_order",
    )

    def __repr__(self) -> str:
        return f"<QuestionnaireType(id={self.id}, name={self.name!r}, is_active={self.is_active})>"
