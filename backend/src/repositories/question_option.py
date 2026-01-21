"""Repository for QuestionOption operations."""

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.question_option import QuestionOption
from src.schemas.question_option import QuestionOptionsSet


class QuestionOptionRepository:
    """Repository for QuestionOption database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_question(self, question_id: UUID) -> list[QuestionOption]:
        """Get all options for a question."""
        result = await self.session.execute(
            select(QuestionOption).where(QuestionOption.question_id == question_id)
        )
        return list(result.scalars().all())

    async def set_options(
        self,
        question_id: UUID,
        options: QuestionOptionsSet,
    ) -> list[QuestionOption]:
        """Set options for a question, replacing any existing options.

        This method deletes existing options and creates new ones.
        """
        # Delete existing options
        await self.session.execute(
            delete(QuestionOption).where(QuestionOption.question_id == question_id)
        )

        # Create YES option
        yes_option = QuestionOption(
            question_id=question_id,
            **options.yes.model_dump(),
        )
        self.session.add(yes_option)

        # Create NO option
        no_option = QuestionOption(
            question_id=question_id,
            **options.no.model_dump(),
        )
        self.session.add(no_option)

        await self.session.flush()
        await self.session.refresh(yes_option)
        await self.session.refresh(no_option)

        return [yes_option, no_option]

    async def delete_by_question(self, question_id: UUID) -> int:
        """Delete all options for a question. Returns count deleted."""
        result = await self.session.execute(
            delete(QuestionOption)
            .where(QuestionOption.question_id == question_id)
            .returning(QuestionOption.id)
        )
        return len(result.all())
