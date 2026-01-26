"""Add assessment_drafts table for server-side draft storage.

Revision ID: 20260124_drafts
Revises:
Create Date: 2026-01-24

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260124_drafts"
down_revision: Union[str, None] = "20260123_000004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create assessment_drafts table."""
    op.create_table(
        "assessment_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assessments.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("draft_data", postgresql.JSONB, nullable=False),
        sa.Column(
            "last_saved_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    # Index for fast lookup by assessment_id (already unique, but explicit)
    op.create_index(
        "idx_assessment_drafts_assessment_id",
        "assessment_drafts",
        ["assessment_id"],
    )


def downgrade() -> None:
    """Drop assessment_drafts table."""
    op.drop_index("idx_assessment_drafts_assessment_id", table_name="assessment_drafts")
    op.drop_table("assessment_drafts")
