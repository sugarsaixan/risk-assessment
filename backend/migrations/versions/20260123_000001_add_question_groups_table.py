"""Add question_groups table for hierarchical question organization.

Revision ID: 20260123_000001
Revises: 20260122_000003
Create Date: 2026-01-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260123_000001"
down_revision: str | None = "20260122_000003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create question_groups table."""
    op.create_table(
        "question_groups",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("type_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("weight", sa.Numeric(precision=5, scale=2), nullable=False, server_default="1.0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
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
            ["type_id"], ["questionnaire_types.id"], ondelete="CASCADE"
        ),
        sa.CheckConstraint("display_order >= 0", name="ck_group_display_order_non_negative"),
        sa.CheckConstraint("weight > 0", name="ck_group_positive_weight"),
    )
    op.create_index(op.f("ix_question_groups_type_id"), "question_groups", ["type_id"])
    op.create_index(op.f("ix_question_groups_is_active"), "question_groups", ["is_active"])
    op.create_index(
        "ix_question_groups_type_display_order",
        "question_groups",
        ["type_id", "display_order"],
    )


def downgrade() -> None:
    """Drop question_groups table."""
    op.drop_index("ix_question_groups_type_display_order", table_name="question_groups")
    op.drop_index(op.f("ix_question_groups_is_active"), table_name="question_groups")
    op.drop_index(op.f("ix_question_groups_type_id"), table_name="question_groups")
    op.drop_table("question_groups")
