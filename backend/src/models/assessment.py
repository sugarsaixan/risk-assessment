"""Assessment model for survey instances with question snapshots."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel
from src.models.enums import AssessmentStatus

if TYPE_CHECKING:
    from src.models.respondent import Respondent
    from src.models.submission_contact import SubmissionContact


class Assessment(BaseModel):
    """Assessment instance with question snapshots.

    Attributes:
        respondent_id: Reference to Respondent being assessed.
        token_hash: SHA-256 hash of the access token.
        selected_type_ids: Array of QuestionnaireType IDs included.
        questions_snapshot: Deep copy of questions/options at creation time.
        expires_at: Link expiration timestamp.
        status: PENDING, COMPLETED, or EXPIRED.
        completed_at: When submission occurred.
    """

    __tablename__ = "assessments"

    respondent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("respondents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
        comment="SHA-256 hash of access token",
    )
    selected_type_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        nullable=False,
        comment="QuestionnaireType IDs included",
    )
    questions_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Deep copy of questions/options",
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Link expiration time",
    )
    status: Mapped[AssessmentStatus] = mapped_column(
        SAEnum(AssessmentStatus, name="assessment_status"),
        nullable=False,
        default=AssessmentStatus.PENDING,
        index=True,
        comment="PENDING/COMPLETED/EXPIRED",
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Submission timestamp",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    respondent: Mapped["Respondent"] = relationship(
        "Respondent",
        back_populates="assessments",
    )
    submission_contact: Mapped["SubmissionContact | None"] = relationship(
        "SubmissionContact",
        back_populates="assessment",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<Assessment(id={self.id}, status={self.status}, respondent_id={self.respondent_id})>"
