"""Repository for Respondent database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.enums import RespondentKind
from src.models.respondent import Respondent


class RespondentRepository:
    """Repository for Respondent database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, respondent_id: UUID) -> Respondent | None:
        """Get a respondent by ID."""
        result = await self.session.execute(
            select(Respondent).where(Respondent.id == respondent_id)
        )
        return result.scalar_one_or_none()

    async def get_by_odoo_id(self, odoo_id: str) -> Respondent | None:
        """Get a respondent by Odoo ID."""
        result = await self.session.execute(
            select(Respondent).where(Respondent.odoo_id == odoo_id)
        )
        return result.scalar_one_or_none()

    async def find_by_kind_and_registration(
        self, kind: RespondentKind, registration_no: str
    ) -> Respondent | None:
        """Find a respondent by kind + registration_no (legacy linking)."""
        result = await self.session.execute(
            select(Respondent).where(
                Respondent.kind == kind,
                Respondent.registration_no == registration_no,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_from_odoo(
        self,
        *,
        odoo_id: str,
        name: str,
        kind: RespondentKind,
        registration_no: str | None,
    ) -> Respondent:
        """Create or update a respondent from Odoo data.

        Strategy:
        1. Try INSERT ON CONFLICT on odoo_id → update name/registration_no.
        2. If no conflict (new odoo_id), check for legacy match by kind+registration_no
           to link an existing respondent.
        3. If still no match, create new.

        Returns the resolved Respondent instance.
        """
        # First, try to find by odoo_id
        existing = await self.get_by_odoo_id(odoo_id)
        if existing is not None:
            # Update name and registration_no to latest Odoo data
            existing.name = name
            existing.registration_no = registration_no
            await self.session.flush()
            await self.session.refresh(existing)
            return existing

        # Try legacy linking: match by kind + registration_no
        if registration_no is not None:
            legacy = await self.find_by_kind_and_registration(kind, registration_no)
            if legacy is not None:
                # Link this legacy respondent to the Odoo ID
                legacy.odoo_id = odoo_id
                legacy.name = name
                legacy.registration_no = registration_no
                await self.session.flush()
                await self.session.refresh(legacy)
                return legacy

        # No match found — use INSERT ON CONFLICT for atomicity
        stmt = pg_insert(Respondent).values(
            odoo_id=odoo_id,
            name=name,
            kind=kind,
            registration_no=registration_no,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["odoo_id"],
            set_={
                "name": stmt.excluded.name,
                "registration_no": stmt.excluded.registration_no,
            },
        ).returning(Respondent)

        result = await self.session.execute(stmt)
        respondent = result.scalar_one()
        await self.session.refresh(respondent)
        return respondent

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

    async def search_by_name(self, name: str, limit: int = 10) -> list[Respondent]:
        """Search respondents by name (case-insensitive)."""
        result = await self.session.execute(
            select(Respondent)
            .where(Respondent.name.ilike(f"%{name}%"))
            .order_by(Respondent.name)
            .limit(limit)
        )
        return list(result.scalars().all())
