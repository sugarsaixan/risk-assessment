"""Service for handling file uploads."""

import uuid
from typing import BinaryIO

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.storage import generate_storage_key, upload_file
from src.models.attachment import Attachment
from src.schemas.attachment import AttachmentUpload

# Allowed image MIME types
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}


class UploadService:
    """Service for validating and uploading files."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def validate_file(
        self,
        filename: str,
        content_type: str,
        size_bytes: int,
        max_size_mb: int | None = None,
    ) -> str | None:
        """Validate a file for upload.

        Args:
            filename: Original filename.
            content_type: MIME type from upload.
            size_bytes: File size in bytes.
            max_size_mb: Maximum size in MB (uses config default if None).

        Returns:
            Error message if invalid, None if valid.
        """
        if max_size_mb is None:
            max_size_mb = settings.upload_max_size_mb

        # Check MIME type
        if content_type not in ALLOWED_MIME_TYPES:
            return f"Invalid file type: {content_type}. Allowed: JPEG, PNG, GIF, WebP"

        # Check file size
        max_bytes = max_size_mb * 1024 * 1024
        if size_bytes > max_bytes:
            return f"File too large: {size_bytes} bytes. Maximum: {max_size_mb}MB"

        # Check filename
        if not filename or len(filename) > 255:
            return "Invalid filename"

        return None

    async def upload_image(
        self,
        assessment_id: uuid.UUID,
        question_id: uuid.UUID,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> AttachmentUpload:
        """Upload an image and create an attachment record.

        Args:
            assessment_id: Assessment UUID.
            question_id: Question UUID this image is for.
            filename: Original filename.
            content_type: MIME type.
            content: File content bytes.

        Returns:
            AttachmentUpload with the created attachment info.

        Raises:
            ValueError: If file validation fails.
        """
        # Validate file
        error = self.validate_file(filename, content_type, len(content))
        if error:
            raise ValueError(error)

        # Generate storage key
        storage_key = generate_storage_key(assessment_id, question_id, filename)

        # Upload to S3/MinIO
        await upload_file(content, storage_key, content_type)

        # Create attachment record (not yet linked to answer)
        # The answer_id will be set during submission
        # For now, we create a temporary record
        attachment = Attachment(
            answer_id=uuid.uuid4(),  # Temporary, will be updated on submission
            storage_key=storage_key,
            original_name=filename,
            size_bytes=len(content),
            mime_type=content_type,
        )
        self.session.add(attachment)
        await self.session.flush()
        await self.session.refresh(attachment)

        return AttachmentUpload(
            id=attachment.id,
            original_name=attachment.original_name,
            size_bytes=attachment.size_bytes,
            mime_type=attachment.mime_type,
        )

    async def get_attachment(self, attachment_id: uuid.UUID) -> Attachment | None:
        """Get an attachment by ID."""
        from sqlalchemy import select

        result = await self.session.execute(
            select(Attachment).where(Attachment.id == attachment_id)
        )
        return result.scalar_one_or_none()

    async def link_attachments_to_answer(
        self,
        answer_id: uuid.UUID,
        attachment_ids: list[uuid.UUID],
    ) -> None:
        """Link uploaded attachments to an answer.

        Args:
            answer_id: Answer UUID.
            attachment_ids: List of attachment UUIDs to link.
        """
        from sqlalchemy import update

        if attachment_ids:
            await self.session.execute(
                update(Attachment)
                .where(Attachment.id.in_(attachment_ids))
                .values(answer_id=answer_id)
            )
