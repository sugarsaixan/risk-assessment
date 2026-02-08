"""fix_odoo_id_unique_constraint

Revision ID: 95973ab8748f
Revises: 20260128_odoo
Create Date: 2026-02-03 10:42:19.135615
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '95973ab8748f'
down_revision: str | None = '20260128_odoo'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply migration: replace unique index with unique constraint."""
    # Drop the partial unique index
    op.drop_index(
        "ix_respondents_odoo_id",
        table_name="respondents",
        postgresql_where=sa.text("odoo_id IS NOT NULL"),
    )

    # Add a proper unique constraint (excluding NULL values)
    # PostgreSQL unique constraints exclude NULL values automatically
    op.create_unique_constraint(
        "uq_respondents_odoo_id",
        "respondents",
        ["odoo_id"],
    )


def downgrade() -> None:
    """Revert migration: restore partial unique index."""
    # Drop the unique constraint
    op.drop_constraint(
        "uq_respondents_odoo_id",
        "respondents",
        type_="unique",
    )

    # Recreate the partial unique index
    op.create_index(
        "ix_respondents_odoo_id",
        "respondents",
        ["odoo_id"],
        unique=True,
        postgresql_where=sa.text("odoo_id IS NOT NULL"),
    )
