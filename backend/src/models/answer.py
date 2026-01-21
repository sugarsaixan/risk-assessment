"""Answer model for respondent's answers to assessment questions."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel
from src.models.enums import OptionType


class Answer(BaseModel):
    """Respondent's answer to an assessment question.

    Attributes:
        assessment_id: Reference to parent Assessment.
        question_id: Question ID from the snapshot.
        selected_option: YES or NO.
        comment: Optional/required comment text.
        score_awarded: Points received for this answer.
    """

    __tablename__ = "answers"
    __table_args__ = (
        UniqueConstraint("assessment_id", "question_id", name="uq_answer_assessment_question"),
        CheckConstraint("char_length(comment) <= 2000", name="ck_comment_max_length"),
        CheckConstraint("score_awarded >= 0", name="ck_positive_score_awarded"),
    )

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        comment="Question ID from snapshot",
    )
    selected_option: Mapped[OptionType] = mapped_column(
        nullable=False,
        comment="YES or NO",
    )
    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Optional/required comment",
    )
    score_awarded: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Points received",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment",
        back_populates="answer",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Answer(id={self.id}, question_id={self.question_id}, option={self.selected_option})>"


# Import for type hint
from src.models.attachment import Attachment  # noqa: E402, F401
