"""SubmissionContact model for storing contact info of who filled out the assessment."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModelWithTimestamps

if TYPE_CHECKING:
    from src.models.assessment import Assessment


class SubmissionContact(BaseModelWithTimestamps):
    """Contact information for the person who submitted the assessment.

    This is separate from Respondent - the respondent is the entity being assessed,
    while the submission contact is the person who actually fills out the form.

    Attributes:
        assessment_id: Reference to parent Assessment (one-to-one).
        last_name: Овог (Family name).
        first_name: Нэр (Given name).
        email: Email address.
        phone: Phone number.
        position: Албан тушаал (Job position/title).
    """

    __tablename__ = "submission_contacts"

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Овог (Family name)",
    )
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Нэр (Given name)",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Email address",
    )
    phone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Phone number",
    )
    position: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Албан тушаал (Job position)",
    )

    # Relationships
    assessment: Mapped["Assessment"] = relationship(
        "Assessment",
        back_populates="submission_contact",
    )

    def __repr__(self) -> str:
        return f"<SubmissionContact(id={self.id}, name={self.last_name} {self.first_name}, email={self.email})>"
