"""Repository for AssessmentDraft database operations."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.assessment_draft import AssessmentDraft


class DraftRepository:
    """Repository for draft database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(
        self,
        assessment_id: UUID,
        draft_data: dict,
    ) -> AssessmentDraft:
        """Create or update a draft for an assessment.

        Uses PostgreSQL ON CONFLICT DO UPDATE for atomic upsert.
        """
        stmt = insert(AssessmentDraft).values(
            assessment_id=assessment_id,
            draft_data=draft_data,
            last_saved_at=datetime.now(timezone.utc),
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["assessment_id"],
            set_={
                "draft_data": stmt.excluded.draft_data,
                "last_saved_at": stmt.excluded.last_saved_at,
            },
        )
        await self.session.execute(stmt)
        await self.session.flush()

        # Fetch the updated/created record
        return await self.get_by_assessment_id(assessment_id)

    async def get_by_assessment_id(
        self,
        assessment_id: UUID,
    ) -> AssessmentDraft | None:
        """Get draft by assessment ID."""
        result = await self.session.execute(
            select(AssessmentDraft).where(
                AssessmentDraft.assessment_id == assessment_id
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, assessment_id: UUID) -> bool:
        """Delete draft for an assessment.

        Returns True if a draft was deleted, False if none existed.
        """
        result = await self.session.execute(
            delete(AssessmentDraft).where(
                AssessmentDraft.assessment_id == assessment_id
            )
        )
        await self.session.flush()
        return result.rowcount > 0
