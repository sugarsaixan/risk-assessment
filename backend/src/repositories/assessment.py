"""Repository for Assessment CRUD operations."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.assessment import Assessment
from src.models.enums import AssessmentStatus


class AssessmentRepository:
    """Repository for Assessment database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        respondent_id: UUID,
        token_hash: str,
        selected_type_ids: list[UUID],
        questions_snapshot: dict[str, Any],
        expires_at: datetime,
    ) -> Assessment:
        """Create a new assessment."""
        assessment = Assessment(
            respondent_id=respondent_id,
            token_hash=token_hash,
            selected_type_ids=selected_type_ids,
            questions_snapshot=questions_snapshot,
            expires_at=expires_at,
        )
        self.session.add(assessment)
        await self.session.flush()
        await self.session.refresh(assessment)
        return assessment

    async def get_by_id(self, assessment_id: UUID) -> Assessment | None:
        """Get an assessment by ID."""
        result = await self.session.execute(
            select(Assessment).where(Assessment.id == assessment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_token_hash(self, token_hash: str) -> Assessment | None:
        """Get an assessment by token hash."""
        result = await self.session.execute(
            select(Assessment).where(Assessment.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        respondent_id: UUID | None = None,
        status: AssessmentStatus | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Assessment]:
        """Get all assessments with optional filtering."""
        stmt = select(Assessment).order_by(Assessment.created_at.desc())

        if respondent_id is not None:
            stmt = stmt.where(Assessment.respondent_id == respondent_id)

        if status is not None:
            stmt = stmt.where(Assessment.status == status)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        *,
        respondent_id: UUID | None = None,
        status: AssessmentStatus | None = None,
    ) -> int:
        """Count assessments with optional filtering."""
        from sqlalchemy import func

        stmt = select(func.count(Assessment.id))

        if respondent_id is not None:
            stmt = stmt.where(Assessment.respondent_id == respondent_id)

        if status is not None:
            stmt = stmt.where(Assessment.status == status)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update_status(
        self,
        assessment: Assessment,
        status: AssessmentStatus,
        completed_at: datetime | None = None,
    ) -> Assessment:
        """Update assessment status."""
        assessment.status = status
        if completed_at is not None:
            assessment.completed_at = completed_at
        await self.session.flush()
        await self.session.refresh(assessment)
        return assessment

    async def mark_expired(self, assessment: Assessment) -> Assessment:
        """Mark an assessment as expired."""
        return await self.update_status(assessment, AssessmentStatus.EXPIRED)

    async def mark_completed(self, assessment: Assessment, completed_at: datetime) -> Assessment:
        """Mark an assessment as completed."""
        return await self.update_status(assessment, AssessmentStatus.COMPLETED, completed_at)

    async def get_pending_expired(self, before: datetime) -> list[Assessment]:
        """Get pending assessments that have expired."""
        result = await self.session.execute(
            select(Assessment).where(
                Assessment.status == AssessmentStatus.PENDING,
                Assessment.expires_at < before,
            )
        )
        return list(result.scalars().all())
