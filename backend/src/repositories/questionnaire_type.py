"""Repository for QuestionnaireType CRUD operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.questionnaire_type import QuestionnaireType
from src.schemas.questionnaire_type import QuestionnaireTypeCreate, QuestionnaireTypeUpdate


class QuestionnaireTypeRepository:
    """Repository for QuestionnaireType database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: QuestionnaireTypeCreate) -> QuestionnaireType:
        """Create a new questionnaire type."""
        questionnaire_type = QuestionnaireType(**data.model_dump())
        self.session.add(questionnaire_type)
        await self.session.flush()
        await self.session.refresh(questionnaire_type)
        return questionnaire_type

    async def get_by_id(self, type_id: UUID) -> QuestionnaireType | None:
        """Get a questionnaire type by ID."""
        result = await self.session.execute(
            select(QuestionnaireType).where(QuestionnaireType.id == type_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[QuestionnaireType]:
        """Get all questionnaire types with optional filtering."""
        stmt = select(QuestionnaireType).order_by(QuestionnaireType.name)

        if is_active is not None:
            stmt = stmt.where(QuestionnaireType.is_active == is_active)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, *, is_active: bool | None = None) -> int:
        """Count questionnaire types with optional filtering."""
        from sqlalchemy import func

        stmt = select(func.count(QuestionnaireType.id))

        if is_active is not None:
            stmt = stmt.where(QuestionnaireType.is_active == is_active)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update(
        self,
        questionnaire_type: QuestionnaireType,
        data: QuestionnaireTypeUpdate,
    ) -> QuestionnaireType:
        """Update a questionnaire type."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(questionnaire_type, field, value)
        await self.session.flush()
        await self.session.refresh(questionnaire_type)
        return questionnaire_type

    async def get_by_ids(self, type_ids: list[UUID]) -> list[QuestionnaireType]:
        """Get multiple questionnaire types by IDs."""
        if not type_ids:
            return []
        result = await self.session.execute(
            select(QuestionnaireType).where(QuestionnaireType.id.in_(type_ids))
        )
        return list(result.scalars().all())

    async def get_active_by_ids(self, type_ids: list[UUID]) -> list[QuestionnaireType]:
        """Get multiple active questionnaire types by IDs."""
        if not type_ids:
            return []
        result = await self.session.execute(
            select(QuestionnaireType).where(
                QuestionnaireType.id.in_(type_ids),
                QuestionnaireType.is_active == True,  # noqa: E712
            )
        )
        return list(result.scalars().all())
