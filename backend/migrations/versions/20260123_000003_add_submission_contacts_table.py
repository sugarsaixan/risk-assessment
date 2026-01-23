"""Add submission_contacts table for storing who filled out assessments.

Revision ID: 20260123_000003
Revises: 20260123_000002
Create Date: 2026-01-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260123_000003"
down_revision: str | None = "20260123_000002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create submission_contacts table."""
    op.create_table(
        "submission_contacts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("assessment_id", sa.UUID(), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False, comment="Овог (Family name)"),
        sa.Column("first_name", sa.String(length=100), nullable=False, comment="Нэр (Given name)"),
        sa.Column("email", sa.String(length=255), nullable=False, comment="Email address"),
        sa.Column("phone", sa.String(length=50), nullable=False, comment="Phone number"),
        sa.Column("position", sa.String(length=200), nullable=False, comment="Албан тушаал (Job position)"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["assessment_id"], ["assessments.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("assessment_id", name="uq_submission_contacts_assessment_id"),
    )
    op.create_index(
        op.f("ix_submission_contacts_assessment_id"),
        "submission_contacts",
        ["assessment_id"],
    )


def downgrade() -> None:
    """Drop submission_contacts table."""
    op.drop_index(op.f("ix_submission_contacts_assessment_id"), table_name="submission_contacts")
    op.drop_table("submission_contacts")
