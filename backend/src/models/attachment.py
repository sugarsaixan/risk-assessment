"""Attachment model for image files uploaded with answers."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Attachment(BaseModel):
    """Image file uploaded with an answer.

    Attributes:
        answer_id: Reference to parent Answer.
        storage_key: S3/MinIO object key.
        original_name: Original filename.
        size_bytes: File size in bytes.
        mime_type: MIME type (image/jpeg, image/png, etc.).
    """

    __tablename__ = "attachments"

    answer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("answers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    storage_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
        comment="S3/MinIO object key",
    )
    original_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Original filename",
    )
    size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="File size in bytes",
    )
    mime_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="MIME type",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    answer: Mapped["Answer"] = relationship(
        "Answer",
        back_populates="attachments",
    )

    def __repr__(self) -> str:
        return f"<Attachment(id={self.id}, original_name={self.original_name!r})>"


# Import for type hint
from src.models.answer import Answer  # noqa: E402, F401
