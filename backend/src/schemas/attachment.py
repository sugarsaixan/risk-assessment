"""Pydantic schemas for Attachment."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AttachmentUpload(BaseModel):
    """Schema for attachment upload response."""

    id: UUID = Field(..., description="Attachment ID for reference in submission")
    original_name: str = Field(..., description="Original filename")
    size_bytes: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="Detected MIME type")


class AttachmentResponse(BaseModel):
    """Schema for attachment response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    answer_id: UUID
    storage_key: str
    original_name: str
    size_bytes: int
    mime_type: str
    created_at: datetime
