"""Create US1 tables: questionnaire_types, questions, question_options, respondents, assessments.

Revision ID: 20260122_000002
Revises: 20260122_000001
Create Date: 2026-01-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260122_000002"
down_revision: str | None = "20260122_000001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create User Story 1 tables."""
    # Create enum types
    scoring_method = postgresql.ENUM("SUM", name="scoring_method", create_type=False)
    scoring_method.create(op.get_bind(), checkfirst=True)

    respondent_kind = postgresql.ENUM("ORG", "PERSON", name="respondent_kind", create_type=False)
    respondent_kind.create(op.get_bind(), checkfirst=True)

    option_type = postgresql.ENUM("YES", "NO", name="option_type", create_type=False)
    option_type.create(op.get_bind(), checkfirst=True)

    assessment_status = postgresql.ENUM(
        "PENDING", "COMPLETED", "EXPIRED", name="assessment_status", create_type=False
    )
    assessment_status.create(op.get_bind(), checkfirst=True)

    # Create questionnaire_types table
    op.create_table(
        "questionnaire_types",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column(
            "scoring_method",
            postgresql.ENUM("SUM", name="scoring_method", create_type=False),
            nullable=False,
            server_default="SUM",
        ),
        sa.Column("threshold_high", sa.Integer(), nullable=False, server_default="80"),
        sa.Column("threshold_medium", sa.Integer(), nullable=False, server_default="50"),
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
        sa.CheckConstraint("threshold_high > threshold_medium", name="ck_threshold_order"),
        sa.CheckConstraint("weight > 0", name="ck_positive_weight"),
    )
    op.create_index(op.f("ix_questionnaire_types_is_active"), "questionnaire_types", ["is_active"])

    # Create questions table
    op.create_table(
        "questions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("type_id", sa.UUID(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("weight", sa.Numeric(precision=5, scale=2), nullable=False, server_default="1.0"),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["type_id"], ["questionnaire_types.id"], ondelete="CASCADE"
        ),
        sa.CheckConstraint("display_order >= 0", name="ck_positive_display_order"),
        sa.CheckConstraint("char_length(text) <= 2000", name="ck_text_max_length"),
    )
    op.create_index(op.f("ix_questions_type_id"), "questions", ["type_id"])
    op.create_index(op.f("ix_questions_is_active"), "questions", ["is_active"])

    # Create question_options table
    op.create_table(
        "question_options",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column(
            "option_type",
            postgresql.ENUM("YES", "NO", name="option_type", create_type=False),
            nullable=False,
        ),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("require_comment", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("require_image", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("comment_min_len", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_images", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("image_max_mb", sa.Integer(), nullable=False, server_default="5"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("question_id", "option_type", name="uq_question_option_type"),
        sa.CheckConstraint("score >= 0", name="ck_positive_score"),
        sa.CheckConstraint(
            "comment_min_len >= 0 AND comment_min_len <= 2000", name="ck_comment_min_len_range"
        ),
        sa.CheckConstraint("max_images >= 1 AND max_images <= 10", name="ck_max_images_range"),
        sa.CheckConstraint("image_max_mb >= 1 AND image_max_mb <= 20", name="ck_image_max_mb_range"),
    )
    op.create_index(op.f("ix_question_options_question_id"), "question_options", ["question_id"])

    # Create respondents table
    op.create_table(
        "respondents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "kind",
            postgresql.ENUM("ORG", "PERSON", name="respondent_kind", create_type=False),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("registration_no", sa.String(length=50), nullable=True),
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
    )
    op.create_index(op.f("ix_respondents_kind"), "respondents", ["kind"])
    op.create_index(op.f("ix_respondents_name"), "respondents", ["name"])

    # Create assessments table
    op.create_table(
        "assessments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("respondent_id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("selected_type_ids", postgresql.ARRAY(sa.UUID()), nullable=False),
        sa.Column("questions_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM("PENDING", "COMPLETED", "EXPIRED", name="assessment_status", create_type=False),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["respondent_id"], ["respondents.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(op.f("ix_assessments_respondent_id"), "assessments", ["respondent_id"])
    op.create_index(op.f("ix_assessments_token_hash"), "assessments", ["token_hash"], unique=True)
    op.create_index(op.f("ix_assessments_status"), "assessments", ["status"])
    op.create_index(op.f("ix_assessments_expires_at"), "assessments", ["expires_at"])


def downgrade() -> None:
    """Drop User Story 1 tables."""
    op.drop_index(op.f("ix_assessments_expires_at"), table_name="assessments")
    op.drop_index(op.f("ix_assessments_status"), table_name="assessments")
    op.drop_index(op.f("ix_assessments_token_hash"), table_name="assessments")
    op.drop_index(op.f("ix_assessments_respondent_id"), table_name="assessments")
    op.drop_table("assessments")

    op.drop_index(op.f("ix_respondents_name"), table_name="respondents")
    op.drop_index(op.f("ix_respondents_kind"), table_name="respondents")
    op.drop_table("respondents")

    op.drop_index(op.f("ix_question_options_question_id"), table_name="question_options")
    op.drop_table("question_options")

    op.drop_index(op.f("ix_questions_is_active"), table_name="questions")
    op.drop_index(op.f("ix_questions_type_id"), table_name="questions")
    op.drop_table("questions")

    op.drop_index(op.f("ix_questionnaire_types_is_active"), table_name="questionnaire_types")
    op.drop_table("questionnaire_types")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS assessment_status")
    op.execute("DROP TYPE IF EXISTS option_type")
    op.execute("DROP TYPE IF EXISTS respondent_kind")
    op.execute("DROP TYPE IF EXISTS scoring_method")
