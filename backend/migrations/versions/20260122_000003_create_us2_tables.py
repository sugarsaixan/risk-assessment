"""Create US2 tables: answers, attachments, assessment_scores.

Revision ID: 20260122_000003
Revises: 20260122_000002
Create Date: 2026-01-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260122_000003"
down_revision: str | None = "20260122_000002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create User Story 2 tables."""
    # Create risk_rating enum
    risk_rating = postgresql.ENUM("LOW", "MEDIUM", "HIGH", name="risk_rating", create_type=False)
    risk_rating.create(op.get_bind(), checkfirst=True)

    # Create answers table
    op.create_table(
        "answers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("assessment_id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column(
            "selected_option",
            postgresql.ENUM("YES", "NO", name="option_type", create_type=False),
            nullable=False,
        ),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("score_awarded", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("assessment_id", "question_id", name="uq_answer_assessment_question"),
        sa.CheckConstraint("char_length(comment) <= 2000", name="ck_comment_max_length"),
        sa.CheckConstraint("score_awarded >= 0", name="ck_positive_score_awarded"),
    )
    op.create_index(op.f("ix_answers_assessment_id"), "answers", ["assessment_id"])

    # Create attachments table
    op.create_table(
        "attachments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("answer_id", sa.UUID(), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["answer_id"], ["answers.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_attachments_answer_id"), "attachments", ["answer_id"])
    op.create_index(op.f("ix_attachments_storage_key"), "attachments", ["storage_key"])

    # Create assessment_scores table
    op.create_table(
        "assessment_scores",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("assessment_id", sa.UUID(), nullable=False),
        sa.Column("type_id", sa.UUID(), nullable=True),
        sa.Column("raw_score", sa.Integer(), nullable=False),
        sa.Column("max_score", sa.Integer(), nullable=False),
        sa.Column("percentage", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column(
            "risk_rating",
            postgresql.ENUM("LOW", "MEDIUM", "HIGH", name="risk_rating", create_type=False),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("assessment_id", "type_id", name="uq_assessment_score_type"),
        sa.CheckConstraint("raw_score >= 0", name="ck_raw_score_positive"),
        sa.CheckConstraint("max_score >= 0", name="ck_max_score_positive"),
        sa.CheckConstraint("raw_score <= max_score", name="ck_raw_score_lte_max"),
        sa.CheckConstraint("percentage >= 0 AND percentage <= 100", name="ck_percentage_range"),
    )
    op.create_index(op.f("ix_assessment_scores_assessment_id"), "assessment_scores", ["assessment_id"])


def downgrade() -> None:
    """Drop User Story 2 tables."""
    op.drop_index(op.f("ix_assessment_scores_assessment_id"), table_name="assessment_scores")
    op.drop_table("assessment_scores")

    op.drop_index(op.f("ix_attachments_storage_key"), table_name="attachments")
    op.drop_index(op.f("ix_attachments_answer_id"), table_name="attachments")
    op.drop_table("attachments")

    op.drop_index(op.f("ix_answers_assessment_id"), table_name="answers")
    op.drop_table("answers")

    # Drop enum type
    op.execute("DROP TYPE IF EXISTS risk_rating")
