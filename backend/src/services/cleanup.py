"""Service for admin cleanup operations on orphaned drafts and images."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.storage import delete_file
from src.models.answer import Answer
from src.models.assessment import Assessment
from src.models.assessment_draft import AssessmentDraft
from src.models.attachment import Attachment
from src.models.enums import AssessmentStatus


# ============================================================================
# Response data classes
# ============================================================================


@dataclass
class CleanupDetail:
    """Detail about a single cleaned-up assessment."""

    assessment_id: str
    expired_at: str
    draft_size_bytes: int


@dataclass
class DraftCleanupResult:
    """Result of draft cleanup operation."""

    drafts_deleted: int = 0
    assessments_affected: int = 0
    images_deleted: int = 0
    storage_freed_bytes: int = 0
    dry_run: bool = False
    details: list[CleanupDetail] = field(default_factory=list)


@dataclass
class ImageCleanupResult:
    """Result of image cleanup operation."""

    images_deleted: int = 0
    storage_freed_bytes: int = 0
    dry_run: bool = False


# ============================================================================
# Service
# ============================================================================


class CleanupService:
    """Service for cleaning up orphaned drafts and images."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def cleanup_drafts(
        self,
        older_than_days: int = 30,
        include_images: bool = False,
        dry_run: bool = False,
    ) -> DraftCleanupResult:
        """Delete draft records for expired assessments.

        Args:
            older_than_days: Only cleanup drafts for assessments expired
                more than N days ago.
            include_images: Also delete orphaned images from storage.
            dry_run: Preview what would be deleted without actually deleting.

        Returns:
            DraftCleanupResult with counts and details.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)

        # Find expired assessments with drafts
        stmt = (
            select(Assessment, AssessmentDraft)
            .join(AssessmentDraft, Assessment.id == AssessmentDraft.assessment_id)
            .where(
                Assessment.expires_at < cutoff,
                Assessment.status != AssessmentStatus.COMPLETED,
            )
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        details: list[CleanupDetail] = []
        total_storage_freed = 0
        images_deleted = 0

        for assessment, draft in rows:
            # Estimate draft size from JSON data
            import json

            draft_json = json.dumps(draft.draft_data)
            draft_size = len(draft_json.encode("utf-8"))

            details.append(
                CleanupDetail(
                    assessment_id=str(assessment.id),
                    expired_at=assessment.expires_at.isoformat(),
                    draft_size_bytes=draft_size,
                )
            )
            total_storage_freed += draft_size

        if not dry_run and rows:
            # Get list of assessment IDs to clean
            assessment_ids = [assessment.id for assessment, _ in rows]

            # Delete orphaned images if requested
            if include_images:
                images_deleted, img_storage = await self._delete_orphaned_images_for_assessments(
                    assessment_ids
                )
                total_storage_freed += img_storage

            # Delete the draft records
            await self.session.execute(
                delete(AssessmentDraft).where(
                    AssessmentDraft.assessment_id.in_(assessment_ids)
                )
            )
            await self.session.flush()

        return DraftCleanupResult(
            drafts_deleted=len(rows) if not dry_run else 0,
            assessments_affected=len(rows),
            images_deleted=images_deleted,
            storage_freed_bytes=total_storage_freed,
            dry_run=dry_run,
            details=details,
        )

    async def cleanup_images(
        self,
        older_than_days: int = 30,
        dry_run: bool = False,
    ) -> ImageCleanupResult:
        """Delete orphaned images not referenced by any submitted answer.

        Orphaned images are attachments whose answer_id doesn't reference
        a valid answer record (i.e., uploaded but assessment never submitted).

        Args:
            older_than_days: Only cleanup images uploaded more than N days ago.
            dry_run: Preview what would be deleted without actually deleting.

        Returns:
            ImageCleanupResult with counts.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)

        # Find attachments not linked to any valid answer and older than cutoff
        # An orphaned attachment is one where the referenced answer doesn't exist
        # (the temporary UUID assigned during upload was never updated to a real answer)
        orphaned_stmt = (
            select(Attachment)
            .outerjoin(Answer, Attachment.answer_id == Answer.id)
            .where(
                Answer.id.is_(None),
                Attachment.created_at < cutoff,
            )
        )
        result = await self.session.execute(orphaned_stmt)
        orphaned = result.scalars().all()

        total_storage = sum(att.size_bytes for att in orphaned)

        if not dry_run and orphaned:
            # Delete from object storage
            for attachment in orphaned:
                try:
                    await delete_file(attachment.storage_key)
                except Exception:
                    # Log but don't fail the batch if one file fails
                    pass

            # Delete DB records
            orphaned_ids = [att.id for att in orphaned]
            await self.session.execute(
                delete(Attachment).where(Attachment.id.in_(orphaned_ids))
            )
            await self.session.flush()

        return ImageCleanupResult(
            images_deleted=len(orphaned) if not dry_run else 0,
            storage_freed_bytes=total_storage,
            dry_run=dry_run,
        )

    async def _delete_orphaned_images_for_assessments(
        self,
        assessment_ids: list,
    ) -> tuple[int, int]:
        """Delete images uploaded for given assessments that were never submitted.

        Returns:
            Tuple of (images_deleted_count, storage_freed_bytes).
        """
        # Find attachments linked to these assessments via storage_key pattern
        # Storage keys follow: assessments/{assessment_id}/...
        deleted_count = 0
        freed_bytes = 0

        for assessment_id in assessment_ids:
            prefix = f"assessments/{assessment_id}/"
            stmt = select(Attachment).where(
                Attachment.storage_key.startswith(prefix)
            )
            result = await self.session.execute(stmt)
            attachments = result.scalars().all()

            for attachment in attachments:
                try:
                    await delete_file(attachment.storage_key)
                except Exception:
                    pass
                freed_bytes += attachment.size_bytes
                deleted_count += 1

            if attachments:
                att_ids = [a.id for a in attachments]
                await self.session.execute(
                    delete(Attachment).where(Attachment.id.in_(att_ids))
                )

        await self.session.flush()
        return deleted_count, freed_bytes
