"""Add odoo_id to respondents and employee fields to assessments.

Revision ID: 20260128_odoo
Revises: 20260124_drafts
Create Date: 2026-01-28

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260128_odoo"
down_revision: Union[str, None] = "20260124_drafts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add odoo_id, employee_id, employee_name columns."""
    # 1. Add odoo_id to respondents (nullable String(100))
    op.add_column(
        "respondents",
        sa.Column("odoo_id", sa.String(100), nullable=True),
    )
    # Partial unique index: only enforce uniqueness where odoo_id IS NOT NULL
    op.create_index(
        "ix_respondents_odoo_id",
        "respondents",
        ["odoo_id"],
        unique=True,
        postgresql_where=sa.text("odoo_id IS NOT NULL"),
    )

    # 2. Add employee_id and employee_name to assessments
    op.add_column(
        "assessments",
        sa.Column("employee_id", sa.String(100), nullable=True),
    )
    op.add_column(
        "assessments",
        sa.Column("employee_name", sa.String(300), nullable=True),
    )
    op.create_index(
        "ix_assessments_employee_id",
        "assessments",
        ["employee_id"],
    )


def downgrade() -> None:
    """Remove odoo_id, employee_id, employee_name columns."""
    op.drop_index("ix_assessments_employee_id", table_name="assessments")
    op.drop_column("assessments", "employee_name")
    op.drop_column("assessments", "employee_id")
    op.drop_index("ix_respondents_odoo_id", table_name="respondents")
    op.drop_column("respondents", "odoo_id")
