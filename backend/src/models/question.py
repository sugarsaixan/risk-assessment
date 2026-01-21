"""Question model for assessment questions."""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel

if TYPE_CHECKING:
    from src.models.question_option import QuestionOption
    from src.models.questionnaire_type import QuestionnaireType


class Question(BaseModel):
    """Individual YES/NO question within a questionnaire type.

    Attributes:
        type_id: Reference to parent QuestionnaireType.
        text: Question text (in Mongolian).
        display_order: Order within the type for display.
        weight: Question weight for scoring (future use).
        is_critical: Critical flag (future use).
        is_active: Available for snapshots.
    """

    __tablename__ = "questions"
    __table_args__ = (
        CheckConstraint("display_order >= 0", name="ck_positive_display_order"),
        CheckConstraint("char_length(text) <= 2000", name="ck_text_max_length"),
    )

    type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questionnaire_types.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Question text (Mongolian)",
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Order within type for display",
    )
    weight: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("1.0"),
        comment="Question weight (future use)",
    )
    is_critical: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Critical flag (future use)",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Available for snapshots",
    )

    # Relationships
    questionnaire_type: Mapped["QuestionnaireType"] = relationship(
        "QuestionnaireType",
        back_populates="questions",
    )
    options: Mapped[list["QuestionOption"]] = relationship(
        "QuestionOption",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, text={self.text[:50]!r}..., is_active={self.is_active})>"
