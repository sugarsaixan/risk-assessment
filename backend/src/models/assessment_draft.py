"""AssessmentDraft model for server-side draft storage."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.assessment import Assessment


class AssessmentDraft(Base):
    """Server-side storage for partial questionnaire progress.

    Attributes:
        assessment_id: Reference to the Assessment being drafted.
        draft_data: JSONB containing answers, current position, etc.
        last_saved_at: When the draft was last updated.
        created_at: When the draft was first created.
    """

    __tablename__ = "assessment_drafts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    draft_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Serialized form state (answers, position)",
    )
    last_saved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    assessment: Mapped["Assessment"] = relationship(
        "Assessment",
        back_populates="draft",
    )

    def __repr__(self) -> str:
        return f"<AssessmentDraft(id={self.id}, assessment_id={self.assessment_id})>"
