"""Add group_id column to assessment_scores for hierarchical scoring.

Revision ID: 20260123_000004
Revises: 20260123_000003
Create Date: 2026-01-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260123_000004"
down_revision: str | None = "20260123_000003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add group_id column and update unique constraint."""
    # Add group_id column
    op.add_column(
        "assessment_scores",
        sa.Column(
            "group_id",
            sa.UUID(),
            nullable=True,
            comment="Group ID or NULL for type/overall",
        ),
    )

    # Drop old unique constraint
    op.drop_constraint("uq_assessment_score_type", "assessment_scores", type_="unique")

    # Create new unique constraint including group_id
    op.create_unique_constraint(
        "uq_assessment_score_type_group",
        "assessment_scores",
        ["assessment_id", "type_id", "group_id"],
    )

    # Create index for group_id queries
    op.create_index(
        "ix_assessment_scores_group_id",
        "assessment_scores",
        ["group_id"],
    )


def downgrade() -> None:
    """Remove group_id column and restore old unique constraint."""
    # Drop index
    op.drop_index("ix_assessment_scores_group_id", table_name="assessment_scores")

    # Drop new unique constraint
    op.drop_constraint("uq_assessment_score_type_group", "assessment_scores", type_="unique")

    # Restore old unique constraint
    op.create_unique_constraint(
        "uq_assessment_score_type",
        "assessment_scores",
        ["assessment_id", "type_id"],
    )

    # Remove group_id column
    op.drop_column("assessment_scores", "group_id")
