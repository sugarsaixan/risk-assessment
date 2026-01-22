"""Repository for Question CRUD operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.question import Question
from src.schemas.question import QuestionCreate, QuestionUpdate


class QuestionRepository:
    """Repository for Question database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: QuestionCreate) -> Question:
        """Create a new question."""
        question = Question(**data.model_dump())
        self.session.add(question)
        await self.session.flush()
        await self.session.refresh(question)
        return question

    async def get_by_id(self, question_id: UUID) -> Question | None:
        """Get a question by ID."""
        result = await self.session.execute(
            select(Question).where(Question.id == question_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_options(self, question_id: UUID) -> Question | None:
        """Get a question by ID with options loaded."""
        result = await self.session.execute(
            select(Question)
            .where(Question.id == question_id)
            .options(selectinload(Question.options))
        )
        return result.scalar_one_or_none()

    async def get_by_type(
        self,
        type_id: UUID,
        *,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Question]:
        """Get questions for a questionnaire type."""
        stmt = (
            select(Question)
            .where(Question.type_id == type_id)
            .order_by(Question.display_order)
        )

        if is_active is not None:
            stmt = stmt.where(Question.is_active == is_active)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_type_with_options(
        self,
        type_id: UUID,
        *,
        is_active: bool | None = None,
    ) -> list[Question]:
        """Get questions for a type with options loaded."""
        stmt = (
            select(Question)
            .where(Question.type_id == type_id)
            .options(selectinload(Question.options))
            .order_by(Question.display_order)
        )

        if is_active is not None:
            stmt = stmt.where(Question.is_active == is_active)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_type(self, type_id: UUID, *, is_active: bool | None = None) -> int:
        """Count questions for a questionnaire type."""
        from sqlalchemy import func

        stmt = select(func.count(Question.id)).where(Question.type_id == type_id)

        if is_active is not None:
            stmt = stmt.where(Question.is_active == is_active)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update(self, question: Question, data: QuestionUpdate) -> Question:
        """Update a question."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(question, field, value)
        await self.session.flush()
        await self.session.refresh(question)
        return question

    async def get_next_display_order(self, type_id: UUID) -> int:
        """Get the next display order for a new question in a type."""
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.coalesce(func.max(Question.display_order), -1) + 1).where(
                Question.type_id == type_id
            )
        )
        return result.scalar_one()
