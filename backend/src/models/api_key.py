"""API Key model for admin authentication."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class ApiKey(BaseModel):
    """API key for authenticating admin requests.

    Keys are stored as Argon2 hashes for security.
    """

    __tablename__ = "api_keys"

    key_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        index=True,
        comment="Argon2 hash of the API key",
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Descriptive name for the key",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Whether the key can be used for authentication",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last successful authentication timestamp",
    )

    def __repr__(self) -> str:
        return f"<ApiKey(id={self.id}, name={self.name!r}, is_active={self.is_active})>"
