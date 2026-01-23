"""Change questions.type_id to questions.group_id for hierarchical structure.

Revision ID: 20260123_000002
Revises: 20260123_000001
Create Date: 2026-01-23

This migration:
1. Adds group_id column to questions table
2. Creates a default group for each type (for existing questions)
3. Migrates existing questions from type_id to group_id
4. Removes type_id column from questions table
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260123_000002"
down_revision: str | None = "20260123_000001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Migrate questions from type_id to group_id."""
    # Step 1: Add group_id column (nullable initially)
    op.add_column(
        "questions",
        sa.Column("group_id", sa.UUID(), nullable=True),
    )

    # Step 2: Create default groups for each type that has questions
    # and update questions to reference those groups
    op.execute("""
        -- Create a default group for each type that has questions
        INSERT INTO question_groups (id, type_id, name, display_order, weight, is_active, created_at, updated_at)
        SELECT
            gen_random_uuid(),
            qt.id,
            'Ерөнхий' || ' - ' || qt.name,
            0,
            1.0,
            true,
            now(),
            now()
        FROM questionnaire_types qt
        WHERE EXISTS (SELECT 1 FROM questions q WHERE q.type_id = qt.id)
        AND NOT EXISTS (SELECT 1 FROM question_groups qg WHERE qg.type_id = qt.id);
    """)

    # Step 3: Update questions to reference their type's default group
    op.execute("""
        UPDATE questions q
        SET group_id = (
            SELECT qg.id
            FROM question_groups qg
            WHERE qg.type_id = q.type_id
            ORDER BY qg.display_order
            LIMIT 1
        )
        WHERE q.group_id IS NULL;
    """)

    # Step 4: Make group_id NOT NULL and add foreign key
    op.alter_column("questions", "group_id", nullable=False)
    op.create_foreign_key(
        "fk_questions_group_id",
        "questions",
        "question_groups",
        ["group_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Step 5: Create index for group_id
    op.create_index(op.f("ix_questions_group_id"), "questions", ["group_id"])

    # Step 6: Drop old type_id column and its constraints
    op.drop_index(op.f("ix_questions_type_id"), table_name="questions")
    op.drop_constraint("questions_type_id_fkey", "questions", type_="foreignkey")
    op.drop_column("questions", "type_id")


def downgrade() -> None:
    """Revert questions from group_id back to type_id."""
    # Step 1: Add type_id column back (nullable initially)
    op.add_column(
        "questions",
        sa.Column("type_id", sa.UUID(), nullable=True),
    )

    # Step 2: Populate type_id from group's type_id
    op.execute("""
        UPDATE questions q
        SET type_id = (
            SELECT qg.type_id
            FROM question_groups qg
            WHERE qg.id = q.group_id
        );
    """)

    # Step 3: Make type_id NOT NULL and add foreign key
    op.alter_column("questions", "type_id", nullable=False)
    op.create_foreign_key(
        "questions_type_id_fkey",
        "questions",
        "questionnaire_types",
        ["type_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(op.f("ix_questions_type_id"), "questions", ["type_id"])

    # Step 4: Drop group_id column
    op.drop_index(op.f("ix_questions_group_id"), table_name="questions")
    op.drop_constraint("fk_questions_group_id", "questions", type_="foreignkey")
    op.drop_column("questions", "group_id")
