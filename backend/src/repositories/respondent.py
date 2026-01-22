"""Repository for Respondent CRUD operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.enums import RespondentKind
from src.models.respondent import Respondent
from src.schemas.respondent import RespondentCreate, RespondentUpdate


class RespondentRepository:
    """Repository for Respondent database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: RespondentCreate) -> Respondent:
        """Create a new respondent."""
        respondent = Respondent(**data.model_dump())
        self.session.add(respondent)
        await self.session.flush()
        await self.session.refresh(respondent)
        return respondent

    async def get_by_id(self, respondent_id: UUID) -> Respondent | None:
        """Get a respondent by ID."""
        result = await self.session.execute(
            select(Respondent).where(Respondent.id == respondent_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        kind: RespondentKind | None = None,
        name_search: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Respondent]:
        """Get all respondents with optional filtering."""
        stmt = select(Respondent).order_by(Respondent.name)

        if kind is not None:
            stmt = stmt.where(Respondent.kind == kind)

        if name_search:
            stmt = stmt.where(Respondent.name.ilike(f"%{name_search}%"))

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        *,
        kind: RespondentKind | None = None,
        name_search: str | None = None,
    ) -> int:
        """Count respondents with optional filtering."""
        from sqlalchemy import func

        stmt = select(func.count(Respondent.id))

        if kind is not None:
            stmt = stmt.where(Respondent.kind == kind)

        if name_search:
            stmt = stmt.where(Respondent.name.ilike(f"%{name_search}%"))

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update(self, respondent: Respondent, data: RespondentUpdate) -> Respondent:
        """Update a respondent."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(respondent, field, value)
        await self.session.flush()
        await self.session.refresh(respondent)
        return respondent

    async def search_by_name(self, name: str, limit: int = 10) -> list[Respondent]:
        """Search respondents by name (case-insensitive)."""
        result = await self.session.execute(
            select(Respondent)
            .where(Respondent.name.ilike(f"%{name}%"))
            .order_by(Respondent.name)
            .limit(limit)
        )
        return list(result.scalars().all())
