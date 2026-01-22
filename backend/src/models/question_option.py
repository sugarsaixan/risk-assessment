"""QuestionOption model for YES/NO option configuration."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Enum as SAEnum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel
from src.models.enums import OptionType

if TYPE_CHECKING:
    from src.models.question import Question


class QuestionOption(BaseModel):
    """Configuration for YES or NO option per question.

    Attributes:
        question_id: Reference to parent Question.
        option_type: YES or NO.
        score: Points awarded when this option is selected.
        require_comment: Whether comment is required.
        require_image: Whether image is required.
        comment_min_len: Minimum comment length if required.
        max_images: Maximum number of images allowed.
        image_max_mb: Maximum image size in MB.
    """

    __tablename__ = "question_options"
    __table_args__ = (
        UniqueConstraint("question_id", "option_type", name="uq_question_option_type"),
        CheckConstraint("score >= 0", name="ck_positive_score"),
        CheckConstraint(
            "comment_min_len >= 0 AND comment_min_len <= 2000",
            name="ck_comment_min_len_range",
        ),
        CheckConstraint(
            "max_images >= 1 AND max_images <= 10",
            name="ck_max_images_range",
        ),
        CheckConstraint(
            "image_max_mb >= 1 AND image_max_mb <= 20",
            name="ck_image_max_mb_range",
        ),
    )

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    option_type: Mapped[OptionType] = mapped_column(
        SAEnum(OptionType, name="option_type"),
        nullable=False,
        comment="YES or NO",
    )
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Points awarded for this option",
    )
    require_comment: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Comment required when selected",
    )
    require_image: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Image required when selected",
    )
    comment_min_len: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Minimum comment characters",
    )
    max_images: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        comment="Maximum images allowed",
    )
    image_max_mb: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        comment="Maximum image size in MB",
    )

    # Relationships
    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="options",
    )

    def __repr__(self) -> str:
        return f"<QuestionOption(id={self.id}, option_type={self.option_type}, score={self.score})>"
