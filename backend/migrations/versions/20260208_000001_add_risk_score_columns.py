"""Add risk score calculation columns to assessment_scores.

Adds nullable columns for the new hierarchical risk grading system:
- classification_label: Group-level Mongolian classification
- probability_score: Type-level probability score
- consequence_score: Type-level consequence score
- risk_value: Type/Overall risk value (rounded integer)
- risk_grade: Type/Overall letter grade (AAA through D)
- risk_description: Type/Overall Mongolian description
- insurance_decision: Overall insurance decision

Revision ID: 20260208_000001
Revises: 20260128_odoo
Create Date: 2026-02-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260208_000001"
down_revision: str | None = "20260128_odoo"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add risk score calculation columns."""
    op.add_column(
        "assessment_scores",
        sa.Column(
            "classification_label",
            sa.String(20),
            nullable=True,
            comment="Group-level: Mongolian classification (Хэвийн, Хянахуйц, etc.)",
        ),
    )
    op.add_column(
        "assessment_scores",
        sa.Column(
            "probability_score",
            sa.Numeric(8, 4),
            nullable=True,
            comment="Type-level: AVERAGE + 0.618*STDEV of group sums",
        ),
    )
    op.add_column(
        "assessment_scores",
        sa.Column(
            "consequence_score",
            sa.Numeric(8, 4),
            nullable=True,
            comment="Type-level: AVERAGE + 0.618*STDEV of group numerics",
        ),
    )
    op.add_column(
        "assessment_scores",
        sa.Column(
            "risk_value",
            sa.Integer(),
            nullable=True,
            comment="Type/Overall: rounded risk product or aggregation",
        ),
    )
    op.add_column(
        "assessment_scores",
        sa.Column(
            "risk_grade",
            sa.String(3),
            nullable=True,
            comment="Type/Overall: letter grade AAA through D",
        ),
    )
    op.add_column(
        "assessment_scores",
        sa.Column(
            "risk_description",
            sa.String(100),
            nullable=True,
            comment="Type/Overall: Mongolian risk description",
        ),
    )
    op.add_column(
        "assessment_scores",
        sa.Column(
            "insurance_decision",
            sa.String(20),
            nullable=True,
            comment="Overall only: Даатгана or Даатгахгүй",
        ),
    )


def downgrade() -> None:
    """Remove risk score calculation columns."""
    op.drop_column("assessment_scores", "insurance_decision")
    op.drop_column("assessment_scores", "risk_description")
    op.drop_column("assessment_scores", "risk_grade")
    op.drop_column("assessment_scores", "risk_value")
    op.drop_column("assessment_scores", "consequence_score")
    op.drop_column("assessment_scores", "probability_score")
    op.drop_column("assessment_scores", "classification_label")
