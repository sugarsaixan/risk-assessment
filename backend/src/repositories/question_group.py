"""Repository for QuestionGroup CRUD operations."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.question_group import QuestionGroup
from src.schemas.question_group import QuestionGroupCreate, QuestionGroupUpdate


class QuestionGroupRepository:
    """Repository for QuestionGroup database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: QuestionGroupCreate) -> QuestionGroup:
        """Create a new question group."""
        question_group = QuestionGroup(**data.model_dump())
        self.session.add(question_group)
        await self.session.flush()
        await self.session.refresh(question_group)
        return question_group

    async def get_by_id(self, group_id: UUID) -> QuestionGroup | None:
        """Get a question group by ID."""
        result = await self.session.execute(
            select(QuestionGroup).where(QuestionGroup.id == group_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_questions(self, group_id: UUID) -> QuestionGroup | None:
        """Get a question group by ID with questions loaded."""
        result = await self.session.execute(
            select(QuestionGroup)
            .where(QuestionGroup.id == group_id)
            .options(selectinload(QuestionGroup.questions))
        )
        return result.scalar_one_or_none()

    async def get_by_type_id(
        self,
        type_id: UUID,
        *,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[QuestionGroup]:
        """Get all question groups for a type with optional filtering."""
        stmt = (
            select(QuestionGroup)
            .where(QuestionGroup.type_id == type_id)
            .order_by(QuestionGroup.display_order)
        )

        if is_active is not None:
            stmt = stmt.where(QuestionGroup.is_active == is_active)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all(
        self,
        *,
        type_id: UUID | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[QuestionGroup]:
        """Get all question groups with optional filtering."""
        stmt = select(QuestionGroup).order_by(
            QuestionGroup.type_id, QuestionGroup.display_order
        )

        if type_id is not None:
            stmt = stmt.where(QuestionGroup.type_id == type_id)

        if is_active is not None:
            stmt = stmt.where(QuestionGroup.is_active == is_active)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        *,
        type_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> int:
        """Count question groups with optional filtering."""
        stmt = select(func.count(QuestionGroup.id))

        if type_id is not None:
            stmt = stmt.where(QuestionGroup.type_id == type_id)

        if is_active is not None:
            stmt = stmt.where(QuestionGroup.is_active == is_active)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update(
        self,
        question_group: QuestionGroup,
        data: QuestionGroupUpdate,
    ) -> QuestionGroup:
        """Update a question group."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(question_group, field, value)
        await self.session.flush()
        await self.session.refresh(question_group)
        return question_group

    async def get_by_ids(self, group_ids: list[UUID]) -> list[QuestionGroup]:
        """Get multiple question groups by IDs."""
        if not group_ids:
            return []
        result = await self.session.execute(
            select(QuestionGroup).where(QuestionGroup.id.in_(group_ids))
        )
        return list(result.scalars().all())

    async def get_active_by_type_id(self, type_id: UUID) -> list[QuestionGroup]:
        """Get all active question groups for a type, ordered by display_order."""
        result = await self.session.execute(
            select(QuestionGroup)
            .where(
                QuestionGroup.type_id == type_id,
                QuestionGroup.is_active == True,  # noqa: E712
            )
            .order_by(QuestionGroup.display_order)
        )
        return list(result.scalars().all())

    async def get_active_by_type_ids(self, type_ids: list[UUID]) -> list[QuestionGroup]:
        """Get all active question groups for multiple types."""
        if not type_ids:
            return []
        result = await self.session.execute(
            select(QuestionGroup)
            .where(
                QuestionGroup.type_id.in_(type_ids),
                QuestionGroup.is_active == True,  # noqa: E712
            )
            .order_by(QuestionGroup.type_id, QuestionGroup.display_order)
        )
        return list(result.scalars().all())
