"""QuestionGroup model for logical grouping of questions within a type."""

from decimal import Decimal
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModelWithTimestamps

if TYPE_CHECKING:
    from src.models.questionnaire_type import QuestionnaireType
    from src.models.question import Question


class QuestionGroup(BaseModelWithTimestamps):
    """Logical grouping of questions within a questionnaire type (Бүлэг).

    Attributes:
        type_id: Reference to parent questionnaire type.
        name: Group name (in Mongolian).
        display_order: Order within the type for display.
        weight: Weight for type score calculation.
        is_active: Whether available for new assessments.
    """

    __tablename__ = "question_groups"
    __table_args__ = (
        CheckConstraint("display_order >= 0", name="ck_group_display_order_non_negative"),
        CheckConstraint("weight > 0", name="ck_group_positive_weight"),
    )

    type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questionnaire_types.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Parent questionnaire type",
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Group name (Mongolian)",
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
        comment="Weight for type score calculation",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Available for new assessments",
    )

    # Relationships
    questionnaire_type: Mapped["QuestionnaireType"] = relationship(
        "QuestionnaireType",
        back_populates="groups",
    )
    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="group",
        cascade="all, delete-orphan",
        order_by="Question.display_order",
    )

    def __repr__(self) -> str:
        return f"<QuestionGroup(id={self.id}, name={self.name!r}, type_id={self.type_id})>"
