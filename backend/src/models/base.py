"""Base SQLAlchemy model with common fields."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """Mixin that adds UUID primary key column."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class BaseModel(UUIDPrimaryKeyMixin, Base):
    """Abstract base model with UUID primary key.

    Use this as the base class for models that only need an ID.
    """

    __abstract__ = True


class BaseModelWithTimestamps(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Abstract base model with UUID primary key and timestamps.

    Use this as the base class for models that need ID and timestamps.
    """

    __abstract__ = True
