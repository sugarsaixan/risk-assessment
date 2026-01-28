"""Respondent model for organizations or individuals taking assessments."""

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModelWithTimestamps
from src.models.enums import RespondentKind

if TYPE_CHECKING:
    from src.models.assessment import Assessment


class Respondent(BaseModelWithTimestamps):
    """Organization or individual taking an assessment.

    Attributes:
        kind: ORG for organization, PERSON for individual.
        name: Respondent name.
        registration_no: Organization registration or person ID number.
    """

    __tablename__ = "respondents"

    kind: Mapped[RespondentKind] = mapped_column(
        SAEnum(RespondentKind, name="respondent_kind"),
        nullable=False,
        index=True,
        comment="ORG or PERSON",
    )
    name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True,
        comment="Respondent name",
    )
    registration_no: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Org registration or person ID",
    )
    odoo_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
        comment="Unique respondent identifier from Odoo ERP",
    )

    # Relationships
    assessments: Mapped[list["Assessment"]] = relationship(
        "Assessment",
        back_populates="respondent",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Respondent(id={self.id}, kind={self.kind}, name={self.name!r})>"
